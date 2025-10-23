# backend/app/db.py
from sqlmodel import SQLModel, create_engine, Session, select
from typing import Optional
from sqlmodel import Field
import datetime

sqlite_file_name = "sessions.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False, connect_args={"check_same_thread": False})

class SessionMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    role: str  # "user" or "agent" or "system"
    text: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    escalate: bool = False

def init_db():
    SQLModel.metadata.create_all(engine)

def save_message(session_id: str, role: str, text: str, escalate: bool=False):
    with Session(engine) as session:
        msg = SessionMessage(session_id=session_id, role=role, text=text, escalate=escalate)
        session.add(msg)
        session.commit()
        session.refresh(msg)
        return msg

def get_session_messages(session_id: str):
    with Session(engine) as session:
        stmt = select(SessionMessage).where(SessionMessage.session_id == session_id).order_by(SessionMessage.created_at)
        return session.exec(stmt).all()

def list_sessions(limit: int = 50):
    with Session(engine) as session:
        stmt = select(SessionMessage.session_id).distinct().limit(limit)
        rows = session.exec(stmt).all()
        return [r for r in rows]
