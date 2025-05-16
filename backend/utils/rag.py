from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    Settings
)
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

from . import llm

storage_context = None

embed_model = AzureOpenAIEmbedding(
    deployment_name="text-embedding-ada-002",
    model="text-embedding-ada-002",
    api_key=llm.api_key,
    azure_endpoint="https://hkust.azure-api.net",
    api_version="2024-06-01",
)

Settings.llm = AzureOpenAI(
    model="gpt-4o-mini",
    deployment_name="gpt-4o-mini",
    api_key=llm.api_key,
    azure_endpoint="https://hkust.azure-api.net",
    api_version="2024-06-01",
)
Settings.embed_model = embed_model

def persist_data():
    """
    Chunks and stores information in knowledge base
    """
    info = SimpleDirectoryReader("rag/info").load_data()
    index = VectorStoreIndex.from_documents(info)
    index.storage_context.persist(persist_dir="rag/storage")

def get_nodes(prompt: str, storage: StorageContext = storage_context):
    """
    Based on user prompt, retrieves nodes in the database to aid generation
    """
    if storage is None:
        return "[EMPTY]"
    index = load_index_from_storage(storage)
    retriever = index.as_retriever(retriever_mode="llm", similarity_top_k=10)
    nodes = retriever.retrieve(prompt)
    retrieved_info = "".join(nodes[i].text for i in range(len(nodes)))
    return retrieved_info