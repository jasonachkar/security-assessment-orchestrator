from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from security_assessment_orchestrator.api.routes.health import router as health_router
from security_assessment_orchestrator.api.routes.assessments import router as assessments_router
from security_assessment_orchestrator.infra.logging import configure_logging

configure_logging()

app = FastAPI(title="security-assessment-orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["health"])
app.include_router(assessments_router, prefix="/assessments", tags=["assessments"])
