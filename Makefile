.DEFAULT_GOAL := help

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest
UVICORN ?= $(PYTHON) -m uvicorn

.PHONY: help
help: ## Affiche l'aide et la liste des commandes disponibles
	@echo "========================================================================"
	@echo "⚡ MangaTok Studio — Mode « Conte animé » Makefile"
	@echo "========================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Installe le package et ses dépendances de base
	@echo "==> Installation de MangaTok Studio..."
	$(PIP) install -e .

.PHONY: dev-install
dev-install: ## Installe toutes les dépendances de développement et de test
	@echo "==> Installation des dépendances de développement..."
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov httpx fastapi uvicorn pillow jinja2 pydantic

.PHONY: test
test: ## Exécute la suite complète de tests hors-ligne
	@echo "==> Exécution des tests unitaires et d'intégration..."
	$(PYTEST) -v

.PHONY: test-cov
test-cov: ## Exécute les tests avec rapport de couverture de code
	@echo "==> Exécution des tests avec couverture..."
	$(PYTEST) --cov=manga_studio --cov-report=term-missing --cov-report=xml --cov-fail-under=85

.PHONY: validate-schemas
validate-schemas: ## Valide les modèles Pydantic et schémas JSON
	@echo "==> Validation des schémas de données..."
	./scripts/validate_schemas.sh

.PHONY: run-demo
run-demo: ## Lance une génération complète sur le conte de démonstration (Mythe de Râ)
	@echo "==> Lancement du pipeline Conte animé (Démo)..."
	./scripts/run_demo.sh

.PHONY: serve
serve: ## Démarre le serveur FastAPI et le tableau de bord Web sur le port 8000
	@echo "==> Démarrage du studio Web FastAPI sur http://0.0.0.0:8000..."
	$(UVICORN) manga_studio.api.app:app --host 0.0.0.0 --port 8000 --reload

.PHONY: frontend-install
frontend-install: ## Installe les dépendances du frontend Next.js
	@echo "==> Installation des dépendances Next.js..."
	cd frontend && npm install

.PHONY: frontend-build
frontend-build: ## Compile le frontend Next.js pour la production
	@echo "==> Compilation du frontend Next.js..."
	cd frontend && npm run build

.PHONY: frontend-dev
frontend-dev: ## Lance le serveur de développement Next.js (port 3000)
	@echo "==> Démarrage du frontend Next.js sur http://0.0.0.0:3000..."
	cd frontend && npm run dev

.PHONY: frontend-start
frontend-start: ## Lance le frontend Next.js en mode production (port 3000)
	@echo "==> Démarrage du frontend Next.js en production sur http://0.0.0.0:3000..."
	cd frontend && npm run start

.PHONY: docker-build
docker-build: ## Compile l'image Docker standard (CPU / Production)
	@echo "==> Construction de l'image Docker standard..."
	docker build -t mangatok-studio:latest -f Dockerfile .

.PHONY: docker-build-gpu
docker-build-gpu: ## Compile l'image Docker CUDA (GPU RTX 4090)
	@echo "==> Construction de l'image Docker GPU CUDA..."
	docker build -t mangatok-studio:gpu -f Dockerfile.gpu .

.PHONY: docker-up
docker-up: ## Démarre les services via Docker Compose
	@echo "==> Démarrage du conteneur via docker-compose..."
	docker compose up -d manga-studio-app

.PHONY: docker-down
docker-down: ## Arrête les services Docker Compose
	@echo "==> Arrêt des conteneurs..."
	docker compose down

.PHONY: benchmark-vram
benchmark-vram: ## Exécute le benchmark mémoire GPU (plafond 22 Go)
	@echo "==> Lancement du benchmark de performance et mémoire..."
	./scripts/benchmark_vram.sh

.PHONY: clean
clean: ## Nettoie les caches, fichiers temporaires et builds
	@echo "==> Nettoyage de l'espace de travail..."
	./scripts/clean.sh
