"""
api_client.py
-------------
Reusable HTTP client for the China Tourism Recommendation FastAPI backend.
All API calls go through this module — no raw requests calls elsewhere.

Backend base URL is read from the TOURISM_API_URL environment variable,
defaulting to http://127.0.0.1:8000.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_BASE_URL: str = os.environ.get("TOURISM_API_URL", "http://127.0.0.1:8000").rstrip("/")
_TIMEOUT: int = 10  # seconds


def _url(path: str) -> str:
    return f"{_BASE_URL}{path}"


def _safe_get(path: str) -> tuple[Optional[dict], Optional[str]]:
    """GET helper. Returns (data_dict, error_message)."""
    try:
        resp = requests.get(_url(path), timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.ConnectionError:
        msg = (
            f"Cannot connect to the backend at {_BASE_URL}. "
            "Make sure the FastAPI server is running (see README for commands)."
        )
        logger.error(msg)
        return None, msg
    except requests.exceptions.Timeout:
        msg = f"Request to {path} timed out after {_TIMEOUT}s."
        logger.error(msg)
        return None, msg
    except requests.exceptions.HTTPError as exc:
        msg = f"Backend returned HTTP {exc.response.status_code} for {path}."
        logger.error(msg)
        return None, msg
    except Exception as exc:  # pylint: disable=broad-except
        msg = f"Unexpected error calling {path}: {type(exc).__name__}: {exc}"
        logger.error(msg)
        return None, msg


def get_health() -> tuple[Optional[dict], Optional[str]]:
    """
    Call GET /health.
    Returns (health_dict, error_message).
    health_dict keys: status, model, catalogue_entries, classes
    """
    return _safe_get("/health")


def get_options() -> tuple[Optional[dict], Optional[str]]:
    """
    Call GET /options.
    Returns (options_dict, error_message).
    options_dict keys: provinces, cities, categories, seasons,
                       holiday_options, age_groups, source_provinces,
                       attraction_levels, recommendation_classes
    """
    data, err = _safe_get("/options")
    if data is None:
        return None, err

    # Derive cities_by_province from the flat cities list isn't possible
    # without province mapping — we build it from the catalogue via the
    # existing options.  The backend exposes a flat 'cities' list.
    # We attach an empty mapping; the UI will request this separately
    # if needed (it already has the province→city mapping from the
    # backend's options response structure).
    return data, None


def get_cities_by_province() -> dict[str, list[str]]:
    """
    Build a province → [city, …] mapping by calling /options and
    supplementing with the catalogue.  Returns an empty dict on failure.

    Because the backend only exposes a flat cities list, we build this
    mapping client-side from the catalogue CSV that ships alongside the
    backend.  This is purely for UI convenience; the API call always
    sends the raw province/city string values.
    """
    try:
        import pandas as pd
        from pathlib import Path

        catalogue_path = (
            Path(__file__).parent / "backend" / "tourism_attraction_catalogue.csv"
        )
        if not catalogue_path.exists():
            return {}
        cat = pd.read_csv(catalogue_path)
        mapping: dict[str, list[str]] = (
            cat.groupby("province")["city"]
            .apply(lambda s: sorted(s.dropna().unique().tolist()))
            .to_dict()
        )
        return mapping
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Could not build cities_by_province: %s", exc)
        return {}


def get_recommendations(payload: dict) -> tuple[Optional[dict], Optional[str]]:
    """
    Call POST /recommendations.
    payload should be a dict matching the RecommendationRequest schema.
    Returns (response_dict, error_message).
    response_dict keys: count, ranking_method, recommendations, note
    """
    try:
        resp = requests.post(
            _url("/recommendations"),
            json=payload,
            timeout=_TIMEOUT,
        )
        if resp.status_code == 422:
            # Validation error — extract detail
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            if isinstance(detail, dict):
                error_msg = detail.get("error", str(detail))
                allowed = detail.get("allowed_values")
                if allowed:
                    error_msg += f"\nAllowed values: {allowed}"
            elif isinstance(detail, list):
                error_msg = "; ".join(
                    d.get("msg", str(d)) if isinstance(d, dict) else str(d)
                    for d in detail
                )
            else:
                error_msg = str(detail)
            return None, f"Invalid request: {error_msg}"

        resp.raise_for_status()
        return resp.json(), None

    except requests.exceptions.ConnectionError:
        msg = (
            f"Cannot connect to the backend at {_BASE_URL}. "
            "Make sure the FastAPI server is running."
        )
        logger.error(msg)
        return None, msg
    except requests.exceptions.Timeout:
        msg = f"Recommendation request timed out after {_TIMEOUT}s."
        logger.error(msg)
        return None, msg
    except requests.exceptions.HTTPError as exc:
        msg = f"Backend error: HTTP {exc.response.status_code}."
        try:
            body = exc.response.json()
            detail = body.get("detail", "")
            if detail:
                msg += f" Detail: {detail}"
        except Exception:
            pass
        logger.error(msg)
        return None, msg
    except Exception as exc:  # pylint: disable=broad-except
        msg = f"Unexpected error: {type(exc).__name__}: {exc}"
        logger.error(msg)
        return None, msg

