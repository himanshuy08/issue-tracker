from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from .database import Base


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="open")
    priority = Column(String(20), default="medium")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    issue = relationship("Issue", back_populates="comments")