# 🤖 Codebase Copilot

Codebase Copilot is an AI-powered developer assistant that can **understand, search, and explain any GitHub repository**.  
It clones a repo, builds semantic embeddings, retrieves the most relevant code, and uses an LLM to answer developer questions — all in real-time.

Think of it as **“ChatGPT for your codebase.”**  
Fast. Accurate. Developer-friendly.

---

## 🚀 Features

✔ Clone & index any GitHub repository  
✔ Chunk & embed source code  
✔ Semantic + keyword hybrid search  
✔ Fast streaming AI chat  
✔ Clean React UI with code viewer  
✔ Supports multiple LLM backends (Ollama)  
✔ Firebase Firestore logging  
✔ Fully local processing — privacy-safe  
✔ Persistent FAISS vector index  

---

## 🏗 Tech Stack

### 🔹 Frontend
- React (Vite)
- JavaScript
- axios
- react-syntax-highlighter
- react-icons
- prism-onedark theme

### 🔹 Backend
- Python
- FastAPI / Starlette server
- Requests
- FAISS (vector search)
- NumPy

### 🔹 Machine Intelligence
- Local LLM via **Ollama**
- Model (recommended):
  - `qwen2.5:1.5b`
- Embeddings:
  - Sentence-Transformers-based

### 🔹 Storage
- Firebase Firestore (for chat logs)
- Local FAISS index persistence

### 🔹 Dev Tools
- Git / GitHub
- Node.js
- Python venv

---
### 🔹Google tech used 

-- Firebase Firestore
-- Google IAM Auth
-- Google Cloud Platform
---
### Deployment
- **GitHub Pages / Netlify / Vercel**

---
## 👥 Team

### Team Name: Permission Debt

| Name | Role |
|-----|-----|
| S Akhileshwar | Full Stack Developer | 
|Y Haritha  | Presentation Designer  |
| D Sai Ram | QA ENgineer  |
| S Fareed | UI Designer  |
## 🧠 System Architecture

```text
            ┌──────────────────────┐
            │      Frontend        │
            │  React + Vite UI     │
            │                      │
            │  • Chat interface    │
            │  • File explorer     │
            │  • Code viewer       │
            └─────────┬────────────┘
                      │ REST API
                      ▼
            ┌──────────────────────┐
            │      Backend         │
            │      Python          │
            │                      │
            │ • clone repo         │
            │ • chunk code         │
            │ • embed text         │
            │ • FAISS search       │
            │ • rank + filter      │
            │ • send prompt        │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │     FAISS Index      │
            │  vector embeddings   │
            └──────────────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │       LLM            │
            │   (via Ollama)       │
            │  qwen2.5:1.5b        │
            └──────────────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │    Firebase Logs     │
            └──────────────────────┘
