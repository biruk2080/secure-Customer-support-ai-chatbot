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
- 📊 **Monitoring** — Real-time Splunk logging at every stage: security violations, routing decisions, and chatbot responses

---

## 🏗️ Architecture

