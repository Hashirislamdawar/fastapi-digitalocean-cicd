# FastAPI DigitalOcean CI/CD

A beginner-friendly FastAPI REST API that will later be containerized and deployed to DigitalOcean through a GitHub Actions CI/CD pipeline.

This repository currently contains **Stage 1** (FastAPI application), **Stage 2** (Docker), and **Stage 3** (GitHub Actions CI). Later stages will add GHCR, Terraform, DigitalOcean, and deployment.

## Current stack

- Python
- FastAPI
- Uvicorn
- pytest
- httpx
- Docker
- Docker Compose
- GitHub Actions

## Project structure

```text
fastapi-digitalocean-cicd/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Local installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Run tests

From the project root:

```bash
pytest
```

Expected result: `3 passed`.

## Start the FastAPI server

From the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

Interactive docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Available API endpoints

| Method | Path       | Description                                      |
| ------ | ---------- | ------------------------------------------------ |
| GET    | `/`        | Confirms the application is running              |
| GET    | `/health`  | Health check for later CI/CD deployment checks   |
| GET    | `/version` | Returns the application version from FastAPI metadata |

Example requests:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

## Docker

The `Dockerfile` builds a small image from `python:3.12-slim`, installs dependencies, copies the FastAPI app, and starts Uvicorn on `0.0.0.0:8000` so the API is reachable from outside the container.

`.dockerignore` keeps local virtualenv files, caches, Git metadata, and `.env` out of the image build context.

### Build the image

From the project root:

```bash
docker build -t fastapi-cicd:1.0.0 .
```

### Run the container

```bash
docker run -d --name fastapi-cicd -p 8000:8000 fastapi-cicd:1.0.0
```

Confirm it is running:

```bash
docker ps
```

Inspect logs:

```bash
docker logs fastapi-cicd
```

### Test the API

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/version
```

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

`GET /health` should return:

```json
{
  "status": "healthy"
}
```

### Stop and remove the container

```bash
docker stop fastapi-cicd
docker rm fastapi-cicd
```

### Docker Compose

`docker-compose.yml` defines a single `api` service that builds the local Dockerfile, maps port `8000`, and restarts unless the container is stopped.

Start:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Test:

```bash
curl http://localhost:8000/health
```

View logs:

```bash
docker compose logs api
```

Stop:

```bash
docker compose down
```

Do not run `docker run` and `docker compose up` at the same time on port 8000, or they will conflict.

## CI/CD

The repository currently has **CI only**. There is no deployment, DigitalOcean, Terraform, or image registry step yet.

```text
GitHub Push / Pull Request
        ↓
Python Tests
        ↓
Docker Build
```

The workflow in `.github/workflows/ci.yml` runs on:

- pushes to `main`
- pushes to `develop`
- pull requests targeting `main`

If pytest fails, the Docker build job is skipped. The Docker job builds `fastapi-cicd:test` to confirm the Dockerfile works; it does **not** push an image.

Future stages will add:

- GitHub Container Registry
- DigitalOcean
- Terraform
- automatic deployment
- security scanning
- rollback

## What's next

This project will later be expanded into a complete CD pipeline using GHCR, Terraform, and DigitalOcean.
