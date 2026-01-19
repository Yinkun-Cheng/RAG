# RAG Backend

Go backend for RAG Test Case Management System.

## ✅ Status: Phase 1.1 Complete

Backend project initialization completed with:
- ✅ Go project structure created
- ✅ Configuration module (Viper)
- ✅ Logging module (Zap)
- ✅ Basic HTTP server with Gin
- ✅ Middleware (CORS, Logger, Recovery)
- ✅ Common response structures
- ✅ Health check endpoint

## Structure

```
backend/
├── cmd/
│   └── server/          # Application entry point
│       └── main.go      # Main program with server setup
├── internal/
│   ├── api/             # API layer
│   │   ├── handler/     # HTTP handlers
│   │   ├── middleware/  # Middleware (CORS, Logger, Recovery)
│   │   └── router/      # Routes
│   ├── domain/          # Domain models
│   │   ├── prd/
│   │   ├── testcase/
│   │   └── common/      # Common response structures
│   ├── repository/      # Data access layer
│   │   ├── postgres/
│   │   └── weaviate/
│   ├── service/         # Business logic
│   │   ├── prd/
│   │   ├── testcase/
│   │   ├── rag/
│   │   └── import/
│   └── pkg/             # Utilities
│       ├── config/      # Configuration loader (Viper)
│       ├── logger/      # Logger (Zap)
│       └── utils/
├── migrations/          # Database migrations
├── scripts/             # Helper scripts
├── config.yaml          # Configuration file
├── .env.example         # Environment variables example
├── Makefile             # Make commands
└── README.md            # This file
```

## Quick Start

### 1. Install Dependencies

```bash
go mod download
```

Or using Make:
```bash
make install-deps
```

### 2. Configuration

Copy environment variables:
```bash
cp .env.example .env
```

Edit `config.yaml` to configure database connections.

### 3. Run Server

```bash
go run cmd/server/main.go
```

Or using Make:
```bash
make run
```

### 4. Test

Health check:
```bash
curl http://localhost:8080/health
```

PowerShell test script:
```powershell
.\test-server.ps1
```

## Available Commands

### Make Commands

- `make run` - Run the application
- `make build` - Build the application
- `make test` - Run tests
- `make clean` - Clean build artifacts
- `make install-deps` - Install dependencies
- `make fmt` - Format code
- `make lint` - Lint code

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "RAG Backend is running"
}
```

### API v1

```
GET /api/v1/ping
```

Response:
```json
{
  "message": "pong"
}
```

## Configuration

See `config.yaml` for all configuration options:

- Server port and mode
- PostgreSQL connection
- Weaviate connection
- File storage settings
- Logging configuration

## Development

### Tech Stack

- **Language**: Go 1.21+
- **Web Framework**: Gin
- **ORM**: GORM
- **Database**: PostgreSQL 15+
- **Vector DB**: Weaviate
- **Configuration**: Viper
- **Logging**: Zap

### Architecture

Layered architecture:

1. **API Layer**: HTTP request/response handling
2. **Service Layer**: Business logic
3. **Repository Layer**: Data access
4. **Domain Layer**: Domain models

## Next Steps

- [ ] Database migrations (Phase 2.1)
- [ ] GORM models
- [ ] Module management API
- [ ] Tag management API

See [中文文档](README_CN.md) for Chinese documentation.
