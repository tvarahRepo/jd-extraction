from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from config import get_judge_llm
from judge_pydantic_models import judgeJson


judge_system_prompt = SystemMessagePromptTemplate.from_template(
    """
    ### ROLE
    You are a strict QA Auditor for a JD Parsing pipeline.
    Your job is to compare the SOURCE_TEXT (Markdown) with the EXTRACTED_JSON.

    ### TASK
    Verify the JSON against the text for three specific errors:
    1. **Hallucinations:** Did the JSON invent a skill or requirement not present in the text?
    2. **Misclassification:** Were mandatory skills placed in optional or vice versa?
    3. **Missing Critical Data:** Did the JSON return 'null' for a role title or mandatory skill that is clearly visible in the text?

    ### OUTPUT FORMAT
    Return valid JSON with two fields:
    - "grade": "PASS" or "FAIL"
    - "grade_summary": "Short explanation of the error (if FAIL), otherwise 'looks good'. in about a single line (100 words)"

    ### CONSTRAINTS
    - Ignore minor formatting differences (e.g., "React.js" vs "React" is acceptable).
    - Be strict about mandatory vs optional skill classification.
    """
)

human_prompt_judge = HumanMessagePromptTemplate.from_template(
    """
    Here is the markdown extraction:
    <markdown>
    {markdown}
    </markdown>

    Here is the Json extraction:
    <jsondata>
    {jsondata}
    </jsondata>
    """
)

prompt_template_judge = ChatPromptTemplate.from_messages(
    [judge_system_prompt, human_prompt_judge]
)


def get_judge_chain():
    llm = get_judge_llm()
    return prompt_template_judge | llm.with_structured_output(judgeJson)
