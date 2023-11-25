// Split the text into 500 character chunks. And overlap each chunk by 20 characters
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter"
import { DirectoryLoader } from "langchain/document_loaders/fs/directory";
import {
  JSONLoader,
  JSONLinesLoader,
} from "langchain/document_loaders/fs/json";
import { TextLoader } from "langchain/document_loaders/fs/text";
import { CSVLoader } from "langchain/document_loaders/fs/csv";
import { OllamaEmbeddings } from "langchain/embeddings/ollama";
import { FaissStore } from "langchain/vectorstores/faiss"

const loader = new DirectoryLoader(
  "./testfiles/MainVault",
  {
    ".json": (path) => new JSONLoader(path, "/texts"),
    ".jsonl": (path) => new JSONLinesLoader(path, "/html"),
    ".txt": (path) => new TextLoader(path),
    ".md": (path) => new TextLoader(path),
    ".csv": (path) => new CSVLoader(path, "text"),
  },
  true,
);

const docs = await loader.load();

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
const vectorStore = await FaissStore.fromDocuments(splitDocs, embeddings);
await vectorStore.save('./faiss');