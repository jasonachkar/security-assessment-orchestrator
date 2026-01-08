from __future__ import annotations

from fastapi import Header, HTTPException, status

from security_assessment_orchestrator.infra.settings import Settings


def require_bearer_token(authorization: str | None = Header(default=None)) -> None:
    settings = Settings()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != settings.auth_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
