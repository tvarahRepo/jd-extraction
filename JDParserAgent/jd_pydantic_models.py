from pydantic import BaseModel, Field


class skillsInfo(BaseModel):
    programming_languages: list[str] = Field(
        default=[],
        description="Programming languages required for the role, e.g. Python, SQL, R",
    )
    frameworks_and_libraries: list[str] = Field(
        default=[],
        description="Frameworks and libraries required for the role, e.g. Pandas, Scikit-learn, TensorFlow",
    )
    tools: list[str] = Field(
        default=[],
        description="Tools and platforms required for the role, e.g. Power BI, Tableau, QlikView, Spotfire, ETL frameworks",
    )
    databases: list[str] = Field(
        default=[],
        description="Databases or database technologies required for the role, e.g. MS SQL, PostgreSQL, MySQL, Oracle",
    )
    cloud_and_infra: list[str] = Field(
        default=[],
        description="Cloud and data platform technologies required for the role, e.g. Azure, AWS, Databricks, Snowflake",
    )


class locationInfo(BaseModel):
    city: str | None = Field(
        default=None,
        description="City where the job is located, e.g. Bengaluru. Return None if not mentioned.",
    )
    country: str | None = Field(
        default=None,
        description="Country where the job is located, e.g. India or USA. Return None if not mentioned.",
    )


class JobDescription(BaseModel):
    role_title: str = Field(
        ...,
        description="The primary job title. Prefer the prominent JD header title over alternate titles in the body.",
    )
    company_name: str | None = Field(
        default=None,
        description="Name of the hiring company or employer",
    )
    salary_range: str | None = Field(
        default=None,
        description="Salary range such as '$120k - $160k'. Return None if not mentioned.",
    )

    location: list[locationInfo] = Field(
        default=[],
        description="Actual job location(s). Ignore generic office lists unless the JD explicitly says the role is open in those places.",
    )

    job_type: str = Field(
        default="Full Time",
        description="Employment type. One of: Full Time, Part Time, Contract, Internship, Freelance. Default to Full Time if not explicitly stated.",
    )
    job_level: str = Field(
        ...,
        description="Seniority level inferred from title, years of experience, and responsibilities. Must be one of: Junior, Mid, Senior, Lead, Manager, Director, VP, C-Level.",
    )
    work_mode: str = Field(
        default="In Office",
        description="Work arrangement. One of: In Office, Remote, Hybrid, Work From Home. Default to In Office if not explicitly mentioned.",
    )

    mandatory_skills: skillsInfo = Field(
        ...,
        description="Technical or platform skills explicitly marked as required or clearly central to the role",
    )
    optional_skills: list[str] = Field(
        default=[],
        description="Skills listed as preferred, bonus, plus, nice to have, good to have, or value addition",
    )

    min_years_experience: int | None = Field(
        default=None,
        description="Minimum years of experience required. Example: '3-5 years' -> 3, '5+ years' -> 5.",
    )
    max_years_experience: int | None = Field(
        default=None,
        description="Maximum years of experience required. Example: '3-5 years' -> 5. Return None if only a minimum is stated.",
    )

    degree_required: str | None = Field(
        default=None,
        description="Education requirement such as 'B.E, MBA or an Advanced degree in Mathematics/Statistics' or 'Bachelor in CS'",
    )
    team_size: str | None = Field(
        default=None,
        description="Explicit team size or direct-report count, e.g. '15-20 team members'. Return None if not stated.",
    )
    industry_domains: list[str] = Field(
        default=[],
        description="Industry domains explicitly mentioned as relevant or preferred, e.g. CPG, Supply Chain, Manufacturing, Marketing, BFSI",
    )

    summary_responsibilities: list[str] = Field(
        ...,
        description="Top 3-5 core responsibilities summarized from the JD",
    )


class JDScorecard(BaseModel):
    role_clarity: int = Field(
        default=0,
        description="0–10 score for how clearly the role is defined (title + responsibilities)",
    )
    tech_specificity: int = Field(
        default=0,
        description="0–10 score for how specific the tech requirements are (number of named tools/skills)",
    )
    consulting_vs_product: str | None = Field(
        default=None,
        description="Company archetype: Consulting, Product, Both, or null if unclear",
    )
    experience_inflation: str = Field(
        default="ok",
        description="'ok' or 'flagged' — flagged if min experience > 8 yrs or range > 10 yrs",
    )
    missing_screening: list[str] = Field(
        default=[],
        description="List of important screening criteria absent from the JD. Empty if nothing is missing.",
    )
    compensation_signal: str = Field(
        default="CTC not specified",
        description="Exact salary/CTC range if mentioned, otherwise 'CTC not specified'",
    )
