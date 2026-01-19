# RAG Backend

Go backend for RAG Test Case Management System.

## Structure

```
backend/
├── cmd/
│   └── server/          # Application entry point
├── internal/
│   ├── api/             # API layer
│   │   ├── handler/     # HTTP handlers
│   │   ├── middleware/  # Middleware
│   │   └── router/      # Routes
│   ├── domain/          # Domain models
│   │   ├── prd/
│   │   ├── testcase/
│   │   └── common/
│   ├── repository/      # Data access layer
│   │   ├── postgres/
│   │   └── weaviate/
│   ├── service/         # Business logic
│   │   ├── prd/
│   │   ├── testcase/
│   │   ├── rag/
│   │   └── import/
│   └── pkg/             # Utilities
│       ├── config/
│       ├── logger/
│       └── utils/
├── migrations/          # Database migrations
└── scripts/             # Helper scripts
```

## Getting Started

1. Install dependencies:
```bash
go mod download
```

2. Configure database in `config.yaml`

3. Run the server:
```bash
go run cmd/server/main.go
```

## Development

- Go version: 1.21+
- Database: PostgreSQL 15+
- Vector DB: Weaviate
