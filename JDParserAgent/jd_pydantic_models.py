from pydantic import BaseModel, Field


class skillsInfo(BaseModel):
    programming_languages: list[str] = Field(default=[], description="Programming languages as required, \
        Ex: Python,C,C++ etc if not present then return None")
    frameworks_and_libraries: list[str] = Field(default=[], description="Frameworks and libraries as required, \
        Ex: React,Angular,Django,Flask,Pandas,Pytorch etc if not present then return None")
    tools: list[str] = Field(default=[], description="Tools as required, \
        Ex: Git,Docker,Kubernetes,Jenkins,Jira,etc. if not present then return None")
    databases: list[str] = Field(default=[], description="Databases as required, \
        Ex: MySQL,PostgreSQL,MongoDB,Oracle,etc. if not present then return None")
    cloud_and_infra: list[str] = Field(default=[], description="Cloud and infra as required, \
        Ex: AWS,Azure,GCP,etc. if not present then return None")


class locationInfo(BaseModel):
    city: str | None = Field(default=None, description="City where the job is located, e.g. 'Bangalore'. Return None if not mentioned.")
    country: str | None = Field(default=None, description="Country, e.g. 'India', 'USA'. Return None if not mentioned.")


class JobDescription(BaseModel):
    role_title: str = Field(..., description="The standard job title, e.g., 'Senior Backend Engineer'")
    company_name: str | None = Field(default=None, description="Name of the company")
    salary_range: str | None = Field(default=None, description="e.g. '$120k - $160k'. Return None if not mentioned.")

    location: list[locationInfo] = Field(default=[], description="List of job locations. Extract all locations mentioned in the JD. Many JDs list multiple cities or countries.")

    job_type: str = Field(
        default="Full Time",
        description="Employment type. One of: 'Full Time', 'Part Time', 'Contract', 'Internship', 'Freelance'. "
                    "Default to 'Full Time' if not explicitly stated."
    )
    job_level: str = Field(
        ...,
        description="Seniority level inferred from title, years of experience, and responsibilities. "
                    "One of: 'Junior', 'Mid', 'Senior', 'Lead', 'Manager', 'Director', 'VP', 'C-Level'. "
                    "Infer from context: 0-2 yrs -> Junior, 2-5 yrs -> Mid, 5-8 yrs -> Senior, "
                    "8+ yrs or team management -> Lead/Manager. Use title keywords (e.g. 'Sr.', 'Principal', 'Staff') as strong signals."
    )
    work_mode: str = Field(
        default="In Office",
        description="Work arrangement. One of: 'In Office', 'Remote', 'Hybrid', 'Work From Home'. "
                    "Default to 'In Office' if not explicitly mentioned. "
                    "'Work From Home' only if explicitly stated as WFH. "
                    "'Remote' if the JD says 'Remote' or 'Fully Remote'. "
                    "'Hybrid' only if explicitly mentioned."
    )

    mandatory_skills: skillsInfo = Field(..., description="Technical skills explicitly marked as required")

    optional_skills: list[str] = Field(default=[], description="Skills listed as 'preferred', 'bonus', or 'plus'")

    min_years_experience: int | None = Field(default=None, description="Minimum years of experience required. e.g. '3-5 years' -> 3, '5+ years' -> 5. Return None if not mentioned.")
    max_years_experience: int | None = Field(default=None, description="Maximum years of experience required. e.g. '3-5 years' -> 5. Return None if only a minimum is stated (e.g. '5+ years') or not mentioned.")

    degree_required: str | None = Field(default=None, description="e.g. 'Bachelor in CS', 'PhD'")

    summary_responsibilities: list[str] = Field(..., description="Top 3-5 core responsibilities summarized")
