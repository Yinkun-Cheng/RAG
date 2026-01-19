# Docker Configuration

Docker setup for RAG Test Case Management System.

## Quick Start

1. Copy environment file:
```bash
cp .env.example .env
```

2. Start PostgreSQL:
```bash
docker-compose up -d postgres
```

3. Check status:
```bash
docker-compose ps
```

4. View logs:
```bash
docker-compose logs -f postgres
```

## Services

- **postgres**: PostgreSQL 15 database
- **backend**: Go API server (to be added)
- **frontend**: React application (to be added)

## Database Connection

- Host: localhost
- Port: 5432
- User: rag_user
- Password: rag_password
- Database: rag_db

## Stopping Services

```bash
docker-compose down
```

## Removing Data

```bash
docker-compose down -v
```
