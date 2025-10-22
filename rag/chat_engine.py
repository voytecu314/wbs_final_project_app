from pathlib import Path

from llama_index.core import (
    Document,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.memory import Memory

from rag.configuration.config_llama import configure_llamaindex
from rag.configuration.config_llm import LLM_SYSTEM_PROMPT

vector_store_path: Path = Path(__file__).parent / "vector_store"


def create_chat_engine() -> VectorStoreIndex:
    """Creates a chat engine using LlamaIndex with configured settings."""

    # Configure LlamaIndex with global settings
    configure_llamaindex()
    if vector_store_path.exists():
        # Load existing index from disk
        storage_context: StorageContext = StorageContext.from_defaults(
            persist_dir=str(vector_store_path)
        )
        index: VectorStoreIndex = load_index_from_storage(storage_context)
    else:
        # Load documents from the specified directory
        documents: list[Document] = SimpleDirectoryReader("rag/documents").load_data()

        # Create a VectorStoreIndex with the documents
        index = VectorStoreIndex.from_documents(documents)

        # Persist the index to disk for future use
        index.storage_context.persist(persist_dir=str(vector_store_path))

    # Set up memory for chat history
    memory = Memory.from_defaults(
        session_id="my_session",
        token_limit=20000,
        token_flush_size=510,
        chat_history_token_ratio=0.7,
    )

    chat_engine = index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=LLM_SYSTEM_PROMPT,
        similarity_top_k=4,
    )

    return chat_engine
