# TaskTrams 🚀

A **Python microservices** project built with **FastAPI**, **PostgreSQL**, **NATS**, and **Docker**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        CLIENT                           │
│              (Browser / Swagger UI / curl)              │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP  :8000
                       ▼
┌──────────────────────────────────────────────────────────┐
│                   API GATEWAY  :8000                     │
│          FastAPI  +  httpx reverse proxy                 │
│      Swagger UI → http://localhost:8000/docs             │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP  :8001  (httpx proxy)
                     ▼
┌──────────────────────────────────────────────────────────┐
│                 USER SERVICE  :8001                      │
│       FastAPI  +  SQLAlchemy  +  asyncpg                 │
│       Routes: /users/register  /login  /me               │
│               /users/verify-email                        │
└──────┬──────────────────────────────┬────────────────────┘
       │ SQL                          │ NATS publish
       ▼                             ▼
┌──────────────┐         ┌───────────────────────────────┐
│  PostgreSQL  │         │      NATS Broker  :4222       │
│    :5432     │         │   (nats:2.10-alpine)          │
│  user_service│         └──────────────┬────────────────┘
│  notif_svc   │                        │ subscribe
└──────────────┘                        ▼
                          ┌─────────────────────────────┐
                          │   NOTIFICATION SERVICE      │
                          │  Pure asyncio NATS consumer │
                          │  Handles:                   │
                          │   • user.registered         │
                          │   • user.logged_in          │
                          │   • user.get_user           │
                          └─────────────────────────────┘
```

### Request Flow (Register example)

```
Swagger UI
  → POST /users/register  (Gateway :8000)
  → httpx proxy
  → POST /users/register  (User Service :8001)
  → Saves user to PostgreSQL
  → Publishes "user.registered" event to NATS :4222
  → Notification Service receives event & logs email + token
```

---

## Project Structure

```
tasktrams/
├── api-gateway/                # HTTP reverse proxy (port 8000)
│   ├── app/
│   │   ├── main.py             # FastAPI app + httpx lifespan
│   │   ├── config.py           # GatewaySettings (USER_SERVICE_URL)
│   │   └── routes/
│   │       └── users.py        # Proxy routes: register, login, me, verify-email
│   ├── Dockerfile
│   └── requirements.txt
│
├── user-service/               # Auth microservice (port 8001)
│   ├── app/
│   │   ├── main.py             # FastAPI app (DB init + NATS lifespan)
│   │   ├── config.py           # app_config (DB URL, JWT, etc.)
│   │   ├── models/user.py      # SQLAlchemy User model
│   │   ├── schemas/            # Pydantic schemas (auth, event, token)
│   │   ├── routes/users.py     # register, login, /me, verify-email
│   │   ├── services/           # jwt_handler, auth_service, email_verification
│   │   ├── repository/         # DB queries
│   │   ├── database/           # engine, session, Base
│   │   └── messaging/
│   │       └── nats_client.py  # NATS connect + publish_event
│   ├── Dockerfile
│   └── requirements.txt
│
├── notification-service/       # NATS event consumer (no HTTP port)
│   ├── app/
│   │   ├── main.py             # asyncio entry point
│   │   └── messaging/
│   │       └── nats_client.py  # connect + subscribe_to_events
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker/
│   └── postgres/
│       └── init.sql            # Creates user_service + notification_service DBs
│
├── docker-compose.yml          # Orchestrates all 5 services
├── .env                        # Local secrets (git-ignored)
├── .env.example                # Template — copy to .env
├── main.py                     # Local dev runner (user-service only)
└── requirements.txt            # Root venv requirements
```

---

## API Reference

All requests go through the **API Gateway** at `http://localhost:8000`.  
Swagger UI: **http://localhost:8000/docs**

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Gateway status + user-service probe |

### Users

| Method | Path | Body / Params | Auth | Description |
|--------|------|--------------|------|-------------|
| `POST` | `/users/register` | `username`, `email`, `password`, `confirm_password` | ❌ | Register new user. Fires `user.registered` NATS event. |
| `POST` | `/users/login` | `username`, `password` | ❌ | Login. Returns JWT. Fires `user.logged_in` event. |
| `GET` | `/users/me` | — | ✅ Bearer | Get current user info. |
| `GET` | `/users/verify-email` | `?token=<token>` | ❌ | Verify email with token from registration event. |

### NATS Events Published by User Service

| Subject | Payload Fields | Triggered by |
|---------|---------------|--------------|
| `user.registered` | `email`, `token`, `url`, `message` | POST /users/register |
| `user.logged_in` | `username`, `email`, `access_token` | POST /users/login |
| `user.get_user` | `username`, `email` | GET /users/me |

---

## Running with Docker (recommended)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Steps

```bash
# 1. Clone the repo
git clone <repo-url>
cd tasktrams

# 2. Copy and edit environment variables (optional — defaults work out of the box)
cp .env.example .env

# 3. Build and start all services
docker compose up --build

# 4. Open Swagger UI
#    http://localhost:8000/docs
```

### Stop everything

```bash
docker compose down

# Also remove the postgres volume (wipes DB data):
docker compose down -v
```

### Individual service logs

```bash
docker compose logs -f api-gateway
docker compose logs -f user-service
docker compose logs -f notification-service
docker compose logs -f nats
docker compose logs -f postgres
```

---

## Running Locally (without Docker)

### Prerequisites

- Python 3.11+
- PostgreSQL running on `localhost:5432`
- NATS server on `localhost:4222`
  ```bash
  # Install NATS server: https://docs.nats.io/running-a-nats-service/introduction/installation
  nats-server
  # or via Docker:
  docker run -d -p 4222:4222 nats:2.10-alpine
  ```

### Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 2. Install root dependencies
pip install -r requirements.txt

# 3. Copy and fill in .env
cp .env.example .env
# Edit .env with your local postgres credentials
```

### Create the databases

```sql
-- In psql or pgAdmin:
CREATE DATABASE user_service;
CREATE DATABASE notification_service;
```

### Start each service in a separate terminal

**Terminal 1 — User Service**
```bash
cd user-service
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 2 — API Gateway**
```bash
cd api-gateway
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 3 — Notification Service**
```bash
cd notification-service
python -m app.main
```

Open **http://localhost:8000/docs** to use Swagger.

---

## Environment Variables

| Variable | Service | Default | Description |
|----------|---------|---------|-------------|
| `USER_DATABASE_URL` | user-service | — | asyncpg PostgreSQL URL |
| `NOTIFICATION_DATABASE_URL` | user-service | — | asyncpg PostgreSQL URL |
| `SECRET_KEY` | user-service | — | JWT signing secret |
| `ALGORITHMS` | user-service | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTE` | user-service | `60` | Token expiry (minutes) |
| `NATS_URL` | user-service, notification-service | `nats://localhost:4222` | NATS broker URL |
| `USER_SERVICE_URL` | api-gateway | `http://127.0.0.1:8001` | User service base URL |
| `GATEWAY_PORT` | api-gateway | `8000` | Gateway listen port |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| HTTP Proxy | [httpx](https://www.python-httpx.org/) |
| ORM | [SQLAlchemy 2 (async)](https://docs.sqlalchemy.org/en/20/) |
| Database Driver | [asyncpg](https://magicstack.github.io/asyncpg/) |
| Database | [PostgreSQL 16](https://www.postgresql.org/) |
| Messaging | [NATS](https://nats.io/) via [nats-py](https://github.com/nats-io/nats.py) |
| Auth | JWT ([python-jose](https://github.com/mpdavis/python-jose)) |
| Password Hashing | [bcrypt](https://pypi.org/project/bcrypt/) |
| Settings | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| ASGI Server | [uvicorn](https://www.uvicorn.org/) |
| Containerisation | [Docker](https://www.docker.com/) + Docker Compose |
