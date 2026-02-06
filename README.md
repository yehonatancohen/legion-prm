# Distributed Agent Management Platform

## Phase 1: Core Backend

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (optional, for local intellisense)

### Quick Start

1.  **Start Services**
    ```bash
    docker-compose up -d --build
    ```

2.  **Run Database Migrations**
    Run this command inside the backend container (or locally if env is setup):
    ```bash
    docker-compose exec backend alembic revision --autogenerate -m "Initial tables"
    docker-compose exec backend alembic upgrade head
    ```

3.  **Access API**
    - OpenAPI Docs: http://localhost:8000/docs
    - Redirect Endpoint: http://localhost:8000/r/{short_code}

### Development
- The `backend` code is mounted as a volume, so changes in `backend/` are hot-reloaded.
- Database runs on port 5432.
- Redis runs on port 6379.
"# legion-prm" 
