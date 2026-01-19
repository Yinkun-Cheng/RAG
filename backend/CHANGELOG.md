# Changelog

All notable changes to the RAG Backend project will be documented in this file.

## [0.1.0] - 2025-01-19

### Added - Phase 1.1: 后端项目初始化

#### Project Structure
- Created complete Go project directory structure
- Organized code following layered architecture pattern
- Set up internal packages for API, domain, repository, service, and utilities

#### Core Modules
- **Configuration Module** (`internal/pkg/config`)
  - Implemented Viper-based configuration loader
  - Support for YAML files and environment variables
  - Structured configuration for server, database, storage, and logging
  - Helper methods for DSN and URL generation

- **Logging Module** (`internal/pkg/logger`)
  - Implemented Zap-based structured logging
  - Support for multiple log levels (debug, info, warn, error, fatal)
  - Support for JSON and console formats
  - Convenient logging functions

#### HTTP Server
- **Main Application** (`cmd/server/main.go`)
  - Complete server startup flow
  - Configuration loading
  - Logger initialization
  - Gin router setup
  - Health check endpoint
  - API v1 group structure
  - Graceful shutdown with signal handling

#### Middleware
- **CORS Middleware** (`internal/api/middleware/cors.go`)
  - Cross-Origin Resource Sharing support
  - Configurable allowed origins and methods

- **Logger Middleware** (`internal/api/middleware/logger.go`)
  - HTTP request logging
  - Latency tracking
  - Client IP logging

- **Recovery Middleware** (`internal/api/middleware/recovery.go`)
  - Panic recovery
  - Error logging
  - User-friendly error responses

#### Domain Models
- **Common Response** (`internal/domain/common/response.go`)
  - Standard API response structure
  - Success and error response helpers
  - Paginated response structure

#### Configuration Files
- `config.yaml` - Main configuration file
- `.env.example` - Environment variables template
- `Makefile` - Build and development commands

#### Documentation
- `README.md` - English documentation
- `README_CN.md` - Chinese documentation
- API endpoint documentation
- Configuration guide
- Development guide

#### Scripts
- `start.ps1` - Server startup script
- `test-server.ps1` - API testing script

#### Dependencies
- gin-gonic/gin v1.10.0 - Web framework
- gorm.io/gorm v1.25.5 - ORM
- gorm.io/driver/postgres v1.5.4 - PostgreSQL driver
- spf13/viper v1.18.2 - Configuration management
- go.uber.org/zap v1.26.0 - Structured logging
- google/uuid v1.6.0 - UUID generation

### API Endpoints

#### Health Check
- `GET /health` - Server health check

#### API v1
- `GET /api/v1/ping` - Ping test endpoint

### Technical Highlights

1. **Layered Architecture**
   - Clear separation of concerns
   - API, Service, Repository, Domain layers

2. **Middleware System**
   - CORS support
   - Request logging
   - Panic recovery

3. **Configuration Management**
   - Flexible configuration loading
   - Support for multiple sources
   - Structured configuration

4. **Logging System**
   - Structured logging with Zap
   - Multiple log levels
   - JSON and console formats

5. **Graceful Shutdown**
   - Signal handling
   - Clean resource cleanup

### Next Steps

- [ ] Database migrations (Phase 2.1)
- [ ] GORM models
- [ ] Module management API
- [ ] Tag management API
- [ ] Docker configuration

---

## Version History

- **0.1.0** (2025-01-19) - Initial backend project setup
