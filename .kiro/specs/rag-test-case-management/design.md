# Design Document

## System Architecture

### Overview

The system follows a three-tier architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - UI Components (Ant Design)                           │
│  - State Management (React Query + Zustand)             │
│  - Routing (React Router)                               │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                    Backend (Go + Gin)                    │
│  - API Layer (HTTP Handlers)                            │
│  - Service Layer (Business Logic)                       │
│  - Repository Layer (Data Access)                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────┬──────────────────────────────────┐
│   PostgreSQL         │        Weaviate                  │
│   (Structured Data)  │    (Vector Database)             │
└──────────────────────┴──────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Language: Go 1.21+
- Web Framework: Gin
- ORM: GORM
- Database: PostgreSQL 15+
- Vector DB: Weaviate (shared with Dify)
- Configuration: Viper
- Logging: Zap
- API Docs: Swagger

**Frontend:**
- Framework: React 18 + TypeScript 5
- Build Tool: Vite 5
- UI Library: Ant Design 5.x
- State Management: React Query + Zustand
- Router: React Router v6
- HTTP Client: Axios
- Styling: Tailwind CSS

**Deployment:**
- Containerization: Docker + Docker Compose
- Reverse Proxy: Nginx
- Database: PostgreSQL (Docker)
- Vector DB: Weaviate (shared with Dify)

## Database Design

### PostgreSQL Schema

#### modules
```sql
CREATE TABLE modules (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id VARCHAR(36) REFERENCES modules(id),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

#### prd_documents
```sql
CREATE TABLE prd_documents (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    version VARCHAR(20) NOT NULL,
    module_id VARCHAR(36) REFERENCES modules(id),
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

#### test_cases
```sql
CREATE TABLE test_cases (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    prd_id VARCHAR(36) REFERENCES prd_documents(id),
    prd_version VARCHAR(20),
    module_id VARCHAR(36) REFERENCES modules(id),
    preconditions TEXT,
    expected_result TEXT NOT NULL,
    priority VARCHAR(10) DEFAULT 'P2',
    type VARCHAR(50) DEFAULT 'functional',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);
```

#### test_steps
```sql
CREATE TABLE test_steps (
    id VARCHAR(36) PRIMARY KEY,
    test_case_id VARCHAR(36) REFERENCES test_cases(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    action TEXT NOT NULL,
    test_data TEXT,
    expected TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### test_step_screenshots
```sql
CREATE TABLE test_step_screenshots (
    id VARCHAR(36) PRIMARY KEY,
    test_step_id VARCHAR(36) REFERENCES test_steps(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### tags
```sql
CREATE TABLE tags (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### test_case_tags & prd_tags
```sql
CREATE TABLE test_case_tags (
    test_case_id VARCHAR(36) REFERENCES test_cases(id) ON DELETE CASCADE,
    tag_id VARCHAR(36) REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (test_case_id, tag_id)
);

CREATE TABLE prd_tags (
    prd_id VARCHAR(36) REFERENCES prd_documents(id) ON DELETE CASCADE,
    tag_id VARCHAR(36) REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (prd_id, tag_id)
);
```

### Weaviate Schema

#### PRDDocument Collection
```json
{
  "class": "PRDDocument",
  "vectorizer": "none",
  "properties": [
    {"name": "documentId", "dataType": ["string"]},
    {"name": "code", "dataType": ["string"]},
    {"name": "title", "dataType": ["string"]},
    {"name": "version", "dataType": ["string"]},
    {"name": "content", "dataType": ["text"]},
    {"name": "moduleId", "dataType": ["string"]},
    {"name": "moduleName", "dataType": ["string"]},
    {"name": "status", "dataType": ["string"]},
    {"name": "tags", "dataType": ["string[]"]},
    {"name": "createdAt", "dataType": ["date"]},
    {"name": "updatedAt", "dataType": ["date"]}
  ]
}
```

#### TestCase Collection
```json
{
  "class": "TestCase",
  "vectorizer": "none",
  "properties": [
    {"name": "caseId", "dataType": ["string"]},
    {"name": "code", "dataType": ["string"]},
    {"name": "title", "dataType": ["string"]},
    {"name": "prdId", "dataType": ["string"]},
    {"name": "prdCode", "dataType": ["string"]},
    {"name": "prdVersion", "dataType": ["string"]},
    {"name": "moduleId", "dataType": ["string"]},
    {"name": "moduleName", "dataType": ["string"]},
    {"name": "preconditions", "dataType": ["text"]},
    {"name": "stepsText", "dataType": ["text"]},
    {"name": "expectedResult", "dataType": ["text"]},
    {"name": "priority", "dataType": ["string"]},
    {"name": "type", "dataType": ["string"]},
    {"name": "tags", "dataType": ["string[]"]},
    {"name": "status", "dataType": ["string"]},
    {"name": "createdAt", "dataType": ["date"]},
    {"name": "updatedAt", "dataType": ["date"]}
  ]
}
```

## API Design

### Base URL
```
http://localhost:8080/api/v1
```

### Response Format
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### Key Endpoints

#### Modules
- `GET /modules/tree` - Get module tree
- `POST /modules` - Create module
- `PUT /modules/:id` - Update module
- `DELETE /modules/:id` - Delete module

#### PRDs
- `GET /prds` - List PRDs (with pagination, filters)
- `GET /prds/:id` - Get PRD detail
- `POST /prds` - Create PRD
- `PUT /prds/:id` - Update PRD
- `DELETE /prds/:id` - Delete PRD
- `GET /prds/:id/versions` - Get version history
- `GET /prds/:id/versions/:version` - Get specific version

#### Test Cases
- `GET /testcases` - List test cases
- `GET /testcases/:id` - Get test case detail
- `POST /testcases` - Create test case
- `PUT /testcases/:id` - Update test case
- `DELETE /testcases/:id` - Delete test case
- `POST /testcases/batch-delete` - Batch delete

#### File Upload
- `POST /upload/screenshot` - Upload screenshot
- `DELETE /upload/:id` - Delete file

#### Tags
- `GET /tags` - List all tags
- `POST /tags` - Create tag
- `PUT /tags/:id` - Update tag
- `DELETE /tags/:id` - Delete tag

#### Import
- `POST /import/excel` - Import from Excel
- `POST /import/xmind` - Import from XMind
- `POST /import/word` - Import from Word

#### Search & RAG
- `POST /search` - Semantic search
- `GET /recommend/:prd_id` - Get recommendations
- `POST /impact-analysis` - Analyze impact

#### Dify Integration
- `POST /dify/retrieval` - Dify retrieval endpoint

#### Statistics
- `GET /statistics` - Get statistics

## Backend Architecture

### Project Structure
```
backend/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── api/
│   │   ├── handler/
│   │   ├── middleware/
│   │   └── router/
│   ├── domain/
│   │   ├── prd/
│   │   ├── testcase/
│   │   └── common/
│   ├── repository/
│   │   ├── postgres/
│   │   └── weaviate/
│   ├── service/
│   │   ├── prd/
│   │   ├── testcase/
│   │   ├── rag/
│   │   └── import/
│   └── pkg/
│       ├── config/
│       ├── logger/
│       └── utils/
├── migrations/
├── go.mod
└── Dockerfile
```

### Layer Responsibilities

**API Layer (Handler):**
- HTTP request/response handling
- Input validation
- Error handling
- Response formatting

**Service Layer:**
- Business logic implementation
- Transaction management
- Cross-domain operations
- External service integration

**Repository Layer:**
- Database operations (CRUD)
- Query building
- Data mapping

**Domain Layer:**
- Entity definitions
- Business rules
- Value objects

## Frontend Architecture

### Project Structure
```
frontend/
├── src/
│   ├── api/
│   ├── components/
│   │   ├── Layout/
│   │   ├── ModuleTree/
│   │   ├── MarkdownEditor/
│   │   ├── ImageUpload/
│   │   └── TagSelect/
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── PRD/
│   │   ├── TestCase/
│   │   ├── Import/
│   │   └── Search/
│   ├── hooks/
│   ├── store/
│   ├── types/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── Dockerfile
```

### State Management

**React Query (Server State):**
- API data fetching
- Caching
- Background updates
- Optimistic updates

**Zustand (Client State):**
- UI state (selected module, search query)
- User preferences
- Temporary form data

### Key Components

**ModuleTree:**
- Tree structure display
- Expand/collapse
- Context menu
- Drag-and-drop

**MarkdownEditor:**
- Monaco Editor integration
- Real-time preview
- Toolbar
- Full-screen mode

**ImageUpload:**
- Drag-and-drop upload
- Multiple files
- Preview
- Progress indicator

**TagSelect:**
- Multi-select dropdown
- Create new tags
- Color display

## Data Flow

### PRD Creation Flow
```
User Input → Form Validation → API Call → Service Layer
→ Save to PostgreSQL → Generate Embedding → Save to Weaviate
→ Return Success → Update UI
```

### Test Case Creation Flow
```
User Input → Form Validation → Upload Screenshots → API Call
→ Service Layer → Transaction Start → Save Test Case
→ Save Test Steps → Save Screenshots → Generate Embedding
→ Save to Weaviate → Transaction Commit → Return Success
→ Update UI
```

### Semantic Search Flow
```
User Query → API Call → Generate Query Embedding
→ Search Weaviate → Apply Filters → Rank Results
→ Fetch Full Data from PostgreSQL → Return Results
→ Display with Highlighting
```

## Security Considerations

### Input Validation
- Validate all user inputs
- Sanitize file uploads
- Prevent SQL injection (use parameterized queries)
- Prevent XSS (escape HTML)

### File Upload Security
- Validate file types
- Limit file sizes
- Generate unique filenames
- Store outside web root

### API Security
- Rate limiting
- Request size limits
- CORS configuration
- Error message sanitization

## Performance Optimization

### Database
- Add indexes on frequently queried columns
- Use connection pooling
- Implement pagination
- Use prepared statements

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- Virtual scrolling for long lists
- Debounce search inputs

### Caching
- React Query automatic caching
- Static asset caching
- API response caching (where appropriate)

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Port 80)                      │
│  /          → React Frontend                             │
│  /api       → Go Backend (Port 8080)                     │
│  /uploads   → Static Files                               │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌─────────┐        ┌──────────┐        ┌──────────┐
   │ React   │        │ Go API   │        │  Nginx   │
   │Container│        │Container │        │Container │
   └─────────┘        └──────────┘        └──────────┘
                            │
                            ▼
                      ┌──────────┐
                      │PostgreSQL│
                      │Container │
                      └──────────┘
                            │
                            ▼
                      ┌──────────┐
                      │ Weaviate │
                      │(Dify's)  │
                      └──────────┘
```

### Docker Compose Services
- `postgres`: PostgreSQL database
- `backend`: Go API server
- `frontend`: React application
- `nginx`: Reverse proxy
- Weaviate: Reuse Dify's instance

## Error Handling Strategy

### Backend
- Use custom error types
- Log all errors with context
- Return user-friendly messages
- Include error codes for client handling

### Frontend
- Display toast notifications for errors
- Show inline validation errors
- Provide retry mechanisms
- Log errors to console (dev mode)

## Testing Strategy

### Backend Testing
- Unit tests for services
- Integration tests for repositories
- API tests for handlers
- Test coverage target: 70%+

### Frontend Testing
- Component tests (React Testing Library)
- Integration tests for pages
- E2E tests (optional, Playwright)
- Test coverage target: 60%+

## Monitoring and Logging

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARN, ERROR
- Log rotation (daily)
- Include request IDs for tracing

### Metrics
- API response times
- Database query times
- Error rates
- Upload success rates

## Configuration Management

### Backend Config (config.yaml)
```yaml
server:
  port: 8080
  mode: debug

database:
  postgres:
    host: localhost
    port: 5432
    user: rag_user
    password: rag_password
    dbname: rag_db
  
  weaviate:
    host: weaviate
    port: 8080
    scheme: http
    api_key: WVF5YThaHlkYwhGUSmCRgsX3tD5ngdN8pkih

storage:
  type: local
  local_path: ./uploads
  max_file_size: 10485760

logging:
  level: info
  format: json
  output: stdout
```

### Frontend Config (.env)
```env
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_UPLOAD_MAX_SIZE=10485760
```

## Migration Strategy

### Database Migrations
- Use numbered migration files
- Apply migrations on startup
- Track applied migrations
- Support rollback

### Data Migration
- Provide scripts for bulk data import
- Support incremental migration
- Validate data after migration

## Future Enhancements

### Phase 2 Features
- User authentication and authorization
- Team collaboration
- Test execution tracking
- Test report generation
- Integration with CI/CD
- Mobile responsive design
- Real-time collaboration
- Advanced analytics

### Scalability Considerations
- Horizontal scaling of API servers
- Database read replicas
- CDN for static assets
- Message queue for async tasks
- Microservices architecture (if needed)
