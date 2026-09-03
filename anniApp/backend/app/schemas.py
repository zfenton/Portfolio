from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityOptionResponse(BaseModel):
    id: int
    option_text: str
    order: int

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    id: int
    question: str
    order: int
    options: List[ActivityOptionResponse]

    class Config:
        from_attributes = True


class VoteCreate(BaseModel):
    activity_id: int
    option_id: int


class VoteResponse(BaseModel):
    id: int
    user_id: int
    activity_id: int
    option_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    message_text: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    user_id: int
    message_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class VotingStatus(BaseModel):
    is_voting_open: bool
    voting_end_time: Optional[datetime]


class VoteCount(BaseModel):
    option_id: int
    option_text: str
    vote_count: int


class ActivityResultResponse(BaseModel):
    activity_id: int
    question: str
    order: int
    vote_counts: List[VoteCount]
    total_votes: int
