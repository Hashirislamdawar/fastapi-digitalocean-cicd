# FastAPI DigitalOcean CI/CD

A beginner-friendly FastAPI REST API that will later be containerized and deployed to DigitalOcean through a GitHub Actions CI/CD pipeline.

This repository currently contains **Stage 1** (FastAPI application), **Stage 2** (Docker), **Stage 3** (GitHub Actions CI), and **Stage 4** (GHCR image publishing). The current stage adds Terraform-based DigitalOcean infrastructure provisioning for a later deployment pipeline.

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

## Stage 5 — Terraform Infrastructure

This stage provisions the DigitalOcean infrastructure required before application deployment begins. It creates a Droplet running Ubuntu, reuses an existing DigitalOcean SSH key, and attaches a cloud firewall with inbound access for SSH, HTTP, and HTTPS. The purpose is to prepare the server for later stages that will install and deploy the FastAPI application.

The Terraform configuration in `terraform/` includes:

- DigitalOcean Droplet
- Ubuntu 22.04 LTS base image
- existing DigitalOcean SSH key lookup via `digitalocean_ssh_key`
- DigitalOcean cloud firewall
- inbound rules for TCP 22, 80, and 443

Application deployment is intentionally not part of this stage. No Docker installation, no Nginx setup, no TLS certificates, and no app deployment scripts are included here.

To initialize the Terraform configuration locally, run:

```bash
cd terraform
terraform init
terraform fmt
terraform validate
```

Before applying changes, review the plan manually:

```bash
terraform plan
```

This stage should only provision infrastructure and should not create or destroy DigitalOcean resources unless you explicitly choose to apply the plan yourself.

## Stage 6 — Server Preparation

Stage 6 prepares the Ubuntu Droplet for later application deployment by installing Docker Engine from Docker's official APT repository, enabling the service, and installing Docker Compose V2 and Docker Buildx. It also creates a dedicated `deploy` user and grants Docker access so the server can host the application in later stages without using root.

This stage verifies the base operating system, updates package metadata, and confirms Docker is working before any application deployment begins. The FastAPI application is intentionally not deployed in Stage 6.

The server is configured with:

- Ubuntu 22.04 LTS
- Docker Engine
- Docker Compose V2
- Docker Buildx
- non-root `deploy` user
- SSH access for the deploy user using the existing key

No application image is pulled, no GitHub Container Registry authentication is added, and no FastAPI container is launched in this stage.

## Stage 7 — Manual GHCR Deployment

Stage 7 demonstrates the manual deployment flow for the existing FastAPI Docker image. The purpose is to understand the deployment process before automating it with GitHub Actions in a later stage.

The conceptual flow is:

1. Verify whether the GHCR package is public or private.
2. If required, authenticate Docker to GHCR using a GitHub PAT with package-read access.
3. Pull the published image from `ghcr.io/hashirislamdawar/fastapi-digitalocean-cicd:latest`.
4. Run the container on the Droplet with a name such as `fastapi-api` and port mapping `8000:8000`.
5. Configure a restart policy of `unless-stopped`.
6. Verify the application endpoints locally and confirm the container started successfully.

Important notes:

- `latest` is convenient for manual deployment but is mutable.
- In production, immutable commit-SHA tags are preferred over `latest`.
- No real GitHub token should be committed to the repository or documented in the README.
- The application is intentionally deployed manually here; GitHub Actions automation is not added in this stage.

Example login command pattern:

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Example deploy command pattern:

```bash
docker run -d \
  --name fastapi-api \
  --restart unless-stopped \
  -p 8000:8000 \
  ghcr.io/hashirislamdawar/fastapi-digitalocean-cicd:latest
```

This stage does not add Nginx, TLS, domain configuration, monitoring, or deployment automation. Those are reserved for later stages.

## Stage 8 — Nginx Reverse Proxy

Stage 8 adds Nginx as the public reverse proxy in front of the FastAPI container. The public entry point is HTTP on port 80, while the FastAPI container remains internal on `127.0.0.1:8000`.

The conceptual flow is:

- Install Nginx from Ubuntu's official package repositories
- Create a dedicated server block for the FastAPI app
- Use `proxy_pass http://127.0.0.1:8000;`
- Keep FastAPI internal to localhost instead of exposing Docker port 8000 publicly
- Validate the proxy with `nginx -t` and HTTP requests through Nginx
- Confirm the service is enabled and active

This stage does not configure HTTPS, Certbot, or a domain. TLS and certificate handling belong to later stages.

Example Nginx site pattern:

```nginx
server {
    listen 80;
    server_name 45.55.86.55;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

This configuration keeps the FastAPI app off the public internet while allowing Nginx to serve the app over HTTP. HTTPS and HSTS are intentionally not added in this stage.

## Stage 9 — Container Security Scanning

Stage 9 adds Trivy to the GitHub Actions pipeline so the Docker image is scanned for vulnerabilities before it is pushed to GHCR. The scan is limited to CI security validation and does not add automated deployment to DigitalOcean.

The workflow now does the following:

1. Runs Python tests
2. Builds the Docker image locally in the runner
3. Scans the built image with Trivy
4. Fails the pipeline when HIGH or CRITICAL vulnerabilities are found
5. Pushes the same image to GHCR only after the scan passes

This keeps the existing GHCR image tags intact while making the release process safer. Trivy runs in GitHub Actions only; it is not installed on the DigitalOcean server as part of this stage.

## What's next

This project will later be expanded into a complete CD pipeline using GHCR, Terraform, DigitalOcean, and automated FastAPI deployment.
