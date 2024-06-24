from fsspec.core import os
from os.path import exists, join
from llama_index.core import (
    VectorStoreIndex,
    get_response_synthesizer,
    PromptTemplate,
    StorageContext,
    load_index_from_storage,
    SimpleDirectoryReader,
    Settings,
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.ollama import Ollama

# from llama_index.core.postprocessor import SimilarityPostprocessor

# Set up the recommended template for mistral query
prompt_template = """
<s>[INST]
You are a helpful assistant, you will use the provided context to
answer user questions. Read the given context before answering questions
and think step by step. If you can not answer a user question based on
the provided context, inform the user. Do not use any other information
for answering user. Provide a detailed answer to the question.

Context: {context_str}
User: {query_str}
[/INST]
"""

base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model = os.getenv("LLM_MODEL", "mistral")
temperature = float(os.getenv("LLM_TEMPERATURE", 0.1))
prompt_template = os.getenv("LLM_PROMPT_TEMPLATE", prompt_template)
persist_dir = os.getenv("INDEXES_PERSIST_DIR", "./storage")
embed_model_name = os.getenv("OLLAMA_EMBED_MODEL_NAME", "mxbai-embed-large")

ollama_embedding = OllamaEmbedding(
    model_name=embed_model_name,
    base_url=base_url,
    ollama_additional_kwargs={"mirostat": 0},
)

# Set up the llm
Settings.llm = Ollama(base_url=base_url, model=model, temperature=temperature)

prompt = PromptTemplate(template=prompt_template)

# Set up service context with our local llm and embedding
Settings.embed_model = ollama_embedding

# Set up a global index so we do not need to read from memory all the time
index: VectorStoreIndex = None


# Indexer helper
def nodes_to_vector(nodes):
    global index

    if not exists(join(persist_dir, "index_store.json")):
        index = VectorStoreIndex.from_documents(nodes)
        index.storage_context.persist(persist_dir=persist_dir)
        return "Vector created"

    # Now we are sure that we have a dir and files
    storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    index = load_index_from_storage(storage_context)
    refreshed = index.refresh_ref_docs(
        nodes,
        # update_kwargs={"delete_kwargs": {"delete_from_docstore": True}}
    )

    if any(refreshed):
        index.storage_context.persist()

    return sum(refreshed)


def ensure_index_exists():
    global index
    if not index:
        nodes_to_vector([])


# File reader helper:
def directory_reader_setup(is_dir, path):
    required_ext = [".md"]
    if is_dir:
        return SimpleDirectoryReader(
            input_dir=path,
            recursive=True,
            filename_as_id=True,
            required_exts=required_ext,
        )
    else:
        return SimpleDirectoryReader(
            input_files=[path], filename_as_id=True, required_exts=required_ext
        )


def index_dir(dir_path):
    if any(fname.endswith(".md") for fname in os.listdir(dir_path)):
        parser = directory_reader_setup(True, dir_path)
        return nodes_to_vector(parser.load_data())
    else:
        # No markdown files in the directory
        return -1


def index_file(file_path):
    parser = directory_reader_setup(False, file_path)
    return nodes_to_vector(parser.load_data())


def delete_index(file_path):
    global index
    ensure_index_exists()

    # Get from path all the part (look like: filepath_part_0)
    d = {
        k: v
        for k, v in index.ref_doc_info.items()
        if v.metadata["file_path"] == file_path
    }

    for key in d:
        index.delete_ref_doc(key, delete_from_docstore=True)

    index.storage_context.persist()


def query(query):
    global index
    ensure_index_exists()

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5,
    )

    response_synthesizer = get_response_synthesizer(
        text_qa_template=prompt,
    )

    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer,
        # node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
    )

    response = query_engine.query(query)
    return response.response
