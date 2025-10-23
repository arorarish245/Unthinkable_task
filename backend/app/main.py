# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import ChatRequest, ChatResponse, FAQItem
from .db import init_db, save_message, get_session_messages, list_sessions
import json, os
from . import llm_client
from typing import List
from pathlib import Path

app = FastAPI(title="AI Customer Support Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# load FAQs
BASE = Path(__file__).resolve().parent
FAQ_FILE = BASE / "faqs.json"
with open(FAQ_FILE) as f:
    FAQS = json.load(f)

# init DB
init_db()

SYSTEM_PROMPT = (
    "You are a helpful customer support assistant. Use the FAQ when possible and be concise. "
    "If you cannot confidently answer, respond with 'I don't know, escalate' or similar."
)

def find_faq_match(user_text: str, top_k: int = 1):
    """
    Simple exact/keyword match fallback.
    For production, replace with embeddings + cosine similarity.
    Returns matched faq or None.
    """
    text = user_text.lower()
    # exact keyword match
    for faq in FAQS:
        if faq["question"].lower() in text or any(word in text for word in faq["question"].lower().split()):
            return faq
    # fallback: check keywords
    keywords = ["password", "refund", "refunds", "contact", "support", "order", "shipping"]
    for k in keywords:
        if k in text:
            for faq in FAQS:
                if k in faq["question"].lower() or k in faq.get("tags", []):
                    return faq
    return None

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Basic validation
    if not req.session_id:
        raise HTTPException(status_code=400, detail="session_id required")

    # Save user message
    save_message(req.session_id, "user", req.message)

    # Try to find an FAQ match first
    faq = find_faq_match(req.message)
    if faq:
        reply = faq["answer"]
        save_message(req.session_id, "agent", reply, escalate=False)
        return ChatResponse(reply=reply, escalate=False, suggestions=None)

    # No direct FAQ. Ask LLM for an answer.
    # Build minimal conversation history for LLM
    history = []
    msgs = get_session_messages(req.session_id)
    for m in msgs[-10:]:
        history.append({"role": m.role if m.role in ("user","assistant") else "system", "content": m.text})

    # choose client
    if os.getenv("OPENAI_API_KEY"):
        reply = llm_client.generate_reply_openai(SYSTEM_PROMPT, history, req.message)
    else:
        reply = llm_client.generate_reply_placeholder(SYSTEM_PROMPT, history, req.message)

    # Simple escalation heuristic:
    # if reply includes "I don't know" or is very short, escalate
    escalate = False
    low_confidence_phrases = ["i don't know", "i'm not sure", "cannot", "unable to", "sorry —"]
    if any(p in reply.lower() for p in low_confidence_phrases) or len(reply.split()) < 6:
        escalate = True
        # simulated escalation text
        esc_text = f"Escalation needed for session {req.session_id}. User: {req.message}"
        save_message(req.session_id, "agent", reply, escalate=True)
        save_message(req.session_id, "system", esc_text, escalate=True)
    else:
        save_message(req.session_id, "agent", reply, escalate=False)

    return ChatResponse(reply=reply, escalate=escalate, suggestions=None)

@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    msgs = get_session_messages(session_id)
    return {"session_id": session_id, "messages": [m.dict() for m in msgs]}

@app.get("/sessions")
def get_sessions():
    return {"sessions": list_sessions()}

@app.get("/faqs", response_model=List[FAQItem])
def get_faqs():
    return FAQS
