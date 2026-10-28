# -*- coding: utf-8 -*-
"""
app.py
------
China Tourism Recommendation & Travel Planning System
Clean Material Symbols design system with streamlined state and qualitative scoring.
"""

from __future__ import annotations

import html
from typing import Optional

import pandas as pd
import streamlit as st

import api_client

# ──────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIGURATION & THEME
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="China Tourism Explorer",
    page_icon=":material/travel_explore:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ──────────────────────────────────────────────────────────────────────────────
# 2. DESIGN SYSTEM & CSS INJECTION
# ──────────────────────────────────────────────────────────────────────────────
def inject_css() -> None:
    """Inject typography, Material Symbols Rounded, and custom component styles."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

        /* Global typography & variables */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 16px;
            color: #0F172A;
            background-color: #F8FAFC;
        }

        /* Material Symbols Inline Helper Class */
        .msi {
            font-family: 'Material Symbols Rounded';
            font-weight: normal;
            font-style: normal;
            font-size: 1.1em;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            vertical-align: middle;
            font-feature-settings: 'liga';
            -webkit-font-smoothing: antialiased;
        }

        /* Compact Header Banner */
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.25rem 1.75rem;
            background: linear-gradient(135deg, #0F766E 0%, #115E59 100%);
            border-radius: 12px;
            color: #FFFFFF;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(15, 118, 110, 0.12);
        }
        .app-header-left h1 {
            font-size: 1.65rem;
            font-weight: 800;
            margin: 0;
            color: #FFFFFF !important;
            letter-spacing: -0.4px;
        }
        .app-header-left p {
            font-size: 0.95rem;
            color: #CCFBF1 !important;
            margin: 0.25rem 0 0 0;
            font-weight: 400;
        }

        /* Status Dot in Header */
        .api-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.15);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #FFFFFF;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-online { background-color: #34D399; box-shadow: 0 0 8px #34D399; }
        .dot-offline { background-color: #F87171; box-shadow: 0 0 8px #F87171; }

        /* Result Summary Bar */
        .summary-bar {
            background: #F1F5F9;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 0.75rem 1.25rem;
            margin-bottom: 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.95rem;
            color: #334155;
            font-weight: 500;
        }

        /* Card Elements */
        .card-header-row {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.4rem;
        }
        .card-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin: 0;
            line-height: 1.3;
        }
        .card-rank-badge {
            font-size: 0.8rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
            background: #F1F5F9;
            color: #475569;
            border: 1px solid #CBD5E1;
        }
        .card-location {
            font-size: 0.9rem;
            color: #64748B;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Chips: Text Only, Zero Icons */
        .chips-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 0.85rem;
        }
        .chip {
            font-size: 0.8rem;
            font-weight: 600;
            padding: 3px 9px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
        }
        .chip-level { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .chip-category { background: #F1F5F9; color: #334155; border: 1px solid #E2E8F0; }
        .chip-price-free { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; font-weight: 700; }
        .chip-price-paid { background: #F8FAFC; color: #0F172A; border: 1px solid #E2E8F0; font-weight: 600; }
        .chip-match-high { background: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
        .chip-match-med { background: #E0F2FE; color: #075985; border: 1px solid #BAE6FD; }
        .chip-match-low { background: #FEF9C3; color: #854D0E; border: 1px solid #FDE047; }

        /* Step Cards for How It Works */
        .step-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 1.5rem;
            height: 100%;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        }
        .step-num {
            font-size: 0.85rem;
            font-weight: 800;
            color: #0F766E;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        .step-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.5rem;
        }
        .step-desc {
            font-size: 0.92rem;
            color: #475569;
            line-height: 1.5;
        }

        /* Metric Tile */
        .metric-tile {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1rem;
            text-align: center;
        }
        .metric-val {
            font-size: 1.75rem;
            font-weight: 800;
            color: #0F766E;
        }
        .metric-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }

        /* Empty State */
        .empty-box {
            background: #FFFFFF;
            border: 2px dashed #CBD5E1;
            border-radius: 12px;
            padding: 3rem 2rem;
            text-align: center;
            color: #64748B;
            margin: 1.5rem 0;
        }
        .empty-icon {
            margin-bottom: 0.75rem;
        }
        .empty-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.4rem;
        }
        .empty-desc {
            font-size: 0.95rem;
            color: #64748B;
            max-width: 480px;
            margin: 0 auto 1.5rem auto;
            line-height: 1.5;
        }

        /* Dropdown Pure Pointer Styling: Suppress text cursor, typing caret & text selection */
        div[data-testid="stSelectbox"] input,
        .react-aria-ComboBox input {
            caret-color: transparent !important;
            cursor: pointer !important;
            user-select: none !important;
            -webkit-user-select: none !important;
        }
        div[data-testid="stSelectbox"],
        div[data-testid="stSelectbox"] *,
        .react-aria-ComboBox,
        .react-aria-ComboBox * {
            cursor: pointer !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def mi(name: str, size: str = "18px", color: str = "") -> str:
    """Helper to render Material Symbols Rounded icons inside raw HTML."""
    style = f"font-size:{size};"
    if color:
        style += f"color:{color};"
    return f'<span class="msi" style="{style}">{name}</span>'


# ──────────────────────────────────────────────────────────────────────────────
# 3. STATE INITIALISATION & PERSISTENCE
# ──────────────────────────────────────────────────────────────────────────────
def init_state() -> None:
    """Ensure persistent session state keys across all interactions."""
    defaults = {
        "trip_plan": [],
        "last_results": None,
        "options": None,
        "health": None,
        "api_error": None,
        "cities_by_province": {},
        # Direct filter widget keys
        "f_province": "(All Provinces)",
        "f_city": "(All Cities)",
        "f_category": "(All Categories)",
        "f_use_budget": False,
        "f_budget": 400,
        "f_season": "Autumn",
        "f_holiday": "(Any / Unspecified)",
        "f_age_group": "(Any / Unspecified)",
        "f_source_prov": "(Any / Unspecified)",
        "f_rank_class_label": "Top picks",
        "f_top_n": 10,
        "pending_search": False,
        "view_mode": "Cards",
        "sort_mode": "Best match",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Re-assign every f_* key so widget state survives when a widget is not rendered
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith("f_"):
            st.session_state[k] = st.session_state[k]


init_state()

# ──────────────────────────────────────────────────────────────────────────────
# 4. PLAIN LANGUAGE DICTIONARIES & HELPERS
# ──────────────────────────────────────────────────────────────────────────────
LABEL_TO_CLASS = {
    "Top picks": "Highly Recommend",
    "Good match": "Recommend",
    "Worth a look": "Neutral",
}
CLASS_TO_LABEL = {v: k for k, v in LABEL_TO_CLASS.items()}


def trip_key(item: dict) -> tuple[str, str, str]:
    return (
        str(item.get("attraction_name", "")),
        str(item.get("city", "")),
        str(item.get("province", "")),
    )


def is_saved(item: dict) -> bool:
    key = trip_key(item)
    return any(trip_key(p) == key for p in st.session_state.trip_plan)


def add_to_plan(item: dict) -> None:
    if not is_saved(item):
        st.session_state.trip_plan.append(item)
        st.toast(
            f"Added {item.get('attraction_name', 'Attraction')} to your trip plan.",
            icon=":material/bookmark_add:",
        )


def remove_from_plan(key: tuple) -> None:
    item_name = key[0]
    st.session_state.trip_plan = [
        p for p in st.session_state.trip_plan if trip_key(p) != key
    ]
    st.toast(f"Removed {item_name} from your trip plan.", icon=":material/delete:")


def clear_plan_callback() -> None:
    """Clear all saved attractions in trip plan."""
    st.session_state.trip_plan = []
    st.toast("Trip plan cleared.", icon=":material/delete_sweep:")


def format_price(price: Optional[float]) -> tuple[str, bool]:
    """Return formatted label and a boolean indicating if it is free."""
    if price is None:
        return "Price not listed", False
    try:
        val = float(price)
        if val == 0:
            return "Free", True
        return f"¥{val:.0f}", False
    except (TypeError, ValueError):
        return str(price), False


def score_to_strength(
    score: Optional[float],
    q_low: float,
    q_high: float,
    rank: int,
    total: int,
) -> tuple[float, str]:
    """Calculate qualitative match strength from result-set terciles and rank-based fill."""
    if total <= 1:
        fill = 0.95
    else:
        fill = 0.95 - ((rank - 1) / (total - 1)) * 0.80
        fill = max(0.10, min(0.95, fill))

    if score is None:
        return fill, "Medium"
    try:
        s = float(score)
        if s >= q_high:
            label = "Strong"
        elif s >= q_low:
            label = "Medium"
        else:
            label = "Light"
        return fill, label
    except Exception:
        return fill, "Medium"


def format_season(val: str) -> str:
    """Map raw backend season token 'Chun Ji' (Spring in Pinyin) to clear user-facing label."""
    if val == "Chun Ji":
        return "Spring (Chun Ji)"
    return val


# ──────────────────────────────────────────────────────────────────────────────
# 5. DATA LOADING & BACKEND REFRESH
# ──────────────────────────────────────────────────────────────────────────────
def load_backend_data(force: bool = False) -> None:
    if force or st.session_state.health is None:
        h, err = api_client.get_health()
        st.session_state.health = h
        st.session_state.api_error = err

    if (force or st.session_state.options is None) and st.session_state.health:
        opts, err = api_client.get_options()
        st.session_state.options = opts
        if err:
            st.session_state.api_error = err

    if not st.session_state.cities_by_province:
        st.session_state.cities_by_province = api_client.get_cities_by_province()


load_backend_data()

backend_online = st.session_state.health is not None
options = st.session_state.options or {}


# ──────────────────────────────────────────────────────────────────────────────
# 6. COMPONENT: HEADER
# ──────────────────────────────────────────────────────────────────────────────
def render_header() -> None:
    """Render compact, high-contrast hero header with embedded status dot."""
    if backend_online:
        h = st.session_state.health or {}
        model_name = h.get("model", "Balanced Linear SVM")
        dot_html = '<span class="status-dot dot-online"></span> API Connected'
        tooltip_text = f"Connected to FastAPI ({model_name} · 433 entries)"
    else:
        dot_html = '<span class="status-dot dot-offline"></span> API Offline'
        tooltip_text = "FastAPI server unreachable at http://127.0.0.1:8000"

    st.markdown(
        f"""
        <div class="app-header">
            <div class="app-header-left">
                <h1>China Tourism Recommendation System</h1>
                <p>Intelligent attraction explorer and travel planning powered by Balanced Linear SVM.</p>
            </div>
            <div>
                <span class="api-pill" title="{tooltip_text}">
                    {dot_html}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 7. COMPONENT: SEARCH BAR & FILTERS (CONTAINER BORDER & DIRECT KEYS)
# ──────────────────────────────────────────────────────────────────────────────
def on_province_change() -> None:
    """Reset city when province changes."""
    st.session_state.f_city = "(All Cities)"


def reset_filters_callback() -> None:
    """Reset all filter keys to initial defaults."""
    st.session_state.f_province = "(All Provinces)"
    st.session_state.f_city = "(All Cities)"
    st.session_state.f_category = "(All Categories)"
    st.session_state.f_use_budget = False
    st.session_state.f_budget = 400
    st.session_state.f_season = "Autumn"
    st.session_state.f_holiday = "(Any / Unspecified)"
    st.session_state.f_age_group = "(Any / Unspecified)"
    st.session_state.f_source_prov = "(Any / Unspecified)"
    st.session_state.f_rank_class_label = "Top picks"
    st.session_state.f_top_n = 10
    st.session_state.last_results = None


def apply_preset_callback(province: str, category: str) -> None:
    """Set preset destination filters and queue an automatic search."""
    opts = st.session_state.options or {}
    prov_opts = opts.get("provinces", [])
    cat_opts = opts.get("categories", [])

    st.session_state.f_province = province if province in prov_opts else "(All Provinces)"
    st.session_state.f_city = "(All Cities)"
    st.session_state.f_category = category if category in cat_opts else "(All Categories)"
    st.session_state.pending_search = True


def render_filters(provinces: list[str], cities: list[str], categories: list[str], cities_by_prov: dict) -> None:
    """Render horizontal search controls directly bound to f_* session_state keys."""
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.4, 1.2])

        with c1:
            prov_list = ["(All Provinces)"] + provinces
            st.selectbox(
                "Destination Province",
                prov_list,
                key="f_province",
                on_change=on_province_change,
                filter_mode=None,
            )

        with c2:
            sel_prov = st.session_state.f_province
            if sel_prov != "(All Provinces)" and cities_by_prov.get(sel_prov):
                city_choices = ["(All Cities)"] + cities_by_prov[sel_prov]
            else:
                city_choices = ["(All Cities)"] + cities

            # Ensure current f_city is valid inside dynamic choices
            if st.session_state.f_city not in city_choices:
                st.session_state.f_city = "(All Cities)"

            st.selectbox(
                "City (Optional)",
                city_choices,
                key="f_city",
                filter_mode=None,
            )

        with c3:
            cat_list = ["(All Categories)"] + categories
            st.selectbox(
                "Attraction Category",
                cat_list,
                key="f_category",
                filter_mode=None,
            )

        with c4:
            st.checkbox("Cap ticket price", key="f_use_budget")
            if st.session_state.f_use_budget:
                st.slider("Max Ticket Price (¥)", 0, 400, step=10, key="f_budget")
            else:
                st.caption("No price cap applied (Free–¥400)")

        with st.expander("Personalise my results (optional)", icon=":material/tune:", expanded=False):
            p1, p2, p3, p4 = st.columns(4)
            seasons = options.get("seasons", ["Autumn", "Summer", "Winter", "Chun Ji"])
            holiday_opts = options.get("holiday_options", ["No", "Yes"])
            age_groups = options.get("age_groups", ["18-25", "26-35", "36-45", "46-55", "56+"])
            source_provinces = options.get("source_provinces", [])

            with p1:
                st.selectbox(
                    "Travel Season",
                    seasons,
                    key="f_season",
                    format_func=format_season,
                    filter_mode=None,
                )
            with p2:
                st.selectbox(
                    "Travelling during a holiday?",
                    ["(Any / Unspecified)"] + holiday_opts,
                    key="f_holiday",
                    filter_mode=None,
                )
            with p3:
                st.selectbox(
                    "Your age group",
                    ["(Any / Unspecified)"] + age_groups,
                    key="f_age_group",
                    filter_mode=None,
                )
            with p4:
                st.selectbox(
                    "Your origin / home province",
                    ["(Any / Unspecified)"] + source_provinces,
                    key="f_source_prov",
                    filter_mode=None,
                )

        with st.expander("Advanced settings", icon=":material/settings:", expanded=False):
            a1, a2 = st.columns(2)
            with a1:
                class_labels = ["Top picks", "Good match", "Worth a look"]
                st.selectbox(
                    "Show me places that are…",
                    class_labels,
                    key="f_rank_class_label",
                    help="Top picks = Highly Recommend · Good match = Recommend · Worth a look = Neutral (experimental)",
                    filter_mode=None,
                )
            with a2:
                st.slider("Number of results to display", 1, 50, key="f_top_n")

        b_col1, b_col2, _ = st.columns([1.5, 1, 4])
        with b_col1:
            submit_btn = st.button("Find attractions", icon=":material/search:", type="primary", use_container_width=True)
        with b_col2:
            st.button(
                "Reset filters",
                icon=":material/restart_alt:",
                use_container_width=True,
                on_click=reset_filters_callback,
            )

    if submit_btn:
        execute_search()


def execute_search() -> None:
    """Build API payload directly from f_* state keys and invoke recommendation endpoint."""
    raw_target_class = LABEL_TO_CLASS.get(st.session_state.f_rank_class_label, "Highly Recommend")
    payload: dict = {
        "rank_class": raw_target_class,
        "top_n": int(st.session_state.f_top_n),
    }

    if st.session_state.f_province != "(All Provinces)":
        payload["province"] = st.session_state.f_province
    if st.session_state.f_city != "(All Cities)":
        payload["city"] = st.session_state.f_city
    if st.session_state.f_category != "(All Categories)":
        payload["category"] = st.session_state.f_category
    if st.session_state.f_use_budget:
        payload["max_ticket_price"] = float(st.session_state.f_budget)
    if st.session_state.f_season:
        payload["season"] = st.session_state.f_season
    if st.session_state.f_holiday != "(Any / Unspecified)":
        payload["is_holiday"] = st.session_state.f_holiday
    if st.session_state.f_age_group != "(Any / Unspecified)":
        payload["age_group"] = st.session_state.f_age_group
    if st.session_state.f_source_prov != "(Any / Unspecified)":
        payload["source_province"] = st.session_state.f_source_prov

    with st.spinner("Finding attractions that fit your trip..."):
        res, err = api_client.get_recommendations(payload)

    if err:
        st.session_state.last_results = None
        st.error(f"Unable to retrieve recommendations: {err}")
    else:
        st.session_state.last_results = res


# ──────────────────────────────────────────────────────────────────────────────
# 8. COMPONENT: RESULT CARD (QUALITATIVE STRENGTH, ZERO PERCENTAGES)
# ──────────────────────────────────────────────────────────────────────────────
def render_card(row: dict, rank: int, total_cards: int, terciles: tuple[float, float]) -> None:
    """Render a card container with text-only chips, qualitative strength, and ranking details."""
    raw_name = row.get("attraction_name", "Unknown Attraction")
    raw_city = row.get("city", "")
    raw_province = row.get("province", "")
    raw_category = row.get("category") or "General Attraction"

    name = html.escape(str(raw_name))
    city = html.escape(str(raw_city))
    province = html.escape(str(raw_province))
    category = html.escape(str(raw_category))

    level = row.get("attraction_level")
    price_val = row.get("ticket_price")
    price_str, is_free = format_price(price_val)
    pred_class = row.get("predicted_recommendation", "Recommend")
    score = row.get("svm_decision_score")

    user_friendly_class = CLASS_TO_LABEL.get(pred_class, pred_class)
    if pred_class == "Highly Recommend":
        match_chip_class = "chip-match-high"
        accent_color = "#10B981"
    elif pred_class == "Recommend":
        match_chip_class = "chip-match-med"
        accent_color = "#0284C7"
    else:
        match_chip_class = "chip-match-low"
        accent_color = "#F59E0B"

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="border-left: 4px solid {accent_color}; padding-left: 10px; margin: -5px 0 8px -5px;">
                <div class="card-header-row">
                    <h3 class="card-title">{name}</h3>
                    <span class="card-rank-badge">#{rank}</span>
                </div>
                <div class="card-location">{mi("location_on", "16px", "#64748B")} {city}, {province}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        level_chip = f'<span class="chip chip-level">{html.escape(str(level))} Level</span>' if level else ""
        price_chip = (
            f'<span class="chip chip-price-free">{price_str}</span>'
            if is_free
            else f'<span class="chip chip-price-paid">{price_str}</span>'
        )
        cat_chip = f'<span class="chip chip-category">{category}</span>'
        class_chip = f'<span class="chip {match_chip_class}">{user_friendly_class}</span>'

        st.markdown(
            f"""
            <div class="chips-wrap">
                {level_chip}
                {cat_chip}
                {price_chip}
                {class_chip}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Qualitative progress representation (No percentage displayed)
        q_low, q_high = terciles
        strength, strength_label = score_to_strength(score, q_low, q_high, rank, total_cards)
        st.progress(strength, text=f"Match strength: {strength_label}")

        btn_col, why_col = st.columns([1.4, 2])
        item_identity = trip_key(row)
        saved = is_saved(row)

        with btn_col:
            if saved:
                st.button(
                    "In trip plan",
                    icon=":material/check:",
                    key=f"saved_{item_identity}",
                    disabled=True,
                    use_container_width=True,
                )
            else:
                st.button(
                    "Add to trip",
                    icon=":material/bookmark_add:",
                    key=f"add_{item_identity}",
                    type="secondary",
                    use_container_width=True,
                    on_click=add_to_plan,
                    args=(row,),
                )

        with why_col:
            with st.expander("Ranking details", icon=":material/help:"):
                applied_filters: list[str] = []
                if st.session_state.f_province != "(All Provinces)":
                    applied_filters.append(f"Province: {st.session_state.f_province}")
                if st.session_state.f_city != "(All Cities)":
                    applied_filters.append(f"City: {st.session_state.f_city}")
                if st.session_state.f_category != "(All Categories)":
                    applied_filters.append(f"Category: {st.session_state.f_category}")
                if st.session_state.f_use_budget:
                    applied_filters.append(f"Max Ticket Price: ¥{st.session_state.f_budget:.0f}")

                # Profile fields not "(Any / Unspecified)"
                if st.session_state.f_holiday != "(Any / Unspecified)":
                    applied_filters.append(f"Holiday: {st.session_state.f_holiday}")
                if st.session_state.f_age_group != "(Any / Unspecified)":
                    applied_filters.append(f"Age Group: {st.session_state.f_age_group}")
                if st.session_state.f_source_prov != "(Any / Unspecified)":
                    applied_filters.append(f"Origin Province: {st.session_state.f_source_prov}")

                if applied_filters:
                    st.markdown("**Applied filters:**")
                    for flt in applied_filters:
                        st.markdown(f"- {flt}")
                else:
                    st.caption("No specific catalogue or profile filters applied.")

                if score is not None:
                    st.caption(f"Raw SVM decision score: `{score:.3f}`")


# ──────────────────────────────────────────────────────────────────────────────
# 9. COMPONENT: EXPLORER TAB WITH SUMMARY STRIP & VIEW TOGGLE
# ──────────────────────────────────────────────────────────────────────────────
def render_explorer() -> None:
    """Render Attraction Explorer tab with search bar, presets, summary strip, and cards."""
    if not backend_online:
        st.error(
            "The recommendation backend is currently offline. "
            "Please ensure FastAPI is started (`uvicorn main:app --reload`) on port 8000."
        )
        return

    # Trigger queued search from preset button clicks if flagged
    if st.session_state.get("pending_search", False):
        st.session_state.pending_search = False
        execute_search()

    provinces = options.get("provinces", [])
    cities = options.get("cities", [])
    categories = options.get("categories", [])
    cities_by_prov = st.session_state.cities_by_province

    render_filters(provinces, cities, categories, cities_by_prov)

    results_data = st.session_state.last_results

    if results_data is None:
        st.markdown(
            f"""
            <div class="empty-box">
                <div class="empty-icon">{mi("travel_explore", "40px", "#0F766E")}</div>
                <div class="empty-title">Ready to plan your trip to China?</div>
                <div class="empty-desc">
                    Choose a destination province above and click <strong>Find attractions</strong>,
                    or jump in with one of our curated destination ideas below.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### Popular Travel Presets")
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.button(
                "Sichuan Culture",
                icon=":material/temple_buddhist:",
                use_container_width=True,
                on_click=apply_preset_callback,
                args=("Sichuan", "Historical Culture"),
            )
        with p2:
            st.button(
                "Beijing Heritage",
                icon=":material/castle:",
                use_container_width=True,
                on_click=apply_preset_callback,
                args=("Beijing", "Historical Architecture"),
            )
        with p3:
            st.button(
                "Yunnan Scenery",
                icon=":material/landscape:",
                use_container_width=True,
                on_click=apply_preset_callback,
                args=("Yunnan", "Natural Scenery"),
            )
        with p4:
            st.button(
                "Shaanxi Relics",
                icon=":material/museum:",
                use_container_width=True,
                on_click=apply_preset_callback,
                args=("Shaanxi", "Historical Site"),
            )
        return

    recs = results_data.get("recommendations", [])
    count = results_data.get("count", 0)

    if count == 0:
        st.warning(
            "No attractions matched this exact combination. "
            "Try setting your Category to (All Categories) or increasing your maximum ticket price."
        )
        return

    prices = [r.get("ticket_price") for r in recs if r.get("ticket_price") is not None]
    if prices:
        min_p = min(prices)
        max_p = max(prices)
        price_text = f"Free–¥{max_p:.0f}" if min_p == 0 else f"¥{min_p:.0f}–¥{max_p:.0f}"
    else:
        price_text = "Ticket prices variable"

    prov_label = st.session_state.f_province if st.session_state.f_province != "(All Provinces)" else "All Provinces"
    season_label = format_season(st.session_state.f_season)
    esc_prov = html.escape(prov_label)
    esc_season = html.escape(season_label)

    s_col1, s_col2, s_col3 = st.columns([3, 1.2, 1])
    with s_col1:
        st.markdown(
            f"""
            <div class="summary-bar">
                <span>{mi("location_on", "18px", "#0F766E")} <strong>{count} attractions</strong> in {esc_prov} · {esc_season} · {price_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with s_col2:
        sort_choice = st.selectbox(
            "Sort by",
            ["Best match", "Price: Low to High", "Price: High to Low", "Level: 5A first"],
            label_visibility="collapsed",
            key="sort_selector",
            filter_mode=None,
        )
    with s_col3:
        view_choice = st.radio(
            "View",
            ["Cards", "Table"],
            horizontal=True,
            label_visibility="collapsed",
            key="view_selector",
        )

    # Compute score terciles once across the current result set
    scores = [
        float(r.get("svm_decision_score", 0.0))
        for r in recs
        if r.get("svm_decision_score") is not None
    ]
    if len(scores) >= 3:
        s_series = pd.Series(scores)
        q_low = float(s_series.quantile(1.0 / 3.0))
        q_high = float(s_series.quantile(2.0 / 3.0))
    elif len(scores) == 2:
        sorted_s = sorted(scores, reverse=True)
        q_high, q_low = sorted_s[0], sorted_s[1]
    elif len(scores) == 1:
        q_high = q_low = scores[0]
    else:
        q_high = q_low = 0.0

    terciles = (q_low, q_high)

    sorted_recs = list(recs)
    if sort_choice == "Price: Low to High":
        sorted_recs.sort(key=lambda x: (x.get("ticket_price") is None, x.get("ticket_price") or 0))
    elif sort_choice == "Price: High to Low":
        sorted_recs.sort(key=lambda x: (x.get("ticket_price") is None, -(x.get("ticket_price") or 0)))
    elif sort_choice == "Level: 5A first":
        level_map = {"5A": 3, "4A": 2, "3A": 1}
        sorted_recs.sort(key=lambda x: -level_map.get(str(x.get("attraction_level")), 0))

    if view_choice == "Table":
        table_df = pd.DataFrame([
            {
                "Rank": i + 1,
                "Attraction": r.get("attraction_name"),
                "City": r.get("city"),
                "Province": r.get("province"),
                "Level": r.get("attraction_level", "—"),
                "Category": r.get("category", "—"),
                "Price": format_price(r.get("ticket_price"))[0],
                "Match": CLASS_TO_LABEL.get(r.get("predicted_recommendation"), r.get("predicted_recommendation")),
                "Score": f"{r.get('svm_decision_score', 0.0):.3f}",
            }
            for i, r in enumerate(sorted_recs)
        ])
        st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        total_cards = len(sorted_recs)
        grid_c1, grid_c2 = st.columns(2)
        for i, item in enumerate(sorted_recs):
            with (grid_c1 if i % 2 == 0 else grid_c2):
                render_card(item, i + 1, total_cards, terciles)


# ──────────────────────────────────────────────────────────────────────────────
# 10. COMPONENT: MY TRIP PLAN (STATIC TAB WITH INTERNAL SAVED COUNT)
# ──────────────────────────────────────────────────────────────────────────────
def render_trip_plan() -> None:
    """Render personal itinerary with summary strip, removal controls, and CSV export."""
    plan = st.session_state.trip_plan
    st.subheader(f"My Trip Plan ({len(plan)} saved)")

    if not plan:
        st.markdown(
            f"""
            <div class="empty-box">
                <div class="empty-icon">{mi("map", "40px", "#0F766E")}</div>
                <div class="empty-title">Your travel shortlist is empty</div>
                <div class="empty-desc">
                    When exploring attractions in the explorer, click <strong>Add to trip</strong>
                    to bookmark places you want to visit and calculate your estimated budget.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    total_spots = len(plan)
    total_cost = sum(float(p.get("ticket_price") or 0) for p in plan)
    cities = {p.get("city") for p in plan if p.get("city")}

    m1, m2, m3, m4 = st.columns([1.5, 1.5, 1.5, 2])
    with m1:
        st.markdown(
            f'<div class="metric-tile"><div class="metric-val">{total_spots}</div><div class="metric-label">Saved Spots</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-tile"><div class="metric-val">{len(cities)}</div><div class="metric-label">Destinations</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-tile"><div class="metric-val">¥{total_cost:.0f}</div><div class="metric-label">Estimated Tickets</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        df_export = pd.DataFrame([
            {
                "Attraction": p.get("attraction_name"),
                "City": p.get("city"),
                "Province": p.get("province"),
                "Level": p.get("attraction_level"),
                "Price": format_price(p.get("ticket_price"))[0],
                "Category": p.get("category"),
            }
            for p in plan
        ])
        st.download_button(
            "Export Plan (CSV)",
            icon=":material/download:",
            data=df_export.to_csv(index=False).encode("utf-8"),
            file_name="my_china_trip_plan.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.button(
            "Clear entire plan",
            icon=":material/delete_sweep:",
            use_container_width=True,
            on_click=clear_plan_callback,
        )

    st.markdown("---")

    for i, item in enumerate(plan):
        raw_name = item.get("attraction_name", "Unknown")
        raw_city = item.get("city", "")
        raw_prov = item.get("province", "")
        raw_cat = item.get("category") or "General"

        name = html.escape(str(raw_name))
        city = html.escape(str(raw_city))
        prov = html.escape(str(raw_prov))
        cat = html.escape(str(raw_cat))

        level = item.get("attraction_level")
        price_str, _ = format_price(item.get("ticket_price"))
        identity = trip_key(item)

        # Build clean caption: hide level if missing and label as "Level:"
        caption_items = []
        if level and str(level).strip() not in ("N/A", "—", "None", ""):
            caption_items.append(f"Level: {level}")
        caption_items.append(f"Category: {cat}")
        caption_items.append(f"Ticket: {price_str}")
        caption_line = " | ".join(caption_items)

        with st.container(border=True):
            row_l, row_r = st.columns([5, 1.2])
            with row_l:
                st.markdown(f"**{i + 1}. {name}** — {mi('location_on', '16px', '#64748B')} {city}, {prov}", unsafe_allow_html=True)
                st.caption(caption_line)
            with row_r:
                st.button(
                    "Remove",
                    icon=":material/delete:",
                    key=f"del_{identity}",
                    use_container_width=True,
                    on_click=remove_from_plan,
                    args=(identity,),
                )


# ──────────────────────────────────────────────────────────────────────────────
# 11. COMPONENT: HOW IT WORKS
# ──────────────────────────────────────────────────────────────────────────────
def render_how_it_works() -> None:
    """Render 3-step visual cards and technical architecture disclosure."""
    st.subheader("How the Recommendation Engine Works")
    st.caption("A transparent, two-stage system combining deterministic catalogue filtering with Linear SVM ranking.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">Step 1</div>
                <div class="step-title">1. You Set Your Preferences</div>
                <div class="step-desc">
                    Choose destination preferences (province, city, category, budget) alongside optional
                    travel context like travel season, age group, and holiday timing.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">Step 2</div>
                <div class="step-title">2. We Narrow the Catalogue</div>
                <div class="step-desc">
                    Hard catalogue rules instantly filter our database of 433 vetted attractions.
                    Any spot exceeding your budget or outside your chosen region is safely eliminated.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">Step 3</div>
                <div class="step-title">3. The AI Ranks What's Left</div>
                <div class="step-desc">
                    Our pre-trained Balanced Linear SVM evaluates remaining candidates across 9 features,
                    ranking the most suitable destinations based on your travel profile.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Deep Dive: Pre-trip Features & Leakage Prevention", icon=":material/analytics:"):
        st.markdown(
            """
            * **Nine Pre-Trip Features Only:** The model evaluates `age_group`, `source_province`, `attraction_name`,
              `attraction_category`, `attraction_level`, `city`, `province`, `season`, and `is_holiday`.
            * **No Data Leakage:** Post-visit variables like satisfaction levels and review scores were deliberately excluded
              from the model inputs because they cannot be known prior to taking a trip.
            * **Decision Scores vs. Probabilities:** The decision score measures distance to the SVM separating hyperplane.
              Higher scores indicate a stronger recommendation match, but are not calibrated percentages.
            """
        )


# ──────────────────────────────────────────────────────────────────────────────
# 12. COMPONENT: MODEL EVALUATION
# ──────────────────────────────────────────────────────────────────────────────
def render_model_evaluation() -> None:
    """Render audited test set metrics, class breakdowns, and validation results."""
    st.subheader("Model Performance & Evaluation")
    st.caption("Audited held-out test partition (15,209 records, grouped by tourist ID with zero overlap).")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="metric-tile"><div class="metric-val">67.80%</div><div class="metric-label">Test Accuracy</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-tile"><div class="metric-val">73.29%</div><div class="metric-label">Balanced Accuracy</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-tile"><div class="metric-val">0.5730</div><div class="metric-label">Macro F1 Score</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="metric-tile"><div class="metric-val">0.6788</div><div class="metric-label">Weighted F1</div></div>', unsafe_allow_html=True)

    st.markdown("#### Class-wise Performance")
    st.markdown(
        """
        | Class | User Label | Precision | Recall | F1-Score | Support |
        |---|---|---:|---:|---:|---:|
        | **Highly Recommend** | Top picks | 0.6811 | 0.6707 | 0.6759 | 7,465 |
        | **Recommend** | Good match | 0.6818 | 0.6843 | 0.6830 | 7,712 |
        | **Neutral** | Worth a look | 0.2288 | 0.8438 | 0.3600 | 32 |
        
        *Notice: The Neutral class contains only 32 samples in the held-out test set (241 in the entire dataset). Results for this label carry statistical variance.*
        """
    )

    with st.expander("Model Benchmark: Linear SVM vs. Random Forest", icon=":material/compare_arrows:"):
        st.markdown(
            """
            | Metric | Balanced Linear SVM (Selected) | Random Forest (Class-Weighted) |
            |---|---:|---:|
            | **Accuracy** | **67.80%** | 64.94% |
            | **Balanced Accuracy** | **73.29%** | 49.60% |
            | **Macro F1** | **0.5730** | 0.5166 |
            | **Weighted F1** | **0.6788** | 0.6491 |

            Linear SVM was chosen because it maintains significantly stronger balanced recall across imbalanced target classes.
            """
        )


# ──────────────────────────────────────────────────────────────────────────────
# 13. MAIN CONTROLLER
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    inject_css()
    render_header()

    tab_explore, tab_plan, tab_how, tab_model = st.tabs(
        [
            ":material/explore: Attraction Explorer",
            ":material/map: My Trip Plan",
            ":material/menu_book: How It Works",
            ":material/query_stats: Model Evaluation",
        ]
    )

    with tab_explore:
        render_explorer()

    with tab_plan:
        render_trip_plan()

    with tab_how:
        render_how_it_works()

    with tab_model:
        render_model_evaluation()


if __name__ == "__main__":
    main()
