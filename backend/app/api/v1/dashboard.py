from collections import Counter, defaultdict
from statistics import mean

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.db.models.prediction_history import PredictionHistory
from app.db.models.user import User


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _prediction_label(value):
    if value is None:
        return "Unknown"

    text = str(value).strip()
    normalized = text.lower()

    if normalized in {"1", "1.0", "true", "resistant", "resistance"}:
        return "Resistant"
    if normalized in {"0", "0.0", "false", "sensitive", "sensitivity"}:
        return "Sensitive"

    return text or "Unknown"


def _confidence_percent(value):
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0

    if confidence <= 1:
        confidence *= 100

    return max(0, min(100, round(confidence)))


def _display_cancer_type(value):
    if not value:
        return "Unspecified cancer"

    return str(value).replace("_", " ").replace("-", " ").title()


def _display_drug(value):
    if value and str(value).strip():
        drug = str(value).strip()
        if drug.lower() not in {"unknown", "n/a", "none"}:
            return drug

    return "Unknown drug"


def _analysis_title(record):
    cancer_type = _display_cancer_type(record.cancer_type)
    drug = _display_drug(record.drug_name)

    if drug != "Unknown drug":
        return f"{cancer_type} response to {drug}"

    return f"{cancer_type} response analysis"


def _pathway_impact(pathway):
    if not isinstance(pathway, dict):
        return None

    raw_value = pathway.get("impact", pathway.get("weight", pathway.get("score")))

    try:
        impact = float(raw_value)
    except (TypeError, ValueError):
        return None

    if abs(impact) <= 1:
        impact *= 100

    return max(0, round(abs(impact)))


def _records_for_user(db: Session, user_id: int):
    return (
        db.query(PredictionHistory)
        .options(joinedload(PredictionHistory.details))
        .filter(PredictionHistory.user_id == user_id)
        .order_by(PredictionHistory.analysis_date.desc())
        .all()
    )


def _top_pathway_stats(records, limit=5):
    counts = Counter()
    impacts = defaultdict(list)

    for record in records:
        details = record.details
        pathways = details.pathways if details and details.pathways else []

        for pathway in pathways:
            if not isinstance(pathway, dict):
                continue

            name = str(pathway.get("name") or "").strip()
            if not name:
                continue

            counts[name] += 1

            impact = _pathway_impact(pathway)
            if impact is not None:
                impacts[name].append(impact)

    ranked = sorted(
        counts.items(),
        key=lambda item: (
            item[1],
            mean(impacts[item[0]]) if impacts[item[0]] else 0,
        ),
        reverse=True,
    )

    return [
        {
            "name": name,
            "count": count,
            "averageImpact": round(mean(impacts[name])) if impacts[name] else 0,
        }
        for name, count in ranked[:limit]
    ]


def _analyses_over_time(records):
    counts = Counter()

    for record in records:
        if record.analysis_date:
            counts[record.analysis_date.strftime("%Y-%m-%d")] += 1

    return [
        {"date": date, "count": count}
        for date, count in sorted(counts.items())
    ]


def _serialize_analysis(record):
    return {
        "id": record.analysis_code,
        "analysis_code": record.analysis_code,
        "title": _analysis_title(record),
        "cancerType": _display_cancer_type(record.cancer_type),
        "drug": _display_drug(record.drug_name),
        "prediction": _prediction_label(record.prediction_result),
        "confidence": _confidence_percent(record.confidence_score),
        "date": (
            record.analysis_date.strftime("%Y-%m-%d")
            if record.analysis_date
            else "N/A"
        ),
    }


@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = _records_for_user(db, current_user.id)
    prediction_counts = Counter(
        _prediction_label(record.prediction_result)
        for record in records
    )
    pathway_stats = _top_pathway_stats(records)
    top_pathway = pathway_stats[0] if pathway_stats else None

    distribution = [
        {"label": "Resistant", "count": prediction_counts.get("Resistant", 0)},
        {"label": "Sensitive", "count": prediction_counts.get("Sensitive", 0)},
    ]

    unknown_count = sum(
        count
        for label, count in prediction_counts.items()
        if label not in {"Resistant", "Sensitive"}
    )
    if unknown_count:
        distribution.append({"label": "Unknown", "count": unknown_count})

    return {
        "doctorName": current_user.full_name or current_user.email or "User",
        "totalAnalyses": len(records),
        "resistant": prediction_counts.get("Resistant", 0),
        "sensitive": prediction_counts.get("Sensitive", 0),
        "topPathway": top_pathway["name"] if top_pathway else "N/A",
        "topPathwayCount": top_pathway["count"] if top_pathway else 0,
        "resistanceDistribution": distribution,
        "topAffectedPathways": pathway_stats,
        "analysesOverTime": _analyses_over_time(records),
    }


@router.get("/recent")
async def get_recent(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recent_records = (
        db.query(PredictionHistory)
        .options(joinedload(PredictionHistory.details))
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.analysis_date.desc())
        .limit(5)
        .all()
    )

    return [_serialize_analysis(record) for record in recent_records]


@router.get("/analyses")
async def get_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = _records_for_user(db, current_user.id)
    return [_serialize_analysis(record) for record in records]
