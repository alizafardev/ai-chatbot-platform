# ChatBot

A Django web application containerized with Docker and backed by PostgreSQL.

## Tech stack

- **Python** 3.12
- **Django** 5.x
- **PostgreSQL** 16
- **Gunicorn** (production / Heroku)
- **Docker Compose** (local development)

## Project structure

```
ChatBot/
├── config/                 # Django project settings and URL routing
├── core/                   # Starter Django app
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

## License

Add your license here.
