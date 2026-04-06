# \# What is GenAI

\- Generative AI is a type of artificial intelligence that creates new content such as text, images, music or code by learning patterns from existing data, mimicking human creativity.

\- AI <- ML <- DL <- GenAI



\# GenAI Impact Areas

\- Customer Support

\- Content Creation

\- Education

\- Software Development



\# Foundation Models (LLM, LMS)

\- A foundation model is a large-scale AI model trained on vast, typically unlabeled, data sets using self-supervision, designed to be adapted (fine-tuned) for a wide range of downstream tasks.



\# foundation models

&#x09;# user perspective (prompt engg, RAG, AI Agents, vector databases, fine tuning).

&#x09;# builder perspective (reinforcement learning with help of human feedback, pretraining, quantization, fine tuning).

&#x09;

# 

### Langchain



\# what is langchain

\- Langchain is an open source framework that helps in building LLM based applications. it provides modular components and end-to-end tools that help developers build complex AI applications, such as chatbots, question-answering systems, retrieval-augmented-generation, autonomous agents and more.



\# features

\- support all the major LLMs.

\- simplifies developing LLM based applications.

\- integrations available for all major tools.

\- open source/free/actively developed.

\- supports all major GenAI use cases.



\# Langchain Roadmap



1\. Fundamentals

\- what is langchain

\- langchain components

\- models

\- prompts

\- parsing output

\- runnables \& LCEL

\- chains

\- memory



2\. RAG

\- document loaders

\- text splitters 

\- embeddings

\- vector stores

\- retrieves

\- building a RAG applications



3\. Agents

\- tools \& toolkits

\- tool calling

\- building an AI agents



\# Benefits

* concept of chains
* model agnostic development
* complete ecosystem
* memory and state handling



\# what can we build?

* conversational chatbots
* AI Knowledge assistants
* AI Agents
* workflow automation
* summarization/research helpers




\# Langchain Components

---

* Models
- models are core interfaces through which you can interact with AI models.
- natural language understanding \& context aware text generation.
- by using langchain we can communicate with two types of models ***language \& embedding.***

* Prompts
- input given to the large language models.
- dynamic \& reusable prompts
- role based prompts
- few shot prompting 

* Chains
- a structured sequence of modular components such as prompts, language models and external tools-linked together to automate complex, multi step workflows.
- parallel chains
- condition based chains 

* Memory
- LLM API calls are stateless.
- ConversationBufferMemory: stores a transcript of recent messages. great for short chats but can grow large quickly.
- ConversationBufferWindowMemory: only keeps the last N interactions to avoid excessive token usage.
- Summarizer-Based Memory: periodically summarizes older chat segments to keep a condensed memory footprint.
- Custom Memory: for advanced use cases, we can store specialized state in a custom memory class.

* Indexes
- Indexes connect your application to external knowledge such as PDF, website or databases.
- This is a combination of Doc loader, Text splitter, Vector store, Retrievals.

* Agents
- An Agent is a system that uses a large language model as a reasoning engine to determine which actions to take and in what order. 

















































































