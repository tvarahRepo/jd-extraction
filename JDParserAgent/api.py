"""
FastAPI deployment for the JDParserAgent.

Run from inside the JDParserAgent/ directory:
    uvicorn api:app --reload --host 0.0.0.0 --port 8001

Endpoints:
    POST /parse     — Upload a JD PDF/DOCX, get structured JSON back
    GET  /health    — Health check
"""

import logging
import os
import sys
import tempfile

# Ensure flat imports (ocr, config, state, etc.) resolve from this directory
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from workflow import build_graph

# --- Logging ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("JDParserAgent")

# --- App ---

app = FastAPI(
    title="JD Parser Agent",
    description="Extracts structured data from Job Description PDFs/DOCXs using Mistral OCR + LLM parsing.",
    version="1.0.0",
)

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

# Compile the graph once at startup
logger.info("Compiling LangGraph workflow...")
graph = build_graph()
logger.info("Graph compiled and ready.")


# --- Endpoints ---
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jdParse")
async def parse_jd(file: UploadFile = File(...)):
    logger.info(f"Received file: '{file.filename}' ({file.content_type})")

    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        logger.warning(f"Rejected unsupported file type: '{ext}' from file '{file.filename}'")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Only PDF and DOCX are accepted.",
        )

    # Save upload to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    logger.info(f"Saved to temp file: {tmp_path}")

    try:
        logger.info("Invoking LangGraph workflow...")
        result = graph.invoke({
            "jd_file_path": tmp_path,
            "jd_markdown": None,
            "jd_data": None,
            "reflection_loop": 0,
            "judge_results": [],
        })
        reflection_loop = result.get("reflection_loop", 0)
        logger.info(f"Workflow complete. Reflection loops: {reflection_loop}")
    except Exception as e:
        logger.error(f"Workflow failed for '{file.filename}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)
        logger.debug(f"Temp file deleted: {tmp_path}")

    # Build response
    judge_results = result.get("judge_results") or []
    final_verdict = judge_results[-1] if judge_results else None
    logger.info(f"Final verdict for '{file.filename}': {final_verdict['grade'] if final_verdict else 'N/A'}")

    return JSONResponse(content={
        "jd_data": result["jd_data"].model_dump() if result.get("jd_data") else None,
        "judge_results": judge_results,
        "reflection_loop": reflection_loop,
        "verdict": final_verdict["grade"] if final_verdict else None,
    })
