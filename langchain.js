// docker run -p 8000:8000 -d --rm --name unstructured-api quay.io/unstructured-io/unstructured-api:latest --port 8000 --host 0.0.0.0
import { UnstructuredDirectoryLoader } from "langchain/document_loaders/fs/unstructured";

const options = {
  apiUrl: 'http://localhost:8000'
};

const loader = new UnstructuredDirectoryLoader(
  "./testfiles/",
  options
);

const docs = await loader.load();


// import { DirectoryLoader } from "langchain/document_loaders/fs/directory";
// import {
//   JSONLoader,
//   JSONLinesLoader,
// } from "langchain/document_loaders/fs/json";
// import { TextLoader } from "langchain/document_loaders/fs/text";
// import { CSVLoader } from "langchain/document_loaders/fs/csv";

// const loader = new DirectoryLoader(
//   "./testfiles",
//   {
//     ".json": (path) => new JSONLoader(path, "/texts"),
//     ".jsonl": (path) => new JSONLinesLoader(path, "/html"),
//     ".txt": (path) => new TextLoader(path),
//     ".md": (path) => new TextLoader(path),
//     ".csv": (path) => new CSVLoader(path, "text"),
//   }
// );
// const docs = await loader.load();

import { RecursiveCharacterTextSplitter } from "langchain/text_splitter"
import { MemoryVectorStore } from "langchain/vectorstores/memory";
// import { OpenAIEmbeddings } from "langchain/embeddings/openai";
import { OllamaEmbeddings } from "langchain/embeddings/ollama";
import { Ollama } from "langchain/llms/ollama";

const ollama = new Ollama({
  baseUrl: "http://localhost:11434",
  model: "llama2",
});


// Split the text into 500 character chunks. And overlap each chunk by 20 characters
const textSplitter = new RecursiveCharacterTextSplitter({
 chunkSize: 500,
 chunkOverlap: 20
});
const splitDocs = await textSplitter.splitDocuments(docs);

const embeddings = new OllamaEmbeddings({
  model: "assistant", // default value
  baseUrl: "http://localhost:11434", // default value
  requestOptions: {
    useMMap: true,
    numThread: 12,
    numGpu: 1,
  },
});
// Then use the TensorFlow Embedding to store these chunks in the datastore
const vectorStore = await MemoryVectorStore.fromDocuments(splitDocs, embeddings);

import { RetrievalQAChain } from "langchain/chains";

const retriever = vectorStore.asRetriever();
const chain = RetrievalQAChain.fromLLM(ollama, retriever);
const question = 'What and who can I play games with? Make it a table.'
const result = await chain.call({query: question});
console.log(result.text)
