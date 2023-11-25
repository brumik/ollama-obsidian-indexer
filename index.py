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

testFolder = './testfiles/';

llm = Ollama(model="mistral", temperature=0.1)

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

parser = SimpleDirectoryReader(input_dir=testFolder, recursive=True, filename_as_id=True, required_exts=['.md'])
md_nodes = parser.load_data() 

if not exists("./storage"):
  index = VectorStoreIndex.from_documents(md_nodes)
  index.storage_context.persist()
else:
  storage_context = StorageContext.from_defaults(persist_dir="./storage")
  index = load_index_from_storage(storage_context)
  refreshed = index.refresh(md_nodes, update_kwargs={"delete_kwargs": {"delete_from_docstore": True}})
  if (any(refreshed)):
    index.storage_context.persist()

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