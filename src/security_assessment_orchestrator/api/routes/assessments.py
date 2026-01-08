from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from security_assessment_orchestrator.infra.db.models import Assessment
from security_assessment_orchestrator.infra.db.session import get_session_factory
from security_assessment_orchestrator.infra.security.auth import require_bearer_token
from security_assessment_orchestrator.infra.security.target_validation import validate_target
from security_assessment_orchestrator.workers.tasks import run_assessment

router = APIRouter(dependencies=[Depends(require_bearer_token)])


class AssessmentCreate(BaseModel):
    target: str = Field(..., description="Hostname/IP or URL (must be allowlisted)")


def _db() -> Session:
    return get_session_factory()()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_assessment(req: AssessmentCreate) -> dict:
    validate_target(req.target)
    db = _db()
    try:
        a = Assessment(target=req.target, status="queued", created_at=dt.datetime.utcnow())
        db.add(a)
        db.commit()
        db.refresh(a)
        run_assessment.delay(a.id)
        return {"id": a.id, "status": a.status, "target": a.target}
    finally:
        db.close()


@router.get("/{assessment_id}")
def get_assessment(assessment_id: int) -> dict:
    db = _db()
    try:
        a = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
        if a is None:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return {
            "id": a.id,
            "target": a.target,
            "status": a.status,
            "created_at": a.created_at,
            "finished_at": a.finished_at,
            "error_message": a.error_message,
        }
    finally:
        db.close()


@router.get("/{assessment_id}/artifacts")
def get_artifacts(assessment_id: int) -> list[dict]:
    db = _db()
    try:
        a = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
        if a is None:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return [
            {
                "id": art.id,
                "kind": art.kind,
                "content_type": art.content_type,
                "content": art.content,
            }
            for art in a.artifacts
        ]
    finally:
        db.close()
