# syntax=docker/dockerfile:1.4
FROM python:3.11-slim AS base

# Empêcher Python de générer des fichiers .pyc et activer le buffer standard
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système (FFmpeg, libsndfile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-privilégié sécurisé
RUN groupadd -g 1000 mangatok && \
    useradd -u 1000 -g mangatok -m -s /bin/bash mangatok

WORKDIR /app

# Outils de packaging ; les dépendances runtime sont déclarées dans pyproject.toml.
COPY pyproject.toml pytest.ini ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copie du code source et des artefacts
COPY manga_studio/ ./manga_studio/
COPY schemas/ ./schemas/
COPY specs/ ./specs/
COPY docs/ ./docs/
COPY tests/ ./tests/
COPY README.md ./

# Installation du package et de ses dépendances runtime verrouillées par pyproject.toml
RUN pip install --no-cache-dir .

# Création du dossier d'artefacts avec permissions appropriées
RUN mkdir -p /app/output /app/demo_output && \
    chown -R mangatok:mangatok /app

USER mangatok

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

CMD ["uvicorn", "manga_studio.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
