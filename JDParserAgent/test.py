import json
import os

os.chdir(os.path.dirname(__file__))

import sys
sys.path.insert(0, os.path.dirname(__file__))

from workflow import build_graph

# --- Edit this path before running ---
JD_FILE_PATH = r"../data/Job Description/Data Science/sample_jd.pdf"
# -------------------------------------


def run():
    graph = build_graph()

    result = graph.invoke({
        "jd_file_path": JD_FILE_PATH,
        "jd_markdown": None,
        "jd_data": None,
        "reflection_loop": 0,
        "judge_results": [],
    })

    output = {
        "jd_data": result["jd_data"].model_dump() if result.get("jd_data") else None,
        "judge_results": result.get("judge_results", []),
        "reflection_loop": result.get("reflection_loop", 0),
    }

    print(json.dumps(output, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    run()
