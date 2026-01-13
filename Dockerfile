FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY shared-security-core /app/shared-security-core

COPY security-assessment-orchestrator/pyproject.toml /app/pyproject.toml
COPY security-assessment-orchestrator/src /app/src
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -e ".[dev]"
COPY security-assessment-orchestrator/alembic.ini /app/alembic.ini
COPY security-assessment-orchestrator/alembic /app/alembic
COPY security-assessment-orchestrator/scripts /app/scripts

EXPOSE 8082

CMD ["uvicorn", "security_assessment_orchestrator.api.main:app", "--host", "0.0.0.0", "--port", "8082"]
