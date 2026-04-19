import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
try:
    from mistralai import Mistral
except ImportError:
    from mistralai.client import Mistral

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


def get_mistral_client() -> Mistral:
    return Mistral(api_key=MISTRAL_API_KEY)


def get_extraction_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="mistralai/ministral-14b-2512",
    )


def get_judge_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="microsoft/phi-4",
    )
