# 🗣️ Voice PDF Bot

A local, privacy-first chatbot that can **answer questions from PDFs**, integrate with **Google Calendar**, and run fully offline using **Ollama (local LLMs)** and **FAISS** for fast document search. Powered by a **Flask backend**, served via **NGINX**, and containerized using **Docker**.

---

## 🚀 Features

- ✅ Ask questions about local PDF files
- ✅ Uses local LLMs via [Ollama](https://ollama.com)
- ✅ Fast vector search with FAISS
- ✅ Google Calendar integration
- ✅ Containerized with Docker + Docker Compose
- ✅ Reverse-proxied with NGINX
- 🛠️ Easy to extend and deploy

---

## 📁 Project Structure

```plaintext
voice_pdf_bot/
│
├── backend/                      # Flask app + backend logic
│   ├── __pycache__/              # Python cache
│   ├── backend/                  # Optional submodule structure
│   ├── faiss_index/              # Stores FAISS vector database
│   ├── google_creds/            # Google OAuth client secrets
│   ├── pdfs/                     # Folder to drop PDF files
│   ├── app.py                    # Flask app entry point
│   ├── pdf_qa_bot.py             # PDF parsing + QA logic
│   ├── google_calendar.py        # Google Calendar integration
│   └── client_secret_*.json      # Google API client secrets
│
├── frontend/
│   ├── index.html                # Optional web UI
│   └── nginx/
│       └── nginx.conf            # NGINX reverse proxy config
│
├── .dockerignore
├── .gitignore
├── Dockerfile                    # Docker build for backend
├── docker-compose.yml           # Compose file to run backend + nginx
├── requirements.txt              # Python dependencies
└── README.md                     # You're reading this :)
