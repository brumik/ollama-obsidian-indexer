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


testFolder = './testfiles/';
question = 'What does Katherina likes?'; 
llm = Ollama(model="llama2")
service_context = ServiceContext.from_defaults(
  llm=llm,
  chunk_size=256,
  embed_model='local'
)
set_global_service_context(service_context)

parser = SimpleDirectoryReader(input_dir=testFolder)
# check if storage already exists
if not exists("./storage"):
  md_nodes = parser.load_data() 
  # load the documents and create the index
  index = VectorStoreIndex.from_documents(md_nodes)
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
response_synthesizer = get_response_synthesizer()

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.5)],
)

# query
response = query_engine.query(question)
print(response)