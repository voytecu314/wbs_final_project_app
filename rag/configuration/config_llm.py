import os

from dotenv import load_dotenv
from llama_index.llms.groq import Groq

# Load environment variables from the .env file
load_dotenv()

LLM_MODEL: str = "llama-3.1-8b-instant"
LLM_TEMPERATURE: float = 0.01
LLM_SYSTEM_PROMPT: str = (
    "You are a helpful educational assistant. "
    "Provide clear and concise answers to the user's questions based "
    "on the provided context."
)


def get_llm() -> Groq:
    """Initialises the Groq LLM with core parameters from config."""

    groq_api_key: str | None = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Make sure it's set in your .env file."
        )

    return Groq(
        api_key=groq_api_key,
        model=LLM_MODEL,
        # The following parameters are optional and will default
        # to the model's defaults if not set
        temperature=LLM_TEMPERATURE,
    )
