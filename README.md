# 📖 Employee Handbook Q&A RAG System

An **n8n** workflow that turns your company's Employee Handbook into a chat-based Q&A assistant using Retrieval-Augmented Generation (RAG). Drop a PDF into a watched Google Drive folder, and employees can immediately start asking policy questions in chat — answered strictly from the handbook, with a clear fallback when the answer isn't there.

---

## ✨ What it does

- **Auto-ingests** a new Employee Handbook PDF the moment it's uploaded to a designated Google Drive folder.
- **Chunks and embeds** the handbook text and stores it in a Pinecone vector index.
- **Answers employee questions** via a chat-triggered AI agent that retrieves relevant handbook passages before responding.
- **Refuses to hallucinate** — if the handbook doesn't cover a question, the agent says so explicitly instead of making something up.

---

## 🏗️ Architecture

This workflow is composed of two independent pipelines that share one Pinecone index.

### 1. Document Ingestion Pipeline

```
Google Drive Trigger (new file in "FOR RAG" folder)
        │
        ▼
Download Handbook PDF
        │
        ▼
Extract Text from PDF
        │
        ▼
Split into Chunks (1,200 chars, 200 char overlap)
        │
        ▼
Format Chunks (pageContent + metadata)
        │
        ▼
Embed Chunks (Hugging Face — all-MiniLM-L6-v2)
        │
        ▼
Store in Pinecone (index: employee-handbook-rag)
```

### 2. Query & Answer Pipeline

```
Chat Trigger (employee sends a question)
        │
        ▼
Prepare Question
        │
        ▼
RAG Agent (LLM: OpenRouter)
        │
        ├── Tool: Retrieve Relevant Handbook Chunks (Pinecone similarity search)
        │             └── Embed Question (Hugging Face — all-MiniLM-L6-v2)
        │
        ▼
Answer returned to chat
```

---

## 🧩 Node Reference

### Ingestion pipeline

| Node | Type | Purpose |
|---|---|---|
| `New Handbook File` | Google Drive Trigger | Polls every minute for a `fileCreated` event in the watched folder. |
| `Download Employee Handbook PDF` | Google Drive | Downloads the PDF binary. |
| `Extract Handbook Text` | Extract From File | Extracts raw text from the PDF. |
| `Split Handbook into Chunks` | Code (JS) | Splits cleaned text into 1,200-char chunks with 200-char overlap. |
| `Format Chunks for Vector Store` | Code (JS) | Converts chunks to `{ pageContent, metadata }`. |
| `Generate Chunk Embeddings` | HF Inference Embeddings | Embeds chunks with `sentence-transformers/all-MiniLM-L6-v2`. |
| `Convert Chunks to Documents` | Document Default Data Loader | Wraps chunks as LangChain documents. |
| `Store Handbook Chunks in Pinecone` | Vector Store — Pinecone (`insert`) | Writes vectors to the `employee-handbook-rag` index. |

### Query pipeline

| Node | Type | Purpose |
|---|---|---|
| `Employee Question` | Chat Trigger | Webhook entry point for chat messages. |
| `Prepare User Question` | Set | Maps `chatInput` to a `question` field. |
| `RAG Agent` | LangChain Agent | Orchestrates retrieval + generation under a strict grounding prompt. |
| `OpenRouter Answer Generator` | LM Chat — OpenRouter | LLM backing the agent (`openrouter/free`). |
| `Retrieve Relevant Handbook Chunks` | Vector Store — Pinecone (`retrieve-as-tool`) | Exposed to the agent as a callable retrieval tool. |
| `Embed User Question` | HF Inference Embeddings | Embeds the question with the same model used at ingestion time. |

---

## 🤖 Agent Behavior

The `RAG Agent` runs under a fixed system prompt that enforces these rules:

1. Always query the handbook retrieval tool before answering.
2. Answer **only** from retrieved handbook content.
3. If the handbook doesn't clearly cover the question, respond with:
   > "I couldn't find a clear answer in the employee handbook."
4. Never invent policies, benefits, rules, or procedures.
5. Keep answers clear, concise, and practical.
6. Reference the relevant handbook section/chunk where possible.
7. Decline questions unrelated to the employee handbook.

---

## ⚙️ Prerequisites

- An [n8n](https://n8n.io/) instance (self-hosted or cloud) with LangChain nodes available.
- A **Google Drive** account with a folder to hold the handbook PDF.
- A **Pinecone** account and API key.
- A **Hugging Face** account with Inference API access.
- An **OpenRouter** account and API key.

---

## 🚀 Setup

1. **Create the Pinecone index**
   - Name: `employee-handbook-rag`
   - Dimensions: `384` (required for `all-MiniLM-L6-v2`)

2. **Import the workflow**
   - In n8n: `Workflows → Import from File` → select `Employee Handbook Q&A RAG System.json`.

3. **Connect credentials**
   - Google Drive OAuth2 API
   - Pinecone API
   - Hugging Face API
   - OpenRouter API

4. **Point the trigger at your Drive folder**
   - Update the `New Handbook File` node's watched folder to your own "FOR RAG" (or equivalent) folder.

5. **Upload the handbook**
   - Drop your Employee Handbook PDF into the watched folder. This kicks off the first indexing run.

6. **Activate the workflow**
   - The workflow ships **inactive** by default — toggle it on so both the Drive poller and the chat webhook go live.

7. **Test**
   - Ask a known-policy question (e.g., "How many paid leave days do I get?").
   - Ask an out-of-scope question to confirm the fallback message triggers correctly.

---

## 🔧 Configuration Reference

| Setting | Value |
|---|---|
| Watched Drive folder | `FOR RAG` |
| Poll interval | Every minute |
| Trigger event | `fileCreated` |
| Chunk size | 1,200 characters |
| Chunk overlap | 200 characters |
| Pinecone index | `employee-handbook-rag` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| LLM | `openrouter/free` |

> ⚠️ **Important:** The same embedding model must be used for both ingestion and query-time embedding. Mixing models will place vectors in incompatible spaces and silently break retrieval.

---

## ⚠️ Known Limitations

| Area | Limitation | Suggested Fix |
|---|---|---|
| Re-indexing | New uploads are appended, not replaced — old handbook versions stay in the index. | Add a delete-by-metadata step before inserting a revised handbook. |
| Model choice | `openrouter/free` has no availability/quality SLA. | Swap in a paid, production-grade model. |
| Chunking | Fixed character-based splitting ignores section/heading boundaries. | Use heading-aware or semantic chunking. |
| Polling | Every-minute Drive polling adds unnecessary API calls when idle. | Use a push-based Drive webhook, or lengthen the interval. |
| Access control | The chat webhook has no visible auth check. | Add token/credential verification before exposing it broadly. |

---

## 📁 Repo Contents

| File | Description |
|---|---|
| `Employee Handbook Q&A RAG System.json` | The exportable n8n workflow. |
| `README.md` | This file. |

---

## 📄 License

Add your license of choice here (e.g., MIT).
