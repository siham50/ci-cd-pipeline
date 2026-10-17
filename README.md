# Self-Hosted CI/CD Pipeline

A complete CI/CD pipeline that automatically lints, tests, builds, and deploys a Flask API on every push to `main` — built from scratch using Docker, Gitea, Jenkins, Nginx, and Python.

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ Docker Host (Local / EC2)                                   │
│                                                             │
│ Developer                                                   │
│     │                                                       │
│     │ git push                                              │
│     ▼                                                       │
│ ┌─────────┐      webhook       ┌───────────┐                │
│ │  Gitea  │ ─────────────────► │  Jenkins  │                │
│ │  :3000  │                    │   :8090   │                │
│ └─────────┘                    └─────┬─────┘                │
│                                      │                      │
│                                lint → test → build          │
│                                      │                      │
│                                      ▼                      │
│                                ┌───────────────┐            │
│                                │ flask-api-prod│ (container)│
│                                │     :5000     │            │
│                                └───────┬───────┘            │
│                                        │                    │
│ User ─────► ┌─────────┐                │                    │
│             │  Nginx  │ ───────────────┘                    │
│             │   :80   │ proxy_pass                          │
│             └─────────┘                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack

| Tool | Purpose |
|---|---|
| **Flask** | Task manager API (the target being deployed) |
| **pytest** | Unit tests for all API routes |
| **flake8** | Python code quality / linting |
| **Docker** | Containerization of the API |
| **Docker Compose** | Runs the full infrastructure stack |
| **Gitea** | Self-hosted Git server (trigger source) |
| **Jenkins** | CI/CD engine that runs the pipeline |
| **Nginx** | Reverse proxy in front of the deployed API |
| **Gunicorn** | Production WSGI server |

---

## How It Works

1. Developer pushes code to **Gitea** (`main` branch).
2. Gitea fires a **webhook** to Jenkins.
3. Jenkins reads the **Jenkinsfile** and runs the pipeline:
   - **Lint** → `flake8` checks code style
   - **Test** → `pytest` runs unit tests for all routes
   - **Build Image** → builds a Docker image tagged with the build number
   - **Deploy** (main only) → stops the old container, runs the new one
   - **Health Check** (main only) → `curl /health` verifies the new container is live
4. If any stage fails, the pipeline stops — **broken code never reaches production**.
5. Nginx proxies user traffic on port 80 to the deployed Flask container.

**Branch-based deployment:**
- Push to `dev` → lint + test only (no deploy)
- Merge to `main` → full pipeline including deploy + health check

---

## Project Structure

```text
ci-cd-pipeline/
├── app/
│   ├── app.py             # Flask task manager API
│   ├── requirements.txt   # Pinned dependencies
│   ├── Dockerfile         # API image
│   ├── .dockerignore
│   └── tests/
│       └── test_app.py    # pytest suite
├── nginx/
│   └── nginx.conf         # Reverse proxy config
├── jenkins/
│   ├── Jenkinsfile        # Pipeline definition
│   └── Dockerfile         # Jenkins + Docker CLI image
├── docker-compose.yml     # Full stack
├── .env.example
├── .gitignore
└── README.md
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Health check for Jenkins |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/<id>` | Get one task |
| POST | `/tasks` | Create a task (`{"title": "..."}`) |
| PUT | `/tasks/<id>` | Update a task |
| DELETE | `/tasks/<id>` | Delete a task |

---

## Setup

### Prerequisites
- Docker
- Docker Compose
- Git

### Run the full stack

```bash
# 1. Clone
git clone https://github.com/youruser/ci-cd-pipeline.git
cd ci-cd-pipeline

# 2. Configure environment
cp .env.example .env
# edit .env and set FLASK_SECRET_KEY

# 3. Start infrastructure (Nginx + Gitea + Jenkins)
docker compose up -d

# 4. Check status
docker compose ps
```
---

## First-time service setup

### Gitea → http://localhost:3000

- Complete initial install (SQLite, admin account)
- Create repo `ci-cd-project`
- Push your code:
```bash
git remote add gitea http://localhost:3000/admin/ci-cd-project.git
git push gitea main
```

### Jenkins → http://localhost:8090

- Get initial password:
```bash
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
- Install suggested plugins + Docker Pipeline
- Add credentials:
**gitea-credentials (username/password)**
**FLASK_SECRET_KEY (secret text)**
- Create a Pipeline job → "Pipeline script from SCM" → point to your Gitea repo → script path: **jenkins/Jenkinsfile**

### Webhook (in Gitea repo → Settings → Webhooks)

- URL: `http://jenkins:8080/gitea-webhook/post`
- Content type: application/json
- Trigger: Push events only

### Verify
```bash
curl http://localhost/health
# → {"status": "ok"}
```

---

## Common Commands
```bash
docker compose up -d          # start everything
docker compose down           # stop (keep volumes)
docker compose down -v        # stop + wipe volumes
docker compose logs -f        # stream logs
docker compose ps             # status
docker compose exec jenkins docker ps
```
---

## What I Learned
- How a webhook connects two services end-to-end
- Why health checks matter more than depends_on in Docker Compose
- How Docker networking resolves service names via internal DNS
- Why Nginx resolves upstreams at startup (and how to fix it with resolver)
- How Jenkins decides pass/fail based on shell exit codes
- Why Docker CLI must be added to a Jenkins image, mounting the socket isn't enough

---

## License
MIT
