# 🧠 AI Customer Support Bot

An AI-powered customer support system that simulates real-world customer interactions using an LLM. It answers queries from a predefined FAQ dataset, remembers previous chat context, and triggers escalation when an answer is unavailable.

---

## 🚀 Features
- LLM-based response generation  
- Contextual conversation memory  
- Escalation simulation for unanswered queries  
- REST API endpoints (built with FastAPI)  
- Simple FAQ dataset for knowledge base  

---

## ⚙️ Tech Stack
- **FastAPI** (Backend)  
- **SQLite / In-memory storage** (Session tracking)  
- **OpenAI / Gemini API** (LLM integration)  

---

## 🧩 Setup & Run
```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ai-customer-support-bot.git
cd ai-customer-support-bot/backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
uvicorn main:app --reload
```

