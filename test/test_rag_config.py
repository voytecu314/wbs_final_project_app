import os

import pytest
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

from rag.configuration.config_llama import configure_llamaindex
from rag.configuration.config_llm import get_llm


@pytest.fixture
def llm():
    return get_llm()


def test_api_key_is_set():
    """Test that GROQ_API_KEY is available in environment."""
    # This works in both local (via .env) and GH Actions (via secrets)
    api_key = os.getenv("GROQ_API_KEY")
    assert api_key is not None, "GROQ_API_KEY must be set"
    assert api_key != "", "GROQ_API_KEY cannot be empty"


def test_get_groq_llm(llm):
    """Test that get_llm() works with the configured API key."""
    assert type(llm).__name__ == "Groq"
    assert llm.api_key == os.getenv("GROQ_API_KEY")


def test_configure_llamaindex():
    """Test that configure_llamaindex sets the LLM correctly."""
    configure_llamaindex()
    assert isinstance(Settings.llm, Groq)
    assert isinstance(Settings.embed_model, HuggingFaceEmbedding)
    assert isinstance(Settings.transformations[0], SentenceSplitter)
