from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models import Activity, ActivityOption, Vote, Message, User
from ..schemas import ActivityResultResponse, VoteCount, MessageResponse

router = APIRouter(prefix="/api/anniversary-celebration-results", tags=["admin"])


@router.get("/activities", response_model=List[ActivityResultResponse])
def get_all_results(db: Session = Depends(get_db)):
    activities = db.query(Activity).filter(Activity.is_active == True).order_by(Activity.order).all()

    results = []
    for activity in activities:
        vote_counts = db.query(
            ActivityOption.id,
            ActivityOption.option_text,
            func.count(Vote.id).label('vote_count')
        ).outerjoin(
            Vote,
            (Vote.option_id == ActivityOption.id) & (Vote.activity_id == activity.id)
        ).filter(
            ActivityOption.activity_id == activity.id
        ).group_by(
            ActivityOption.id,
            ActivityOption.option_text
        ).order_by(
            ActivityOption.order
        ).all()

        vote_count_list = [
            VoteCount(option_id=vc[0], option_text=vc[1], vote_count=vc[2])
            for vc in vote_counts
        ]

        total_votes = sum(vc.vote_count for vc in vote_count_list)

        results.append(
            ActivityResultResponse(
                activity_id=activity.id,
                question=activity.question,
                order=activity.order,
                vote_counts=vote_count_list,
                total_votes=total_votes
            )
        )

    return results


@router.get("/messages", response_model=List[MessageResponse])
def get_all_messages(db: Session = Depends(get_db)):
    messages = db.query(Message).order_by(Message.created_at.desc()).all()
    return messages


@router.post("/reset")
def reset_users_and_votes(db: Session = Depends(get_db)):
    deleted_votes = db.query(Vote).delete()
    deleted_messages = db.query(Message).delete()
    deleted_users = db.query(User).delete()
    db.commit()
    return {
        "message": "Reset complete. Activities and options preserved.",
        "deleted_users": deleted_users,
        "deleted_votes": deleted_votes,
        "deleted_messages": deleted_messages,
    }
