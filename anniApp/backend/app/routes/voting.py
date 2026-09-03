from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Activity, ActivityOption, Vote, User, AppConfig
from ..schemas import ActivityResponse, VoteCreate, VoteResponse, VotingStatus

router = APIRouter(prefix="/api/voting", tags=["voting"])


def check_voting_open(db: Session) -> bool:
    config = db.query(AppConfig).first()
    if not config:
        return True

    if config.is_voting_closed:
        return False

    if config.voting_end_time and datetime.now() >= config.voting_end_time:
        return False

    return True


@router.get("/status", response_model=VotingStatus)
def get_voting_status(db: Session = Depends(get_db)):
    config = db.query(AppConfig).first()
    if not config:
        return VotingStatus(is_voting_open=True, voting_end_time=None)

    is_open = check_voting_open(db)
    return VotingStatus(
        is_voting_open=is_open,
        voting_end_time=config.voting_end_time
    )


@router.get("/activities", response_model=List[ActivityResponse])
def get_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).filter(Activity.is_active == True).order_by(Activity.order).all()
    return activities


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@router.post("/vote/{user_id}", response_model=VoteResponse)
def submit_vote(user_id: int, vote: VoteCreate, db: Session = Depends(get_db)):
    if not check_voting_open(db):
        raise HTTPException(status_code=403, detail="Voting is closed")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    activity = db.query(Activity).filter(Activity.id == vote.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    option = db.query(ActivityOption).filter(
        ActivityOption.id == vote.option_id,
        ActivityOption.activity_id == vote.activity_id
    ).first()
    if not option:
        raise HTTPException(status_code=404, detail="Invalid option for this activity")

    existing_vote = db.query(Vote).filter(
        Vote.user_id == user_id,
        Vote.activity_id == vote.activity_id
    ).first()

    if existing_vote:
        existing_vote.option_id = vote.option_id
        db.commit()
        db.refresh(existing_vote)
        return existing_vote

    db_vote = Vote(
        user_id=user_id,
        activity_id=vote.activity_id,
        option_id=vote.option_id
    )
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote


@router.get("/user-votes/{user_id}", response_model=List[VoteResponse])
def get_user_votes(user_id: int, db: Session = Depends(get_db)):
    votes = db.query(Vote).filter(Vote.user_id == user_id).all()
    return votes
