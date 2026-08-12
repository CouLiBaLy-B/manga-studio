# Revue de qualité de bout en bout — 12 août 2026

## Synthèse exécutive

**Verdict : non prêt pour un déploiement de production.** Le cœur du pipeline et ses modèles de domaine sont plutôt bien structurés (ports/adaptateurs, modèles Pydantic, suite de tests conséquente), mais les interfaces Web et le packaging présentent des défauts bloquants : la suite Python ne passe pas dans un environnement propre, l'API est liée à un chemin de développement, la composition Docker ne permet pas au frontend de joindre le backend, et la surface HTTP autorise des écritures non authentifiées et des traversées de répertoires.

| Axe | Appréciation | Conclusion |
|---|---:|---|
| Fonctionnel / pipeline | 3/5 | Exécution de démonstration et modèles correctement couverts ; comportement de QC réel peu exercé. |
| Tests et automatisation | 2/5 | 62 réussites mais 2 échecs reproductibles ; CI GitHub placée hors du répertoire reconnu. |
| Sécurité applicative | 1/5 | Contrôles d'accès, validation de chemins et limites d'upload absents. |
| Déploiement / exploitabilité | 1/5 | Chemin absolu et proxy inter-conteneurs erroné. |
| Dépendances | 1/5 | Deux vulnérabilités `npm audit`, dont une critique ; dépendances backend d'API non déclarées. |
| Frontend | 3/5 | Build et vérification TypeScript passent ; intégration backend en Docker défaillante. |

**Priorité recommandée :** corriger les points P0 avant toute exposition réseau ; traiter P1 avant la prochaine livraison ; puis instaurer les contrôles de qualité P2.

## Périmètre et méthode

Revue statique du dépôt, des Dockerfiles, Compose, CI, packaging, API FastAPI, client Next.js et tests. Exécutions réalisées dans un environnement propre le 12 août 2026 :

```text
/tmp/manga-studio-venv/bin/pytest -q --cov=manga_studio --cov-report=term-missing --cov-fail-under=85
Résultat : 62 passed, 2 failed ; couverture globale 86,67 % (seuil 85 % atteint)

frontend: npm ci && npm run build
Résultat : succès ; Next.js 14.2.5 ; route / statiquement générée

frontend: npm audit --omit=dev --audit-level=low
Résultat : 2 vulnérabilités : 1 critique (next), 1 élevée (postcss transitif)

python -m compileall -q manga_studio ; python -m pip check
Résultat : succès dans l'environnement initial (vérification de cohérence des paquets installés)
```

Les tests n'ont pas été modifiés afin de conserver l'observation fidèle de l'état du dépôt. Les scans ne remplacent ni un pentest authentifié ni un test GPU/modèles réels.

## Constats détaillés

### P0 — à corriger avant exposition ou livraison

#### Q-01 — Écriture / lecture arbitraire par traversée de répertoires dans l'API

- **Preuve :** `manga_studio/api/app.py:248`, `:303` construisent `BASE_DIR / "output" / story_id` sans whitelist ni vérification de résolution ; `:262` écrit directement `chars_dir / f.filename`. Les routes de lecture utilisent également `story_id`, et `:231` accepte toute extension de sous-titre.
- **Impact :** un `story_id` tel que `../../…` ou un nom de fichier d'upload contenant des segments de chemin peut sortir de `output/`, écraser/lire des fichiers accessibles au processus, ou polluer des artefacts. La validation de type MIME et de taille est aussi absente.
- **Correction :** imposer un identifiant canonique (`^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$`), résoudre le chemin et vérifier `is_relative_to(OUTPUT_ROOT)` ; utiliser `Path(upload.filename).name`, une extension/MIME autorisés, un maximum de 9 fichiers et une limite de taille en streaming. Limiter `ext` à `srt|ass`.

#### Q-02 — API de génération et d'édition ouverte, CORS dangereux

- **Preuve :** `app.py:31-35` configure `allow_origins=["*"]` avec `allow_credentials=True`. Les endpoints `POST /api/generate`, `POST /api/upload-and-run`, `PUT .../segments/...` et `POST .../reorder` ne demandent ni authentification, ni autorisation, ni protection anti-abus.
- **Impact :** toute origine peut tenter de piloter une génération coûteuse, modifier les storyboards et accéder aux productions dès que le service est publié. La combinaison wildcard + credentials est en outre incohérente avec les navigateurs.
- **Correction :** authentification (OIDC/session ou jeton de service), autorisation par run, liste d'origines configurée par environnement, rate limiting et quotas. Désactiver CORS public si le frontend est servi par le même domaine.

#### Q-03 — L'intégration Docker frontend → API est rompue

- **Preuve :** `frontend/next.config.js:8` réécrit vers `http://127.0.0.1:8000`; dans `docker-compose.yml`, frontend et API sont deux conteneurs. `127.0.0.1` est donc le conteneur frontend, pas `manga-studio-app`.
- **Impact :** le dashboard construit avec succès mais ses appels `/api/*` échouent dans la pile Compose.
- **Correction :** rendre l'URL de backend configurable (`BACKEND_URL`, par défaut local pour le développement) et injecter `http://manga-studio-app:8000` dans le service frontend. Ajouter un smoke test Compose qui vérifie `/api/status` à travers le proxy.

#### Q-04 — Le backend ne démarre pas dans l'image fournie

- **Preuve :** `app.py:37` fixe `BASE_DIR = Path("/home/user/manga-studio")`, tandis que `Dockerfile` utilise `WORKDIR /app` et y copie le code/fixtures. Le répertoire codé en dur n'existe pas dans l'image.
- **Impact :** les données de démonstration, sorties et fixtures recherchées par l'API sont introuvables en conteneur ; les endpoints de génération échouent ou écrivent hors de l'emplacement attendu.
- **Correction :** configurer `DATA_ROOT`/`OUTPUT_ROOT` via variables d'environnement et faire un défaut relatif déterministe à partir de `Path(__file__)` ou `/app`. Ne jamais dépendre d'un chemin de poste de développeur.

### P1 — à traiter avant la prochaine version

#### Q-05 — La suite Python ne passe pas de manière isolée

- **Preuve :** commande de test ci-dessus : `test_update_segment_endpoint` et `test_reorder_segments_endpoint` renvoient **404**. Les tests dans `tests/unit/test_storyboard_editor_api.py` attendent un run `conte` préexistant, alors qu'aucun fixture de storyboard n'est créé et `demo_output/` est ignoré par Git.
- **Impact :** le quality gate annoncé ne garantit pas un dépôt vert ; les tests dépendent d'un état externe et peuvent donner des résultats différents selon l'ordre/l'environnement.
- **Correction :** fixture pytest temporaire et injection du répertoire de sortie (ou `monkeypatch`), création explicite du storyboard de test avant chaque cas, et assertion des refus (404/422) attendus. Ne pas utiliser le répertoire de travail réel dans les tests.

#### Q-06 — Le workflow CI n'est pas dans le chemin GitHub Actions standard

- **Preuve :** le workflow est dans `ci/workflows/ci.yml`, alors que GitHub Actions ne charge que `.github/workflows/*.yml`. Le badge README renvoie lui aussi vers ce fichier et affirme « CI Passing ».
- **Impact :** aucun contrôle ne se déclenche réellement sur GitHub à partir de ce fichier ; les régressions et vulnérabilités peuvent être fusionnées sans garde-fou.
- **Correction :** déplacer les workflows dans `.github/workflows/`, vérifier leur déclenchement avec `gh run list`, et retirer le badge « Passing » tant qu'une exécution vérifiée n'existe pas.

#### Q-07 — Vulnérabilités frontend connues

- **Preuve :** `npm audit --omit=dev --audit-level=low` retourne 1 vulnérabilité **critique** sur `next@14.2.5` (avec de multiples avis, notamment empoisonnement de cache, SSRF/contournement d'autorisation et DoS) et 1 vulnérabilité **élevée** sur `postcss` transitif. Le build avertit aussi explicitement que cette version de Next est vulnérable.
- **Impact :** exposition d'une application Next auto-hébergée à des vulnérabilités publiées.
- **Correction :** appliquer et examiner `npm audit fix` dans une branche, verrouiller une version Next corrigée et le lockfile, reconstruire et exécuter les tests. Ajouter `npm ci`, `npm run build` et `npm audit --audit-level=high` à la CI.

#### Q-08 — Dépendances runtime API absentes du manifeste Python

- **Preuve :** `pyproject.toml` ne déclare que Pydantic, Pillow, Jinja2 et **pytest**. Pourtant `manga_studio.api.app` importe FastAPI et requiert `python-multipart` pour `Form`/`File`; le Makefile et la CI les installent séparément.
- **Impact :** `pip install .` ne fournit pas l'application Web promise ; l'installation n'est pas reproductible. `pytest` est en plus une dépendance de production plutôt qu'un extra de développement.
- **Correction :** déclarer les dépendances runtime avec bornes compatibles (FastAPI, Uvicorn, python-multipart si l'API reste incluse) et déplacer tests/outils dans `[project.optional-dependencies].dev`; ajouter un lockfile ou une stratégie de contraintes reproductible.

#### Q-09 — Risque d'altération silencieuse lors du réordonnancement

- **Preuve :** `app.py:164-170` ne reconstruit que les IDs fournis. Un payload incomplet ou avec doublon aboutit à la suppression silencieuse de scènes ; aucun contrôle de permutation exacte n'est réalisé.
- **Impact :** perte de contenu du storyboard via l'interface ou un appel API erroné.
- **Correction :** vérifier que l'ensemble et la cardinalité des IDs reçus correspondent exactement aux scènes existantes, sinon retourner 422 ; effectuer l'écriture atomiquement et ajouter des tests d'IDs inconnus, manquants et dupliqués.

#### Q-10 — Génération synchrone, non bornée et sans isolation par tâche

- **Preuve :** `upload_and_run` (`app.py:242-294`) et `trigger_generation` (`:300-332`) exécutent directement `AnimatedTalePipelineRunner.run_pipeline` dans le handler HTTP, sans timeout, file, état de tâche ou annulation.
- **Impact :** saturation des workers/processus par des générations longues, requêtes interrompues sans visibilité, déni de service facile même après ajout d'authentification.
- **Correction :** file de jobs durable (worker séparé), identifiant de job, progression/polling, concurrence plafonnée, timeout et quotas par tenant. Pour un MVP, au minimum `BackgroundTasks` ne suffit pas pour une charge GPU : séparer le worker.

### P2 — amélioration de robustesse et de maintenabilité

1. **Résultats QC et intégrations réelles sous-testés.** Malgré 86,67 % global, `clip_dino_qc_adapter.py` n'est couvert qu'à 62 %, Bedrock à 56 %, l'API à 45 % et GPU à 68 %. Le seuil global masque les zones risquées. Définir des seuils par module critique et utiliser des fakes contractuels.
2. **Absence de contrôles de style/statique visibles.** Aucun Ruff/Black/mypy/ESLint dédié ni hook de pré-commit n'est configuré. Ajouter des cibles Make et les gates CI correspondants.
3. **Docker reproductible.** Les Dockerfiles installent des versions Python et npm non verrouillées ; `frontend/Dockerfile` utilise `npm install` plutôt que `npm ci`. Ajouter `.dockerignore` efficace, builds multi-stage exécutés en utilisateur non privilégié (déjà le cas backend, point positif), et SBOM/image scan.
4. **UX/fiabilité frontend.** `handleGenerate` inscrit « succès » avant d'avoir vérifié `res.ok` (`frontend/app/page.tsx`) ; les URLs d'aperçu créées avec `URL.createObjectURL` ne sont pas révoquées. Afficher l'erreur serveur, empêcher les soumissions concurrentes et libérer les object URLs.
5. **Observabilité.** L'API renvoie des chemins internes (`report_path`), n'a pas de corrélation de requête, métriques, ni journal structuré. Exposer plutôt des URLs/IDs contrôlés et instrumenter durée, échecs, utilisation GPU et coûts.

## Points positifs vérifiés

- La séparation core/ports/adaptateurs est lisible et la couverture du pipeline nominal est bonne.
- Les modèles Pydantic imposent plusieurs bornes utiles (budget, VRAM, retries, résolution).
- La compilation Python et `pip check` ne révèlent pas d'erreur syntaxique ou de conflit dans l'environnement inspecté.
- Le build production Next.js réussit, avec vérification TypeScript.
- Les Dockerfiles exécutent le backend sous un utilisateur non privilégié et le `.gitignore` exclut correctement sorties et caches usuels.
- Les appels `subprocess` inspectés pour FFmpeg sont construits sous forme de listes, sans `shell=True` dans le code applicatif.

## Plan de remédiation proposé

1. **J0–J2 :** Q-01 à Q-04, correctifs avec tests de sécurité (traversal, upload, CORS, Compose). Bloquer toute exposition publique jusque-là.
2. **J3–J5 :** Q-05 à Q-09 ; déplacer/activer CI, rendre les tests hermétiques, mettre à jour Next et déclarer/verrouiller les dépendances.
3. **J6–J10 :** Q-10 et P2 ; worker de jobs, observabilité, lint/type-check, scans de dépendances et smoke tests d'image/Compose.
4. **Critère de sortie :** CI réellement exécutée et verte sur Python 3.11/3.12, build frontend, audit sans vulnérabilité high/critical, test Compose proxy→API, tests d'autorisation/chemins/uploads, et revue manuelle de la génération GPU réelle.
