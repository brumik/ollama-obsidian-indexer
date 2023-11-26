from llama_index.llms import Ollama
from os.path import exists
from llama_index import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
    SimpleDirectoryReader,
    set_global_service_context,
    get_response_synthesizer,
)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import SimilarityPostprocessor
from llama_index.prompts import PromptTemplate


## Set default values for the methods

# Set up the llm from local mistral
llm = Ollama(model="mistral", temperature=0.1)

# Set up the recommended template for mistral query
prompt_template="""
<s>[INST]
You are a helpful assistant, you will use the provided context to answer user questions.
Read the given context before answering questions and think step by step. If you can not answer a user question based on 
the provided context, inform the user. Do not use any other information for answering user. Provide a detailed answer to the question.

Context: {context_str}
User: {query_str}
[/INST]
"""
prompt = PromptTemplate(template=prompt_template)

# Set up service context with our local llm and embedding
service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model='local'
)
set_global_service_context(service_context)

# Set up where to save the index store
persist_dir='./storage'

# Set up a global index so we do not need to read from memory all the time
index = None

# Indexer helper
def nodes_to_vector(nodes):
  global index

  if not exists(persist_dir): 
    index = VectorStoreIndex.from_documents([])
    index.storage_context.persist(persist_dir=persist_dir)

  # Now we are sure that we have a dir and files
  storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
  index = load_index_from_storage(storage_context)
  refreshed = index.refresh_ref_docs(nodes, update_kwargs={"delete_kwargs": {"delete_from_docstore": True}})

  if (any(refreshed)):
    index.storage_context.persist()
  
  return sum(refreshed)

def ensure_index_exists():
  global index
  if not index:
    if not exists(persist_dir):
      nodes_to_vector([])
    else:
      storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
      index = load_index_from_storage(storage_context)


# File reader helper:
def directory_reader_setup(is_dir, path):
  required_ext = ['.md']
  if (is_dir):
    return SimpleDirectoryReader(input_dir=path, recursive=True, filename_as_id=True, required_exts=required_ext)
  else:
    return SimpleDirectoryReader(input_files=[path], filename_as_id=True, required_exts=required_ext)

def index_dir(dir_path):
  parser = directory_reader_setup(True, dir_path)
  return nodes_to_vector(parser.load_data())

def index_file(file_path):
  parser = directory_reader_setup(False, file_path)
  return nodes_to_vector(parser.load_data())

def delete_index(file_path):
  global index
  ensure_index_exists()

  # Get from path all the part (look like: filepath_part_0)
  d = {k: v for k, v in index.ref_doc_info.items() if v.metadata['file_path'] == file_path}

  for key in d:
    index.delete_ref_doc(key, delete_from_docstore = True)

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
      node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
  )

  response = query_engine.query(query)
  return response.response