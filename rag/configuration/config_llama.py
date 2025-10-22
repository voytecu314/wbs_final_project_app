from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from rag.configuration.config_llm import get_llm

EMBED_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE: int = 1024
CHUNK_OVERLAP: int = 200


def configure_llamaindex():
    """Configure global LlamaIndex settings"""

    # LLM Configuration
    Settings.llm = get_llm()

    # Embedding Model
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL_NAME,
        cache_folder="rag/configuration/embedding_model_cache",
    )

    # Text Splitting
    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP

    # Alternative: using transformations
    Settings.transformations = [
        SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    ]
