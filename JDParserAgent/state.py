import operator
from typing import Annotated, TypedDict, Optional

from jd_pydantic_models import JobDescription


class AgentState(TypedDict):
    # --- Input ---
    jd_file_path: str
    # --- Intermediate ---
    jd_markdown: Optional[str]
    # --- Extraction result ---
    jd_data: JobDescription | None
    # --- Judge ---
    reflection_loop: int
    judge_results: Annotated[list[dict], operator.add]
