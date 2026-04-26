"""
Compute a JDScorecard from an extracted JobDescription object.

This is a deterministic (non-LLM) computation derived from the parsed fields,
so it adds zero latency to the pipeline.
"""

from jd_pydantic_models import JobDescription, JDScorecard


def compute_scorecard(jd: JobDescription) -> JDScorecard:
    must_have: list[str] = (
        jd.mandatory_skills.programming_languages
        + jd.mandatory_skills.frameworks_and_libraries
        + jd.mandatory_skills.tools
        + jd.mandatory_skills.databases
        + jd.mandatory_skills.cloud_and_infra
    )

    # ── Role Clarity (0–10) ───────────────────────────────────────────────────
    role_clarity = 0
    if jd.role_title:
        role_clarity += 3
    if len(jd.summary_responsibilities) >= 3:
        role_clarity += 4
    if len(jd.summary_responsibilities) >= 6:
        role_clarity += 3
    role_clarity = min(10, role_clarity)

    # ── Tech Specificity (0–10) ───────────────────────────────────────────────
    total_skills = len(must_have) + len(jd.optional_skills)
    if total_skills >= 14:
        tech_specificity = 10
    elif total_skills >= 10:
        tech_specificity = 9
    elif total_skills >= 7:
        tech_specificity = 7
    elif total_skills >= 4:
        tech_specificity = 5
    elif total_skills >= 1:
        tech_specificity = 3
    else:
        tech_specificity = 0

    # ── Consulting vs Product ─────────────────────────────────────────────────
    title_lower = (jd.role_title or "").lower()
    if "consultant" in title_lower or "advisor" in title_lower:
        consulting_vs_product: str | None = "Consulting"
    elif any(w in title_lower for w in ["product", "engineer", "developer", "analyst", "scientist"]):
        consulting_vs_product = "Product"
    else:
        consulting_vs_product = None

    # ── Experience Inflation ──────────────────────────────────────────────────
    min_exp = jd.min_years_experience or 0
    max_exp = jd.max_years_experience or min_exp
    experience_inflation = "flagged" if min_exp > 8 or (max_exp - min_exp) > 10 else "ok"

    # ── Missing Screening Criteria ────────────────────────────────────────────
    missing_screening: list[str] = []
    if not jd.degree_required:
        missing_screening.append("Education requirement")
    if not must_have:
        missing_screening.append("Required skills")
    if jd.min_years_experience is None:
        missing_screening.append("Experience range")

    # ── Compensation Signal ───────────────────────────────────────────────────
    compensation_signal = jd.salary_range if jd.salary_range else "CTC not specified"

    return JDScorecard(
        role_clarity=role_clarity,
        tech_specificity=tech_specificity,
        consulting_vs_product=consulting_vs_product,
        experience_inflation=experience_inflation,
        missing_screening=missing_screening,
        compensation_signal=compensation_signal,
    )
