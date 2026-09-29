from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Mini Issue Tracker")


def get_issue_or_404(issue_id: int, db: Session) -> models.Issue:
    issue = db.get(models.Issue, issue_id)
    if not issue:
        raise HTTPException(404, "Issue not found")
    return issue


@app.post("/issues", response_model=schemas.IssueOut, status_code=201)
def create_issue(data: schemas.IssueCreate, db: Session = Depends(get_db)):
    issue = models.Issue(**data.model_dump(mode="json"))
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


@app.get("/issues", response_model=list[schemas.IssueOut])
def list_issues(
    status: schemas.Status | None = None,
    priority: schemas.Priority | None = None,
    q: str | None = Query(None, description="Search in title"),
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    stmt = select(models.Issue).order_by(models.Issue.id.desc())
    if status:
        stmt = stmt.where(models.Issue.status == status.value)
    if priority:
        stmt = stmt.where(models.Issue.priority == priority.value)
    if q:
        stmt = stmt.where(models.Issue.title.ilike(f"%{q}%"))
    return db.scalars(stmt.limit(limit).offset(offset)).all()


@app.get("/issues/{issue_id}", response_model=schemas.IssueOut)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    return get_issue_or_404(issue_id, db)


@app.patch("/issues/{issue_id}", response_model=schemas.IssueOut)
def update_issue(issue_id: int, data: schemas.IssueUpdate, db: Session = Depends(get_db)):
    issue = get_issue_or_404(issue_id, db)
    for key, value in data.model_dump(exclude_unset=True, mode="json").items():
        setattr(issue, key, value)
    db.commit()
    db.refresh(issue)
    return issue


@app.delete("/issues/{issue_id}", status_code=204)
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    db.delete(get_issue_or_404(issue_id, db))
    db.commit()


@app.post("/issues/{issue_id}/comments", response_model=schemas.CommentOut, status_code=201)
def add_comment(issue_id: int, data: schemas.CommentCreate, db: Session = Depends(get_db)):
    get_issue_or_404(issue_id, db)
    comment = models.Comment(issue_id=issue_id, body=data.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment