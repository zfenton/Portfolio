from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Message, User
from ..schemas import MessageCreate, MessageResponse

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/{user_id}", response_model=MessageResponse)
def submit_message(user_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_message = db.query(Message).filter(Message.user_id == user_id).first()
    if existing_message:
        existing_message.message_text = message.message_text
        db.commit()
        db.refresh(existing_message)
        return existing_message

    db_message = Message(user_id=user_id, message_text=message.message_text)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/{user_id}", response_model=MessageResponse)
def get_user_message(user_id: int, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.user_id == user_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
