# 🛡️ Secure AI Customer Support Chatbot

A production-grade **AI-powered customer support chatbot** built with **LangChain**, **LangGraph**, **GPT-4**, and **RAG**, featuring intelligent **prompt routing**, a **multi-layer security system**, and real-time **monitoring via Splunk**.

**AI-powered customer support chatbot** built with **LangChain**, **LangGraph**, **GPT-4**, and **RAG**, featuring intelligent **prompt routing**, a **multi-layer security system**, and real-time **monitoring via Splunk**.
User queries are classified by an LLM-powered router node and dispatched to one of three specialized handler nodes, each with its **own dedicated RAG pipeline**
---

## 🚀 Overview
@@ -26,7 +26,7 @@ User Input
┌─────────────────────────────────┐
│        Security Layer           │
│  [1] Rule-Based Filter (Regex)  │
│  [2] Semantic Similarity (FAISS)│
│  [2] Semantic Similarity(Chroma)│
│  [3] LLM Classifier (GPT-4)     │
└────────────┬────────────────────┘
             │
@@ -68,20 +68,17 @@ User Input
| LLM | OpenAI GPT-4 |
| Agent Framework | LangChain + LangGraph |
| Retrieval (RAG) | LangChain OpenAI embedding RAG pipeline + vector store | 
| Prompt Engineering | SystemMessage + HumanMessage 
| Prompt Routing | LangGraph conditional edges / node routing |
| Security – Rule-based | Regex pattern matching |
| Security – Semantic | FAISS vector similarity search |
| Security – Semantic | Chroma vector similarity search |
| Security – LLM | GPT-4 classifier |
| Monitoring | Splunk (HEC logging) |
| UI | Gradio |

---

## 🔀 Prompt Routing (LangGraph)

User queries are classified by an LLM-powered router node and dispatched to one of three specialized handler nodes, each with its **own dedicated RAG pipeline**:

```
User Query
    │
    ▼
@@ -98,30 +95,27 @@ User Query
  └───────────────┴──────────────┘
                  │
                 END
```

**Node responsibilities:**

| Node | Handles | RAG Knowledge Base |
|---|---|---|
| `router` | Classifies incoming query intent via `llm_call_router()` | — |
| `router` | Classifies incoming query and despatch to correspondent Node.  
| `product` | Product questions — features, recommendations, availability | Product catalog & docs |
| `billing` | Billing questions — payments, invoices, subscriptions, refunds | Billing records & policies |
| `technical` | Technical support — troubleshooting, errors, configuration | Technical docs & FAQs |

Each node retrieves from its **own isolated vector store**, ensuring responses are grounded in the most relevant domain-specific knowledge without cross-domain noise.

---

## 🛡️ Security Architecture

Three defense layers run in sequence on every user input:

### Layer 1 — Rule-Based Detection (Regex)
Fast, lightweight pattern matching against known injection signatures.
Fast pattern matching against known injection signatures.

### Layer 2 — Semantic Similarity (Vector DB)
Embeds the user input and computes cosine similarity against a database of known attack vectors. Catches paraphrased or obfuscated injections that bypass regex.
Embeds the user input and computes cosine similarity against a database of known attack vectors. Catches injections that bypass regex.

### Layer 3 — LLM Classifier (GPT-4)
For inputs that pass the first two layers, a GPT-4 classifier makes a final judgment on whether the intent is malicious.
@@ -130,7 +124,7 @@ For inputs that pass the first two layers, a GPT-4 classifier makes a final judg

## 📊 Monitoring & Observability (Splunk)

All events are logged to Splunk in real time via HTTP Event Collector (HEC) — covering **security violations**, **allowed requests**, **routing decisions**, and **chatbot responses**, giving complete visibility at every stage of the pipeline.
All events are logged to Splunk in real time covering **security violations**, **allowed requests**, **routing decisions**, and **chatbot responses**, giving complete visibility at every stage of the pipeline.

### Security Event Log

@@ -140,54 +134,30 @@ Captured whenever a request is blocked by any of the three guardrail layers:
|---|---|
| `timestamp` | Time of the request |
| `user_input` | Raw user message |
| `detection_layer` | Which layer blocked the request (`regex` / `vector` / `llm`) |
| `similarity_score` | Vector similarity score (Layer 2) |
| `blocked` | `true` |
| `classifier_reasoning` | LLM explanation (Layer 3) |

### Allowed Request Log

Captured whenever a request passes all three security layers and is cleared to proceed to the LangGraph agent:
| `detection_layer` | Which layer blocked the request 
| `similarity_score` | Vector similarity score 
| `classifier_reasoning` | LLM explanation 

| Field | Description |
|---|---|
| `timestamp` | Time the request was cleared |
| `user_input` | Raw user message |
| `blocked` | `false` |
| `layers_passed` | Confirmation all three layers passed (`regex`, `vector`, `llm`) |

### Routing Decision Log
### Routing Decision and chatbot_response Log

Captured every time the router node classifies a query and dispatches it to a node:
Captured every time the router node classifies a query, dispatches node and response delivered to the user:

| Field | Description |
|---|---|
| `timestamp` | Time of the routing decision |
| `user_input` | Original user message |
| `routed_to` | Destination node (`product` / `billing` / `technical`) |
| `routed_to` | Destination node, Which node handled the query (`product` / `billing` / `technical`) |
| `router_reasoning` | LLM explanation for the routing decision |

### Chatbot Response Log

Captured for every successful response delivered to the user:

| Field | Description |
|---|---|
| `timestamp` | Time of the response |
| `user_input` | Original user message |
| `routed_to` | Which node handled the query (`product` / `billing` / `technical`) |
| `bot_response` | Final response text sent to the user |
| `blocked` | `false` |


Together, these four log types give full end-to-end visibility across every stage of the pipeline — all queryable in Splunk:
Together, these two log types give full end-to-end visibility across every stage of the pipeline — all queryable in Splunk:

| Event Type | When Logged | `blocked` |
|---|---|---|
| `security_violation` | Request blocked by a guardrail layer | `true` |
| `allowed_request` | Request passes all three security layers | `false` |
| `routing_decision` | Router classifies and dispatches the query | — |
| `chatbot_response` | Final response delivered to the user | `false` |
| `security_violation` | Request passes all three security layers or blocked by a guardrail layer 
| `routing_decision` | Router classifies and dispatches the query 
| `chatbot_response` | Final response delivered to the user 

---

@@ -205,7 +175,7 @@ Each handler node has its own **isolated RAG pipeline** with a dedicated vector
              ▼                        ▼                         ▼
   ┌─────────────────┐    ┌─────────────────────┐   ┌─────────────────────┐
   │  Product Store  │    │   Billing Store     │   │  Technical Store    │
   │  (FAISS/Chroma) │    │   (FAISS/Chroma)    │   │  (FAISS/Chroma)     │
   │   (Chroma)      │              (Chroma)    │   │        (Chroma)     │
   │                 │    │                     │   │                     │
   │ • Product docs  │    │ • Billing policies  │   │ • Technical docs    │
   │ • Catalog       │    │ • Invoice records   │   │ • Troubleshooting   │
@@ -299,17 +269,13 @@ Gradio will launch a local web interface. To create a public shareable link:

---




## 🚀 Future Improvements

- [ ] Expand RAG with a full product database
- [ ] Add user authentication and session tracking
- [ ] Deploy as REST API (FastAPI + Docker)
- [ ] Add rate limiting and anomaly detection
- [ ] Multi-turn memory with LangGraph persistence
- [ ] Fine-tune injection classifier for domain-specific attacks

---
