from fastapi import FastAPI, Depends, HTTPException
from backend.database import Base, engine, get_db
from backend import models
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal
from fastapi.responses import StreamingResponse
from backend.database import Base, engine, get_db, SessionLocal
from backend.services.gemini import stream_response
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI(
    title="Ask Buddy API",
    description="Backend API for Ask Buddy AI Chatbot",
    version="1.0.0"
)


# Frontend directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# Serve frontend assets
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)



# Create database tables
Base.metadata.create_all(bind=engine)


DEFAULT_TITLE = "Ask Buddy Chat"


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Request schema
class ConversationCreate(BaseModel):
    title: str | None = None


# 1. Create a new conversation
@app.post("/conversations/")
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db)
):
    conversation = models.Conversation(title=data.title)

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at
    }


# 2. Get all conversations (newest first)
@app.get("/conversations/")
def get_conversations(db: Session = Depends(get_db)):
    conversations = (
        db.query(models.Conversation)
        .order_by(models.Conversation.id.desc())
        .all()
    )

    return conversations


# 3. Get a specific conversation
@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content
            }
            for message in conversation.messages
        ]
    }


# 4. Delete a conversation (and its messages via cascade)
@app.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Use db.delete() so cascade="all, delete-orphan" removes the messages too
    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted"}


# Message request schema
class MessageCreate(BaseModel):
    role: Literal["user", "assistant"]
    content: str


# Create a new message
@app.post("/conversations/{conversation_id}/messages/")
def create_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    # Check whether conversation exists
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Create message
    message = models.Message(
        conversation_id=conversation_id,
        role=data.role,
        content=data.content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at
    }


# Chat request schema
class ChatRequest(BaseModel):
    conversation_id: int
    message: str



# Chat API - Streaming Agent Response
@app.post("/chat/")
def chat(
    data: ChatRequest,
    db: Session = Depends(get_db)
):

    # Check conversation
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == data.conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # Auto-title
    if not conversation.title or conversation.title == DEFAULT_TITLE:

        new_title = data.message.strip()[:40]

        if len(data.message.strip()) > 40:
            new_title += "..."

        conversation.title = new_title

    # Save user message
    user_message = models.Message(
        conversation_id=data.conversation_id,
        role="user",
        content=data.message
    )

    db.add(user_message)
    db.commit()

    # Load conversation history
    stored_messages = (
        db.query(models.Message)
        .filter(
            models.Message.conversation_id == data.conversation_id
        )
        .order_by(models.Message.id.asc())
        .all()
    )

    history = [
        {"role": m.role, "content": m.content}
        for m in stored_messages[-20:]
    ]

    # Stream AI response
    def generate():

        full_response = ""

        try:

            for chunk in stream_response(
                history,
                data.conversation_id
            ):

                full_response += chunk
                yield chunk

            # Save completed AI response
            if full_response:

                stream_db = SessionLocal()

                try:

                    assistant_message = models.Message(
                        conversation_id=data.conversation_id,
                        role="assistant",
                        content=full_response
                    )

                    stream_db.add(assistant_message)
                    stream_db.commit()

                finally:
                    stream_db.close()

        except Exception as e:

            print(f"AI Agent Error: {e}")

            yield "\n\nSorry, something went wrong while generating the response."

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
