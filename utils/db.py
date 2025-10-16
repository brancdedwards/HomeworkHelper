from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_PATH = 'data/homework_helper.db'
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# ORM model definitions
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    topic = Column(String)
    passages = relationship("Passage", back_populates="session")

class Passage(Base):
    __tablename__ = "passages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    original_text = Column(Text)
    simplified_text = Column(Text)
    session = relationship("Session", back_populates="passages")
    questions = relationship("Question", back_populates="passage")
    words = relationship("Word", back_populates="passage")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    passage_id = Column(Integer, ForeignKey("passages.id"))
    question_text = Column(Text)
    passage = relationship("Passage", back_populates="questions")

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    passage_id = Column(Integer, ForeignKey("passages.id"))
    word = Column(String)
    explanation = Column(Text)
    passage = relationship("Passage", back_populates="words")

class Concept(Base):
    __tablename__ = "concepts"
    id = Column(Integer, primary_key=True)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime)
    subject = Column(String, nullable=False)
    topic = Column(Text, nullable=False)
    type = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(engine)
