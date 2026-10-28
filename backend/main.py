from pathlib import Path
from typing import Optional
import math

import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "final_linear_svm_pipeline.joblib"
CATALOGUE_PATH = BASE_DIR / "tourism_attraction_catalogue.csv"
DATASET_PATH = BASE_DIR / "tourism_recommendation_dataset_en.csv"

for path in [MODEL_PATH, CATALOGUE_PATH, DATASET_PATH]:
    if not path.is_file():
        raise FileNotFoundError(f"Required API file missing: {path}")

model = joblib.load(MODEL_PATH)
catalogue = pd.read_csv(CATALOGUE_PATH)

context_columns = [
    "season", "is_holiday", "age_group", "source_province"
]
reference = pd.read_csv(
    DATASET_PATH,
    usecols=context_columns,
    low_memory=False,
)

FEATURES = [
    "age_group",
    "source_province",
    "attraction_name",
    "attraction_category",
    "attraction_level",
    "city",
    "province",
    "season",
    "is_holiday",
]

IDENTITY = ["attraction_name", "city", "province"]
CLASSES = model.named_steps["classifier"].classes_.tolist()

if catalogue.duplicated(IDENTITY).any():
    raise ValueError("The catalogue contains duplicate location identities.")

catalogue["ticket_price"] = pd.to_numeric(
    catalogue["ticket_price"], errors="coerce"
)

def values(column):
    return sorted(
        reference[column].dropna().astype(str).str.strip().unique().tolist()
    )

OPTIONS = {
    "provinces": sorted(catalogue["province"].dropna().unique().tolist()),
    "cities": sorted(catalogue["city"].dropna().unique().tolist()),
    "categories": sorted(
        catalogue["attraction_category"].dropna().unique().tolist()
    ),
    "seasons": values("season"),
    "holiday_options": values("is_holiday"),
    "age_groups": values("age_group"),
    "source_provinces": values("source_province"),
    "attraction_levels": sorted(
        catalogue["attraction_level"].dropna().unique().tolist()
    ),
    "recommendation_classes": CLASSES,
}

app = FastAPI(
    title="China Tourism Recommendation API",
    version="1.0.0",
    description="Experimental tourism recommendation service using Linear SVM.",
)

class RecommendationRequest(BaseModel):
    province: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    max_ticket_price: Optional[float] = Field(default=None, ge=0)
    season: Optional[str] = None
    is_holiday: Optional[str] = None
    age_group: Optional[str] = None
    source_province: Optional[str] = None
    rank_class: str = "Highly Recommend"
    top_n: int = Field(default=10, ge=1, le=50)

def canonical(value, options, field):
    if value is None:
        return None
    lookup = {str(v).strip().casefold(): str(v).strip() for v in options}
    key = str(value).strip().casefold()
    if key not in lookup:
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Invalid value for {field}",
                "provided": value,
                "allowed_values": options,
            },
        )
    return lookup[key]

@app.get("/")
def root():
    return {
        "name": "China Tourism Recommendation API",
        "status": "ready",
        "docs": "/docs",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "Balanced Linear SVM",
        "catalogue_entries": len(catalogue),
        "classes": CLASSES,
    }

@app.get("/options")
def get_options():
    return OPTIONS

@app.post("/recommendations")
def recommendations(request: RecommendationRequest):
    province = canonical(request.province, OPTIONS["provinces"], "province")
    city = canonical(request.city, OPTIONS["cities"], "city")
    category = canonical(request.category, OPTIONS["categories"], "category")
    season = canonical(request.season, OPTIONS["seasons"], "season")
    holiday = canonical(
        request.is_holiday, OPTIONS["holiday_options"], "is_holiday"
    )
    age_group = canonical(
        request.age_group, OPTIONS["age_groups"], "age_group"
    )
    source_province = canonical(
        request.source_province,
        OPTIONS["source_provinces"],
        "source_province",
    )
    rank_class = canonical(
        request.rank_class, CLASSES, "rank_class"
    )

    budget = request.max_ticket_price
    if budget is not None and not math.isfinite(budget):
        raise HTTPException(
            status_code=422,
            detail="Budget must be a finite number.",
        )

    # Apply mandatory catalogue constraints before inference.
    eligible = catalogue.copy()

    if province is not None:
        eligible = eligible[eligible["province"] == province]
    if city is not None:
        eligible = eligible[eligible["city"] == city]
    if category is not None:
        eligible = eligible[eligible["attraction_category"] == category]
    if budget is not None:
        eligible = eligible[
            eligible["ticket_price"].notna()
            & (eligible["ticket_price"] <= budget)
        ]

    if eligible.empty:
        return {
            "count": 0,
            "recommendations": [],
            "message": "No attractions match these filters. Try relaxing them.",
        }

    n = len(eligible)
    X = pd.DataFrame({
        "age_group": [age_group] * n,
        "source_province": [source_province] * n,
        "attraction_name": eligible["attraction_name"].to_numpy(),
        "attraction_category": eligible["attraction_category"].to_numpy(),
        "attraction_level": eligible["attraction_level"].to_numpy(),
        "city": eligible["city"].to_numpy(),
        "province": eligible["province"].to_numpy(),
        "season": [season] * n,
        "is_holiday": [holiday] * n,
    })[FEATURES]

    predictions = model.predict(X)
    scores = model.decision_function(X)

    class_index = CLASSES.index(rank_class)
    selected_scores = scores[:, class_index]

    ranked = eligible.copy()
    ranked["predicted_recommendation"] = predictions
    ranked["svm_decision_score"] = selected_scores
    ranked = ranked.sort_values("svm_decision_score", ascending=False).head(
        request.top_n
    )

    filters = {}
    if province is not None:
        filters["province"] = province
    if city is not None:
        filters["city"] = city
    if category is not None:
        filters["category"] = category
    if budget is not None:
        filters["max_ticket_price"] = budget

    context = {
        k: v for k, v in {
            "season": season,
            "is_holiday": holiday,
            "age_group": age_group,
            "source_province": source_province,
        }.items() if v is not None
    }

    results = []
    for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
        price = row["ticket_price"]
        results.append({
            "rank": rank,
            "attraction_name": str(row["attraction_name"]),
            "city": str(row["city"]),
            "province": str(row["province"]),
            "category": (
                None if pd.isna(row["attraction_category"])
                else str(row["attraction_category"])
            ),
            "attraction_level": (
                None if pd.isna(row["attraction_level"])
                else str(row["attraction_level"])
            ),
            "ticket_price": None if pd.isna(price) else float(price),
            "predicted_recommendation": str(
                row["predicted_recommendation"]
            ),
            "ranking_class": rank_class,
            "svm_decision_score": float(row["svm_decision_score"]),
            "applied_filters": filters,
            "ranking_context": context,
        })

    return {
        "count": len(results),
        "ranking_method": "Linear SVM decision score",
        "recommendations": results,
        "note": (
            "Decision scores are not calibrated probabilities. "
            "Dataset ticket prices are not live prices."
        ),
    }
