# ChatBot

A Django web application containerized with Docker and backed by PostgreSQL.

## Tech stack

- **Python** 3.12
- **Django** 5.x
- **Django Ninja** (REST API)
- **PostgreSQL** 16
- **Gunicorn** (production / Heroku)
- **Docker Compose** (local development)
- **LangChain** (RAG orchestration)
- **Pinecone** (vector store, cloud-hosted)
- **Ollama** (local LLM + embeddings)

## Project structure

```
ChatBot/
├── config/                 # Django project settings and URL routing
│   └── api.py              # Ninja API assembly (mounts app routers)
├── core/                   # Starter Django app
│   ├── api.py              # Core REST routes (/api/ping)
│   └── rag/                # LangChain + Pinecone helpers
├── chat/                   # Chat app (conversations, messages)
│   ├── api.py              # Chat REST routes (/api/chat/...)
│   └── urls.py             # Chat Django URLConf
├── docker-compose.yml      # Local development (Postgres + runserver)
├── Dockerfile              # Image for local Compose and Heroku
├── heroku.yml              # Heroku Container stack manifest
├── entrypoint.sh           # Runs migrations before start (local only)
├── manage.py
├── requirements.txt
└── .env.example            # Environment variable template
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting started

### 1. Configure environment variables

Copy the example env file and update values as needed:

```bash
cp .env.example .env
```

At minimum, change `SECRET_KEY` to a unique random string before deploying.

For RAG features, also set `PINECONE_API_KEY` and `PINECONE_INDEX_NAME` (see [RAG / Pinecone](#rag--pinecone)). Ollama runs as a Docker service — no API key needed locally.

### 2. Start the development stack

```bash
docker compose up --build
```

The app will be available at [http://localhost:8000](http://localhost:8000).

On startup, the web container automatically runs database migrations.

### 3. Create a superuser (optional)

```bash
docker compose exec web python manage.py createsuperuser
```

Then open the Django admin at [http://localhost:8000/admin/](http://localhost:8000/admin/).

## Development

The compose file mounts your local code into the container, so changes are picked up by Django's development server without rebuilding the image.

### Common commands

```bash
# Run in the background
docker compose up -d

# View logs
docker compose logs -f web

# Run migrations manually
docker compose exec web python manage.py migrate

# Create a new Django app
docker compose exec web python manage.py startapp myapp

# Open a shell in the web container
docker compose exec web bash

# Create Pinecone index (first time only)
docker compose exec web python manage.py ensure_pinecone_index

# Pull Ollama models (first time only — downloads llama + embedding model)
docker compose exec web python manage.py pull_ollama_models

# Verify RAG pipeline (embed → upsert → search)
docker compose exec web python manage.py rag_smoke_test

# Stop containers
docker compose down
```

### Health check

```bash
curl http://localhost:8000/health/
```

Expected response:

```json
{"status": "ok"}
```

### REST API

REST endpoints are served by [Django Ninja](https://django-ninja.dev/) under `/api/`.

| Endpoint | Description |
|---|---|
| `GET /api/ping` | API health / metadata |
| `GET /api/chat/` | Chat app status |
| `GET /api/docs` | Interactive OpenAPI docs (Swagger UI) |
| `GET /api/openapi.json` | OpenAPI schema |

```bash
curl http://localhost:8000/api/ping
```

## RAG / Pinecone + Ollama

- **Pinecone** is a managed vector database (cloud-hosted, API key required).
- **Ollama** runs locally in Docker and serves the LLM and embedding models.

### One-time setup

1. Create a [Pinecone](https://www.pinecone.io/) account and API key.
2. Add to `.env`:

   ```bash
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX_NAME=chatbot-dev
   ```

3. Start the stack and pull models:

   ```bash
   docker compose up --build -d
   docker compose exec web python manage.py pull_ollama_models
   docker compose exec web python manage.py ensure_pinecone_index
   ```

4. Run the smoke test:

   ```bash
   docker compose exec web python manage.py rag_smoke_test
   ```

Default models: `nomic-embed-text` (768-dim embeddings) and `llama3.2` (chat). Override via `OLLAMA_EMBEDDING_MODEL`, `OLLAMA_LLM_MODEL`, and `EMBEDDING_DIMENSION` in `.env`. `EMBEDDING_DIMENSION` must match the Pinecone index.

Ollama is also exposed on [http://localhost:11434](http://localhost:11434) if you want to use it outside Docker.

### Heroku

Pinecone works on Heroku with config vars only. Ollama is **not** suitable for Heroku dynos — use a hosted LLM API in production or run Ollama on a separate server and set `OLLAMA_BASE_URL` accordingly.

```bash
heroku config:set \
  PINECONE_API_KEY="..." \
  PINECONE_INDEX_NAME="chatbot-prod" \
  -a your-app-name
```

## Deploy to Heroku (Docker)

Production runs on [Heroku Container stack](https://devcenter.heroku.com/articles/build-docker-images-heroku). The same `Dockerfile` is used locally and on Heroku. `heroku.yml` defines the build, release (migrate + collectstatic), and run (Gunicorn) phases.

### Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Logged in: `heroku login`
- Git repo with a `main` branch

### One-time setup

Replace `your-app-name` with your Heroku app name:

```bash
heroku create your-app-name
heroku stack:set container -a your-app-name
heroku addons:create heroku-postgresql:essential-0 -a your-app-name
heroku config:set \
  SECRET_KEY="your-random-secret-key" \
  DEBUG=False \
  ALLOWED_HOSTS="your-app-name.herokuapp.com,.herokuapp.com" \
  CSRF_TRUSTED_ORIGINS="https://your-app-name.herokuapp.com" \
  -a your-app-name
heroku git:remote -a your-app-name
```

`DATABASE_URL` is set automatically when Postgres is attached.

### Deploy

```bash
git push heroku main
```

Heroku builds the Docker image from `Dockerfile`, runs migrations and `collectstatic` in the release phase, then starts Gunicorn.

### Verify

```bash
heroku open -a your-app-name
curl https://your-app-name.herokuapp.com/health/
```

### Alternative: push image from local Docker

```bash
heroku container:login
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1,0.0.0.0` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | — |
| `POSTGRES_DB` | Database name (local) | `chatbot` |
| `POSTGRES_USER` | Database user (local) | `chatbot` |
| `POSTGRES_PASSWORD` | Database password (local) | `chatbot` |
| `POSTGRES_HOST` | Database host (local) | `db` |
| `POSTGRES_PORT` | Database port (local) | `5432` |
| `DATABASE_URL` | Database URL (Heroku, auto-set) | — |
| `PINECONE_API_KEY` | Pinecone API key | — |
| `PINECONE_INDEX_NAME` | Pinecone index name | `chatbot-dev` |
| `PINECONE_NAMESPACE` | Pinecone namespace | `default` |
| `PINECONE_CLOUD` | Serverless cloud provider | `aws` |
| `PINECONE_REGION` | Serverless region | `us-east-1` |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://ollama:11434` |
| `OLLAMA_LLM_MODEL` | Chat model | `llama3.2` |
| `OLLAMA_EMBEDDING_MODEL` | Embedding model | `nomic-embed-text` |
| `EMBEDDING_DIMENSION` | Vector dimension (must match index) | `768` |

## License

Add your license here.
