from pydantic import BaseModel, Field


class judgeJson(BaseModel):
    grade: str = Field(..., description="PASS or FAIL")
    grade_summary: str = Field(..., description="Summary of what things are right or what is wrong with the extraction")
