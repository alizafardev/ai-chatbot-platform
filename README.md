# ChatBot

A Django web application containerized with Docker and backed by PostgreSQL, with LangChain chat and RAG APIs.

## Tech stack

- **Python** 3.12
- **Django** 5.x
- **Django Ninja** (REST API)
- **PostgreSQL** 16
- **Gunicorn** (production / Heroku)
- **Docker Compose** (local development)
- **LangChain** (LLM orchestration)
- **Pinecone** (vector store, cloud-hosted)
- **Ollama** (local LLM + embeddings)
- **OpenRouter** (production LLM + embeddings on Heroku)

## Project structure

```
ChatBot/
├── config/
│   ├── api.py              # Ninja API assembly (mounts app routers)
│   └── settings.py
├── core/
│   ├── api.py              # Core REST routes (/api/ping/)
│   └── rag/                # LangChain + Pinecone helpers
├── chat/
│   ├── api.py              # Chat REST routes
│   ├── schemas.py          # Request/response schemas
│   ├── service.py          # ChatService (hello + RAG)
│   └── urls.py
├── docker-compose.yml
├── Dockerfile
├── heroku.yml
├── entrypoint.sh
├── manage.py
└── requirements.txt
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Pinecone](https://www.pinecone.io/) account (for RAG)
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) (for production deploy)

## Getting started (local)

### 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values. At minimum set `SECRET_KEY`. For RAG, also set `PINECONE_API_KEY` and `PINECONE_INDEX_NAME`.

After changing `.env`, recreate the web container so Docker picks up new vars:

```bash
docker compose up -d --force-recreate web
```

### 2. Start the development stack

```bash
docker compose up --build
```

The app will be available at [http://localhost:8000](http://localhost:8000).

### 3. Bootstrap Pinecone + Ollama (first time)

```bash
docker compose exec web python manage.py pull_ollama_models
docker compose exec web python manage.py ensure_pinecone_index
docker compose exec web python manage.py rag_smoke_test
```

### 4. Create a superuser (optional)

```bash
docker compose exec web python manage.py createsuperuser
```

## REST API

Endpoints are served by [Django Ninja](https://django-ninja.dev/) under `/api/`. Routes use **trailing slashes** (Django convention).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health/` | Django health check |
| `GET` | `/api/ping/` | API health / metadata |
| `POST` | `/api/chat/hello/` | LangChain + LLM (Ollama locally, OpenRouter on Heroku) |
| `POST` | `/api/chat/rag/` | RAG: Pinecone retrieval + LLM answer |
| `GET` | `/api/docs` | Swagger UI |
| `GET` | `/api/openapi.json` | OpenAPI schema |

### Examples

```bash
# Health
curl http://localhost:8000/health/
curl http://localhost:8000/api/ping/

# LangChain hello (Ollama only)
curl -X POST http://localhost:8000/api/chat/hello/ \
  -H "Content-Type: application/json" \
  -d '{"question": "what is the capital of canada?"}'

# RAG (Pinecone + Ollama — requires seeded index)
curl -X POST http://localhost:8000/api/chat/rag/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What vector database does the platform use?"}'
```

## RAG / Pinecone + Ollama (local)

- **Pinecone** — cloud vector DB (API key required, no Docker service)
- **Ollama** — runs in Docker Compose (`ollama` service)

Add to `.env`:

```bash
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=chatbot-dev
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIMENSION=768
```

Default embedding model `nomic-embed-text` produces **768-dimensional** vectors. `EMBEDDING_DIMENSION` must match the Pinecone index.

`/api/chat/rag/` only **searches** Pinecone — it does not ingest. Seed knowledge first (`rag_smoke_test` or your own ingest flow).

## Deploy to Heroku (Docker)

Production uses [Heroku Container stack](https://devcenter.heroku.com/articles/build-docker-images-heroku). The same `Dockerfile` is used locally and on Heroku. `heroku.yml` defines build, release (migrate + collectstatic), and run (Gunicorn).

### One-time setup

Replace `your-app-name` with your Heroku app name:

```bash
heroku login
heroku create your-app-name
heroku stack:set container -a your-app-name
heroku addons:create heroku-postgresql:essential-0 -a your-app-name

heroku config:set \
  SECRET_KEY="your-random-secret-key" \
  DEBUG=False \
  ALLOWED_HOSTS="your-app-name.herokuapp.com,.herokuapp.com" \
  CSRF_TRUSTED_ORIGINS="https://your-app-name.herokuapp.com" \
  PINECONE_API_KEY="your-pinecone-api-key" \
  PINECONE_INDEX_NAME="chatbot-prod" \
  OPENROUTER_API_KEY="your-openrouter-api-key" \
  OPENROUTER_MODEL="~anthropic/claude-sonnet-latest" \
  OPENROUTER_EMBEDDING_MODEL="openai/text-embedding-3-small" \
  OPENROUTER_SITE_URL="https://your-app-name.herokuapp.com" \
  OPENROUTER_SITE_NAME="AI Chatbot Platform" \
  EMBEDDING_DIMENSION="1536" \
  -a your-app-name

heroku git:remote -a your-app-name
```

`DATABASE_URL` is set automatically when Postgres is attached.

**Production uses [OpenRouter](https://openrouter.ai/)** for LLM and embeddings (detected via `IS_HEROKU` / `DATABASE_URL`). **Local dev uses Ollama** in Docker Compose.

Use a **separate Pinecone index** for production (`chatbot-prod`, **1536** dimensions for OpenRouter embeddings) vs local dev (`chatbot-dev`, **768** for Ollama `nomic-embed-text`).

### Deploy

```bash
git push heroku main
```

Or from a feature branch:

```bash
git push heroku ft/pinecone-langchain-rag:main
```

### Post-deploy bootstrap

On Eco dynos, scale web down before one-off commands, then scale back up:

```bash
heroku ps:scale web=0 -a your-app-name
heroku run python manage.py ensure_pinecone_index -a your-app-name
heroku run python manage.py rag_smoke_test -a your-app-name
heroku ps:scale web=1 -a your-app-name
```

`rag_smoke_test` on Heroku uses OpenRouter for embeddings (requires `OPENROUTER_API_KEY`).

### Verify on Heroku

```bash
heroku open -a your-app-name

curl https://your-app-name.herokuapp.com/health/
curl https://your-app-name.herokuapp.com/api/ping/

curl -X POST https://your-app-name.herokuapp.com/api/chat/hello/ \
  -H "Content-Type: application/json" \
  -d '{"question": "what is the capital of canada?"}'

curl -X POST https://your-app-name.herokuapp.com/api/chat/rag/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What vector database does the platform use?"}'
```

### Alternative: push image from local Docker

```bash
heroku container:login
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `404` on `/api/ping` | Missing trailing slash | Use `/api/ping/` |
| `503` on `/api/chat/hello/` (local) | Ollama unreachable | `docker compose up` and `pull_ollama_models` |
| `503` on `/api/chat/hello/` (Heroku) | OpenRouter misconfigured | Set `OPENROUTER_API_KEY` on Heroku |
| `400` on `/api/chat/rag/` | Empty Pinecone index | Run `rag_smoke_test` (local or `heroku run`) to seed data |
| `PINECONE_API_KEY is not set` | Env not loaded | Add key to `.env`, then `docker compose up -d --force-recreate web` |
| Heroku env changes ignored | Container not recreated | Redeploy or `heroku restart` after `config:set` |

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
| `OLLAMA_EMBEDDING_MODEL` | Embedding model (local) | `nomic-embed-text` |
| `EMBEDDING_DIMENSION` | Vector dimension (must match index) | `768` (local), `1536` (Heroku) |
| `OPENROUTER_API_KEY` | OpenRouter API key (Heroku) | — |
| `OPENROUTER_MODEL` | Chat model (Heroku) | `~anthropic/claude-sonnet-latest` |
| `OPENROUTER_EMBEDDING_MODEL` | Embedding model (Heroku) | `openai/text-embedding-3-small` |
| `OPENROUTER_SITE_URL` | HTTP-Referer header for OpenRouter | — |
| `OPENROUTER_SITE_NAME` | X-OpenRouter-Title header | `AI Chatbot Platform` |

## License

Add your license here.
