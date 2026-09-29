from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class Status(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CommentCreate(BaseModel):
    body: str = Field(min_length=1)


class CommentOut(CommentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    priority: Priority = Priority.medium


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    status: Status
    priority: Priority
    created_at: datetime
    updated_at: datetime
    comments: list[CommentOut] = []