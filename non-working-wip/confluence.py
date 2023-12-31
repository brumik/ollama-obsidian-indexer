from llama_index.llms import Ollama
from os.path import exists
from llama_index import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    ServiceContext,
    set_global_service_context,
    get_response_synthesizer,
)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import SimilarityPostprocessor
from llama_index.prompts import PromptTemplate

import time
import pickle

time1 = time.perf_counter()

llm = Ollama(model="mistral", temperature=0.01)

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

service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model='local'
)

set_global_service_context(service_context)

from llama_hub.confluence import ConfluenceReader

base_url = "https://klara.atlassian.net/wiki"

# page_ids = ["945717249"]
# space_key = "~62e7f6f225abc07e51c5386f"
space_key = "KLARA"

def save_object(obj, filename):
  with open(filename, 'wb') as outp:  # Overwrites any existing file.
    pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)

if not exists(space_key + ".pkl"):
  reader = ConfluenceReader(base_url=base_url, cloud=True)
  nodes = reader.load_data(space_key=space_key, include_attachments=False, page_status="current")
  time2 = time.perf_counter()
  print(f"Downloaded the files in {time2 - time1:0.4f} seconds")
  save_object(nodes, space_key + '.pkl')
else:
  with open(space_key + '.pkl', 'rb') as inp:
    nodes = pickle.load(inp)  
    time2 = time.perf_counter()

if not exists("./storage"): 
  # load the documents and create the index
  index = VectorStoreIndex.from_documents(nodes)
  time3 = time.perf_counter()
  print(f"Indexed the files in {time3 - time2:0.4f} seconds")
 
  # store it for later
  index.storage_context.persist()
else:
    # load the existing index
  storage_context = StorageContext.from_defaults(persist_dir="./storage")
  index = load_index_from_storage(storage_context)


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

# query
try: 
  while True: 
    question = input ('>>> ')
    response = query_engine.query(question)
    print(response)
except EOFError:
  exit()