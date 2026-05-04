# 🛡️ Secure AI Customer Support Chatbot

**AI-powered customer support chatbot** built with **LangChain**, **LangGraph**, **GPT-4**, and **RAG**, featuring intelligent **prompt routing**, a **multi-layer security system**, and real-time **monitoring via Splunk**.
User queries are classified by an LLM-powered router node and dispatched to one of three specialized handler nodes, each with its **own dedicated RAG pipeline**
---

## 🚀 Overview

This project demonstrates how to build and safely a real-world LLM application — combining advanced AI capabilities with enterprise-grade security and observability.

**Core pillars:**

- 🤖 **Intelligent Chatbot** — GPT-4 powered, answers customer queries with context-aware RAG
- 🔀 **Prompt Routing** — LangGraph routes each query to the appropriate node/handler
- 🛡️ **Security Layer** — Multi-layer prompt injection detection (regex + vector + LLM)
- 📊 **Monitoring** — Real-time Splunk logging at every stage: security violations, routing decisions, chatbot responses, and latency tracking

---

## 🏗️ Architecture

```
User Input
   │
   ▼
┌─────────────────────────────────┐
│        Security Layer           │
│  [1] Rule-Based Filter (Regex)  │
│  [2] Semantic Similarity(Chroma)│
│  [3] LLM Classifier (GPT-4)     │
└────────────┬────────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
  BLOCKED ⚠️     ALLOWED ✅
  (Logged to      │
   Splunk)        ▼
          ┌──────────────────────────────────┐
          │         LangGraph Agent          │
          │   ┌──────────────────────────┐   │
          │   │       Router Node        │   │
          │   │    llm_call_router()     │───┼──► Splunk (routing_decision)
          │   └───────────┬──────────────┘   │
          │               │ route_decision() │
          │       ┌───────┼────────┐         │
          │       ▼       ▼        ▼         │
          │  [product] [billing] [technical] │
          │   + RAG     + RAG     + RAG      │
          │       │       │        │         │
          │       └───────┴────────┘         │
          │                │ END             │
          └────────────────┼─────────────────┘
                           ▼
                   Chatbot Response
                           │
                           ▼
                 ┌──────────────────┐
                 │  Splunk Logging  │  ← response + metadata + latency logged
                 └──────────────────┘
```

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4 |
| Agent Framework | LangChain + LangGraph |
| Retrieval (RAG) | LangChain OpenAI embedding RAG pipeline + vector store | 
| Prompt Engineering | SystemMessage + HumanMessage 
| Prompt Routing | LangGraph conditional edges / node routing |
| Security – Rule-based | Regex pattern matching |
| Security – Semantic | Chroma vector similarity search |
| Security – LLM | GPT-4 classifier |
| Monitoring | Splunk (HEC logging) |
| UI | Gradio |


## 🔀 Prompt Routing (LangGraph)

User Query
    │
    ▼
┌─────────────┐
│ Router Node │  ← llm_call_router() classifies intent
└──────┬──────┘
       │
       │  route_decision()
  ┌────┴──────────┬──────────────┐
  ▼               ▼              ▼
[product]      [billing]    [technical]
  RAG            RAG            RAG
  │               │              │
  └───────────────┴──────────────┘
                  │
                 END

**Node responsibilities:**

| Node | Handles | RAG Knowledge Base |
|---|---|---|
| `router` | Classifies incoming query and despatch to correspondent Node.  
| `product` | Product questions — features, recommendations, availability | Product catalog & docs |
| `billing` | Billing questions — payments, invoices, subscriptions, refunds | Billing records & policies |
| `technical` | Technical support — troubleshooting, errors, configuration | Technical docs & FAQs |

Each node retrieves from its **own isolated vector store**, ensuring responses are grounded in the most relevant domain-specific knowledge without cross-domain noise.

## 🛡️ Security Architecture

Three defense layers run in sequence on every user input:

### Layer 1 — Rule-Based Detection (Regex)
Fast pattern matching against known injection signatures.

### Layer 2 — Semantic Similarity (Vector DB)
Embeds the user input and computes cosine similarity against a database of known attack vectors. Catches injections that bypass regex.

### Layer 3 — LLM Classifier (GPT-4)
For inputs that pass the first two layers, a GPT-4 classifier makes a final judgment on whether the intent is malicious.

---

## 📊 Monitoring & Observability (Splunk)

All events are logged to Splunk in real time covering **security violations**, **allowed requests**, **routing decisions**, **chatbot responses**, and **latency metrics**, giving complete visibility at every stage of the pipeline.

### Security Event Log

Captured whenever a request is blocked by any of the three guardrail layers:

| Field | Description |
|---|---|
| `timestamp` | Time of the request |
| `user_input` | Raw user message |
| `detection_layer` | Which layer blocked the request 
| `similarity_score` | Vector similarity score 
| `classifier_reasoning` | LLM explanation 


### Routing Decision and chatbot_response Log

Captured every time the router node classifies a query, dispatches node and response delivered to the user:

| Field | Description |
|---|---|
| `timestamp` | Time of the routing decision |
| `user_input` | Original user message |
| `routed_to` | Destination node, Which node handled the query (`product` / `billing` / `technical`) |
| `router_reasoning` | LLM explanation for the routing decision |
| `bot_response` | Final response text sent to the user |
| `retrieval_time` | Time taken for vector database retrieval (seconds) |
| `llm_response_time` | Time taken for LLM to generate response (seconds) |
| `route_time` | Time taken for routing decision (seconds) |
| `total_processing_time` | Total time for the entire pipeline (seconds) |

Together, these two log types give full end-to-end visibility across every stage of the pipeline — all queryable in Splunk:

| Event Type | When Logged | `blocked` |
|---|---|---|
| `security_violation` | Request passes all three security layers or blocked by a guardrail layer 
| `routing_decision` | Router classifies and dispatches the query 
| `chatbot_response` | Final response delivered to the user 

---

## 📚 RAG Pipelines

Each handler node has its own **isolated RAG pipeline** with a dedicated vector store, keeping domain knowledge separated for cleaner, more accurate retrieval:

```
                    ┌─────────────────────────────────────────┐
                    │             Shared Flow                  │
  User Query ──► Embed Query (text-embedding-ada-002)         │
                    └──────────────────┬──────────────────────┘
                                       │
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                         ▼
   ┌─────────────────┐    ┌─────────────────────┐   ┌─────────────────────┐
   │  Product Store  │    │   Billing Store     │   │  Technical Store    │
   │   (Chroma)      │              (Chroma)    │   │        (Chroma)     │
   │                 │    │                     │   │                     │
   │ • Product docs  │    │ • Billing policies  │   │ • Technical docs    │
   │ • Catalog       │    │ • Invoice records   │   │ • Troubleshooting   │
   │ • Feature specs │    │ • Subscription info │   │ • Config guides     │
   └────────┬────────┘    └──────────┬──────────┘   └──────────┬──────────┘
            │                        │                          │
            ▼                        ▼                          ▼
      Top-K Chunks             Top-K Chunks               Top-K Chunks
            │                        │                          │
            └────────────────────────┼──────────────────────────┘
                                     ▼
                          GPT-4 generates response
                          grounded in retrieved context
```

**Why separate vector stores?**

- Prevents cross-domain retrieval noise 
- Each store can be updated independently as knowledge evolves
- Enables domain-specific chunking and embedding strategies per node

---

## 🗂️ Project Structure

```
productChatBot/
│
├── Gradio.py        # Main chatbot + Gradio interface
├── guardrail.py      # Prompt injection detection (all 3 layers)
├── state.py          # Shared LangGraph state object
├── vector_db.py      # Embeddings + Chroma similarity search
├── test_cases.py     # Adversarial security test suite
├── requirements.txt  # Dependencies
|-- Splunk_logger.py. # send log data to Splunk 
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-username/secure-ai-chatbot.git
cd secure-ai-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the root directory:

```env
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional — Splunk monitoring
SPLUNK_TOKEN=your_splunk_hec_token
SPLUNK_URL=https://your-splunk-instance:8088
```

---

## ▶️ Running the Application

```bash
python Gradio.py
```

Gradio will launch a local web interface. To create a public shareable link:

```python


---

## 🚀 Future Improvements

- [ ] Expand RAG with a full product database
- [ ] Add user authentication and session tracking
- [ ] Deploy as REST API (FastAPI + Docker)
- [ ] Add rate limiting and anomaly detection
- [ ] Multi-turn memory with LangGraph persistence

---

## 💼 What This Project Demonstrates

| Skill Area | Implementation |
|---|---|
| 🤖 LLM Application Dev | LangChain + GPT-4 end-to-end pipeline |
| 🔀 Agent Orchestration | LangGraph state machine with prompt routing |
| 📚 RAG | Retrieval-augmented generation for grounded answers | Embeddings
| 🔐 AI Security Engineering | 3-layer prompt injection defense system |
| 📊 Monitoring & Observability | Splunk HEC integration with structured logging and latency tracking |
| 🧪 Adversarial Testing | Security test suite for attack detection coverage |
| 🏗️ System Design | Production-style architecture with separation of concerns |


## 📜 License

MIT License

Built as a real-world AI Security + Intelligent Chatbot system to demonstrate production-safe LLM applications.
---

## 👨‍💻 Author

Biruk Geletu 


---

