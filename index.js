import {
  VectorStoreIndex,
  serviceContextFromDefaults,
  storageContextFromDefaults,
  SimpleDirectoryReader,
} from "llamaindex";
import { Ollama } from 'ollama-node';
import fs from 'fs';
const question = 'What does Katherina likes?'; 

const service_context = serviceContextFromDefaults({ chunkSize: 256, embedModel: 'local', llm: "llama2" })
const storage_context = await storageContextFromDefaults({ persistDir: "./storage" });

const testFolder = './testfiles/';

const mdreader = new SimpleDirectoryReader();
const thedoc = await mdreader.loadData({ directoryPath: testFolder });

await VectorStoreIndex.fromDocuments(thedoc, { 
  storageContext: storage_context,
  serviceContext: service_context
});

console.log('indexed', mdpath);


const index = await VectorStoreIndex.init({ storageContext: storage_context });
const ret = index.asRetriever();
ret.similarityTopK = 5
const prompt = question;
const response = await ret.retrieve(prompt);
const systemPrompt = `Use the following text to help come up with an answer to the prompt: 
  ${response.map(r => r.node.toJSON().text).join(" - ")}
`

console.log('system prompt', systemPrompt);

const ollama = new Ollama();
ollama.setModel("llama2");
ollama.setSystemPrompt(systemPrompt);
const genout = await ollama.generate(prompt);
console.log(genout);