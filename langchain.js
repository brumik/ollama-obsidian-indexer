import { OllamaEmbeddings } from "langchain/embeddings/ollama";
import { Ollama } from "langchain/llms/ollama";
import { FaissStore } from "langchain/vectorstores/faiss"
import { RetrievalQAChain } from "langchain/chains";

const ollama = new Ollama({
  baseUrl: "http://localhost:11434",
  model: "llama2",
});

const template = (question) => `Use the following pieces of information to answer the user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Question: ${question}
Only return the helpful answer below and nothing else.
Helpful answer:
`;

const embeddings = new OllamaEmbeddings({
  model: "assistant", // default value
  baseUrl: "http://localhost:11434", // default value
  requestOptions: {
    useMMap: true,
    numThread: 12,
    numGpu: 1,
  },
});

const vectorStore = await FaissStore.load('./faiss', embeddings);


const retriever = vectorStore.asRetriever({
  k: 5
});
const chain = RetrievalQAChain.fromLLM(ollama, retriever);
const question = 'What and who can I play games with? Make it a table.'
const result = await chain.call({query: 'Who is Katherina?'});
console.log(result.text)
