# ChatBot

A Django web application containerized with Docker and backed by PostgreSQL.

## Tech stack

- **Python** 3.12
- **Django** 5.x
- **PostgreSQL** 16
- **Gunicorn** (production)
- **Docker Compose**

## Project structure

```
ChatBot/
├── config/                 # Django project settings and URL routing
├── core/                   # Starter Django app
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── Dockerfile
├── entrypoint.sh           # Runs migrations before the app starts
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

The development compose file mounts your local code into the container, so changes are picked up by Django's development server without rebuilding the image.

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

## Production

Use the production compose file, which runs Gunicorn instead of Django's development server:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Before deploying to production:

1. Set `DEBUG=False` in `.env`
2. Use a strong, unique `SECRET_KEY`
3. Set `ALLOWED_HOSTS` to your domain(s)
4. Use strong PostgreSQL credentials

## Environment variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1,0.0.0.0` |
| `POSTGRES_DB` | Database name | `chatbot` |
| `POSTGRES_USER` | Database user | `chatbot` |
| `POSTGRES_PASSWORD` | Database password | `chatbot` |
| `POSTGRES_HOST` | Database host | `db` |
| `POSTGRES_PORT` | Database port | `5432` |

## License

Add your license here.
