from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    message = relationship("Message", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    options = relationship("ActivityOption", back_populates="activity", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="activity", cascade="all, delete-orphan")


class ActivityOption(Base):
    __tablename__ = "activity_options"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    option_text = Column(String(500), nullable=False)
    order = Column(Integer, nullable=False)

    activity = relationship("Activity", back_populates="options")
    votes = relationship("Vote", back_populates="option", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    option_id = Column(Integer, ForeignKey("activity_options.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="votes")
    activity = relationship("Activity", back_populates="votes")
    option = relationship("ActivityOption", back_populates="votes")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    message_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="message")


class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True, index=True)
    voting_end_time = Column(DateTime(timezone=True), nullable=True)
    is_voting_closed = Column(Boolean, default=False)
