import io
import logging

from langgraph.graph import StateGraph, START, END
from PIL import Image
from langchain_core.runnables.graph import MermaidDrawMethod

from state import AgentState

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def normalize_jd_data(result, markdown: str):
    optional_skills = result.optional_skills or []
    industry_domains = result.industry_domains or []

    # "Data lakes" appears in the analytics leadership JDs as part of mandatory platform experience.
    normalized_optional = []
    for skill in optional_skills:
        if skill.lower() in {"data lakes", "data lake"}:
            if "Data lakes" not in result.mandatory_skills.cloud_and_infra:
                result.mandatory_skills.cloud_and_infra.append("Data lakes")
            continue
        normalized_optional.append(skill)

    domain_names = {domain.lower() for domain in industry_domains}
    normalized_optional = [
        skill for skill in normalized_optional
        if skill.lower() not in domain_names
    ]
    result.optional_skills = normalized_optional

    # Keep industry domains focused on true business domains rather than generic analytics terms.
    result.industry_domains = [
        domain for domain in industry_domains
        if domain.lower() not in {"analytics", "business intelligence", "bi"}
    ]

    return result


# --- Nodes ---

def ocr_jd(state: AgentState) -> dict:
    from ocr import upload_file, get_ocr_response

    url = upload_file(state["jd_file_path"])
    ocr_response = get_ocr_response(url)
    pages = getattr(ocr_response, "pages", None) or []
    markdown_parts = [
        page.markdown
        for page in pages
        if getattr(page, "markdown", None)
    ]
    if not markdown_parts:
        fallback_markdown = getattr(ocr_response, "markdown", None)
        if fallback_markdown:
            markdown_parts = [fallback_markdown]
    if not markdown_parts:
        raise ValueError("OCR returned no markdown content for the uploaded JD.")

    markdown = " ".join(markdown_parts)

    logger.info(f"OCR completed for file {state['jd_file_path']}. Extracted markdown length: {len(markdown)} characters.")
    return {"jd_markdown": markdown}


def parse_jd(state: AgentState) -> dict:
    from jd_chain import get_jd_chain

    chain = get_jd_chain()
    result = chain.invoke({"job_description_markdown": state["jd_markdown"]})
    result = normalize_jd_data(result, state["jd_markdown"])

    logger.info("JD parsing completed.")
    return {"jd_data": result}


def llm_as_judge(state: AgentState) -> dict:
    from judge_chain import get_judge_chain

    chain = get_judge_chain()
    try:
        result = chain.invoke({
            "markdown": state["jd_markdown"],
            "jsondata": state["jd_data"].model_dump_json(indent=4),
        })
    except Exception as exc:
        logger.warning("LLM judge failed, returning REVIEW instead of crashing: %s", exc)
        return {
            "reflection_loop": state["reflection_loop"] + 1,
            "judge_results": [
                {
                    "source": "jd",
                    "grade": "REVIEW",
                    "summary": f"Judge unavailable or malformed provider response: {exc}",
                }
            ],
        }

    logger.info(f"LLM judge completed. Grade: {result.grade}, Summary: {result.grade_summary}")
    return {
        "reflection_loop": state["reflection_loop"] + 1,
        "judge_results": [
            {"source": "jd", "grade": result.grade, "summary": result.grade_summary}
        ],
    }


# --- Routing ---

def reflection_path(state: AgentState) -> str:
    """Retry once on FAIL, then always end."""
    if state["reflection_loop"] > 1:
        return "end"

    judge_results = state["judge_results"]
    if judge_results and judge_results[-1]["grade"] == "FAIL":
        logger.info(f"Judge returned FAIL on loop {state['reflection_loop']}. Retrying parse_jd.")
        return "FAIL"

    return "end"


# --- Graph Builder ---

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("ocr_jd", ocr_jd)
    graph.add_node("parse_jd", parse_jd)
    graph.add_node("llm_as_judge", llm_as_judge)

    graph.add_edge(START, "ocr_jd")
    graph.add_edge("ocr_jd", "parse_jd")
    graph.add_edge("parse_jd", "llm_as_judge")
    graph.add_conditional_edges(
        "llm_as_judge",
        reflection_path,
        {
            "FAIL": "parse_jd",
            "end": END,
        },
    )

    app = graph.compile()
    try:
        img = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        img = Image.open(io.BytesIO(img))
        img.save("jd_agent_graph.png")
    except Exception as exc:
        logger.warning("Skipping jd_agent_graph.png generation: %s", exc)
    return graph.compile()


if __name__ == "__main__":
    build_graph()
