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
    def dedupe_keep_order(values):
        output = []
        seen = set()
        for value in values or []:
            if not value:
                continue
            normalized = " ".join(str(value).split()).strip()
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            output.append(normalized)
        return output

    result.mandatory_skills.programming_languages = dedupe_keep_order(result.mandatory_skills.programming_languages)
    result.mandatory_skills.frameworks_and_libraries = dedupe_keep_order(result.mandatory_skills.frameworks_and_libraries)
    result.mandatory_skills.tools = dedupe_keep_order(result.mandatory_skills.tools)
    result.mandatory_skills.databases = dedupe_keep_order(result.mandatory_skills.databases)
    result.mandatory_skills.cloud_and_infra = dedupe_keep_order(result.mandatory_skills.cloud_and_infra)

    result.industry_domains = [
        domain for domain in dedupe_keep_order(result.industry_domains)
        if domain.lower() not in {"analytics", "business intelligence", "bi"}
    ]

    domain_names = {domain.lower() for domain in result.industry_domains}
    result.optional_skills = [
        skill for skill in dedupe_keep_order(result.optional_skills)
        if skill.lower() not in domain_names
    ]

    result.summary_responsibilities = dedupe_keep_order(result.summary_responsibilities)

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
