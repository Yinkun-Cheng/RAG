# Requirements Document

## Introduction

This document specifies the requirements for implementing the complete backend API for the RAG Test Case Management System. The system serves as a specialized external knowledge base for AI Agents (like Dify), providing structured test knowledge retrieval capabilities. The backend will implement database models, RESTful APIs, vector storage integration, and AI-powered features for test case management.

## Glossary

- **System**: The RAG Test Case Management Backend API
- **Database**: PostgreSQL relational database for structured data storage
- **Vector_Store**: Weaviate vector database for semantic search capabilities
- **Agent**: AI Agent (e.g., Dify) that consumes the external knowledge base API
- **PRD**: Product Requirements Document
- **Test_Case**: Test case with steps, preconditions, and expected results
- **Module**: Hierarchical organizational unit for PRDs and test cases
- **Tag**: Label for categorizing PRDs and test cases
- **App_Version**: Application version identifier (e.g., v1.0.0)
- **Sync_Status**: Status of data synchronization to Vector_Store (syncing, synced, failed)
- **Priority**: Test case priority level (high, medium, low)
- **Test_Type**: Type of test (functional, performance, security, ui)
- **Status**: Entity status (active, draft, archived, deprecated)

## Requirements

### Requirement 1: Database Schema and Models

**User Story:** As a developer, I want well-defined database models with proper relationships, so that data integrity is maintained and queries are efficient.

#### Acceptance Criteria

1. THE System SHALL define GORM models for Project, AppVersion, Module, Tag, PRD, TestCase, and TestStep entities
2. THE System SHALL use UUID as primary keys for all entities
3. THE System SHALL implement soft delete support using GORM's DeletedAt field
4. THE System SHALL define foreign key relationships between entities (Project → AppVersion, Module → PRD, PRD → TestCase, TestCase → TestStep)
5. THE System SHALL add database indexes on frequently queried fields (project_id, app_version_id, module_id, status, created_at)
6. THE System SHALL implement GORM hooks for automatic timestamp management (CreatedAt, UpdatedAt)
7. THE System SHALL support JSON fields for storing arrays (tags, screenshots)

### Requirement 2: Database Migrations

**User Story:** As a developer, I want automated database migrations, so that schema changes are version-controlled and reproducible.

#### Acceptance Criteria

1. THE System SHALL provide migration scripts for creating all database tables
2. THE System SHALL support migration rollback functionality
3. THE System SHALL include seed data migrations for initial setup
4. WHEN migrations are executed, THE System SHALL log migration status and errors
5. THE System SHALL validate database connection before running migrations

### Requirement 3: Project and Version Management API

**User Story:** As a user, I want to manage projects and their versions, so that I can organize test artifacts by project and version.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/projects, THE System SHALL create a new project with name and description
2. WHEN a GET request is made to /api/v1/projects, THE System SHALL return a paginated list of projects with PRD and test case counts
3. WHEN a GET request is made to /api/v1/projects/:id, THE System SHALL return project details including all app versions
4. WHEN a PUT request is made to /api/v1/projects/:id, THE System SHALL update project information
5. WHEN a DELETE request is made to /api/v1/projects/:id, THE System SHALL soft delete the project
6. WHEN a POST request is made to /api/v1/projects/:id/versions, THE System SHALL create a new app version for the project
7. WHEN a GET request is made to /api/v1/projects/:id/versions, THE System SHALL return all versions for the project ordered by creation date

### Requirement 4: Module Management API

**User Story:** As a user, I want to manage hierarchical modules, so that I can organize PRDs and test cases in a tree structure.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/modules, THE System SHALL create a new module with name and optional parent_id
2. WHEN a GET request is made to /api/v1/modules, THE System SHALL return modules in tree structure format
3. WHEN a GET request is made to /api/v1/modules/:id, THE System SHALL return module details including full path
4. WHEN a PUT request is made to /api/v1/modules/:id, THE System SHALL update module information
5. WHEN a DELETE request is made to /api/v1/modules/:id, THE System SHALL prevent deletion if module has children or associated PRDs/test cases
6. WHEN a module is moved to a different parent, THE System SHALL update the full path for all descendants
7. THE System SHALL validate that circular references are not created in the module hierarchy

### Requirement 5: Tag Management API

**User Story:** As a user, I want to manage tags, so that I can categorize and filter PRDs and test cases.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/tags, THE System SHALL create a new tag with name and color
2. WHEN a GET request is made to /api/v1/tags, THE System SHALL return all tags with usage counts
3. WHEN a PUT request is made to /api/v1/tags/:id, THE System SHALL update tag information
4. WHEN a DELETE request is made to /api/v1/tags/:id, THE System SHALL remove tag associations from PRDs and test cases
5. THE System SHALL automatically calculate usage count based on PRD and test case associations

### Requirement 6: PRD Management API

**User Story:** As a user, I want to manage PRD documents with version control, so that I can track requirement changes over time.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/prds, THE System SHALL create a new PRD with title, content, project_id, app_version_id, module_id, and tags
2. WHEN a GET request is made to /api/v1/prds, THE System SHALL return paginated PRDs with filters for project_id, app_version_id, module_id, status, and tags
3. WHEN a GET request is made to /api/v1/prds/:id, THE System SHALL return complete PRD details including content
4. WHEN a PUT request is made to /api/v1/prds/:id, THE System SHALL update PRD and increment version number
5. WHEN a DELETE request is made to /api/v1/prds/:id, THE System SHALL soft delete the PRD
6. WHEN a PRD is created or updated, THE System SHALL set sync_status to "syncing" and trigger Vector_Store synchronization
7. THE System SHALL support status transitions (draft → published → archived)
8. THE System SHALL validate that app_version_id belongs to the specified project_id

### Requirement 7: Test Case Management API

**User Story:** As a user, I want to manage test cases with detailed steps and screenshots, so that I can document test procedures comprehensively.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/testcases, THE System SHALL create a new test case with title, project_id, app_version_id, module_id, priority, type, precondition, expected_result, steps, and tags
2. WHEN a GET request is made to /api/v1/testcases, THE System SHALL return paginated test cases with filters for project_id, app_version_id, module_id, priority, type, status, and tags
3. WHEN a GET request is made to /api/v1/testcases/:id, THE System SHALL return complete test case details including all steps and screenshots
4. WHEN a PUT request is made to /api/v1/testcases/:id, THE System SHALL update test case information and steps
5. WHEN a DELETE request is made to /api/v1/testcases/:id, THE System SHALL soft delete the test case
6. WHEN a test case is created or updated, THE System SHALL set sync_status to "syncing" and trigger Vector_Store synchronization
7. THE System SHALL maintain step order and validate that order values are sequential
8. THE System SHALL support status values (active, deprecated)

### Requirement 8: File Upload API

**User Story:** As a user, I want to upload screenshots for test steps, so that I can provide visual documentation.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/upload, THE System SHALL accept image files (jpg, png, gif)
2. WHEN a file is uploaded, THE System SHALL validate file size does not exceed 10MB
3. WHEN a file is uploaded, THE System SHALL generate a unique filename using UUID
4. WHEN a file is uploaded, THE System SHALL store the file in the configured storage location
5. WHEN a file is uploaded, THE System SHALL return the file URL
6. IF file validation fails, THEN THE System SHALL return a descriptive error message
7. THE System SHALL support local file storage with configurable path

### Requirement 9: Weaviate Vector Store Integration

**User Story:** As a developer, I want automatic synchronization to Weaviate, so that semantic search capabilities are always up-to-date.

#### Acceptance Criteria

1. THE System SHALL define Weaviate schemas for PRD and TestCase classes with appropriate properties
2. WHEN a PRD is created or updated, THE System SHALL extract text content and metadata for vectorization
3. WHEN a test case is created or updated, THE System SHALL combine title, precondition, steps, and expected_result for vectorization
4. WHEN vectorizing content, THE System SHALL include metadata fields (project_id, project_name, app_version, module, priority, type, status, tags, created_at)
5. WHEN synchronization succeeds, THE System SHALL update sync_status to "synced" and set last_sync_time
6. IF synchronization fails, THEN THE System SHALL update sync_status to "failed" and log the error
7. THE System SHALL support batch synchronization for historical data migration
8. THE System SHALL handle Weaviate connection errors gracefully without blocking API operations

### Requirement 10: Semantic Search API

**User Story:** As an Agent, I want to perform semantic search across PRDs and test cases, so that I can find relevant information based on natural language queries.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/search, THE System SHALL accept query text, type filter (prd, testcase, or both), and metadata filters
2. WHEN performing search, THE System SHALL query Weaviate using vector similarity
3. WHEN performing search, THE System SHALL apply metadata filters (project_id, app_version_id, module_id, priority, type, status)
4. WHEN performing search, THE System SHALL return results with content, similarity score, and complete metadata
5. WHEN performing search, THE System SHALL support top_k parameter for result limit (default 10, max 50)
6. WHEN performing search, THE System SHALL support score_threshold parameter for minimum similarity (default 0.7)
7. THE System SHALL return results ordered by similarity score descending

### Requirement 11: Dify External Knowledge Base API

**User Story:** As a Dify Agent, I want to retrieve test knowledge through a standardized API, so that I can answer user questions about test artifacts.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/dify/retrieval, THE System SHALL accept query, top_k, score_threshold, and filters
2. WHEN Dify calls the API, THE System SHALL perform semantic search using the provided query
3. WHEN Dify calls the API, THE System SHALL apply all provided filters (project_id, app_version, module, type, priority, status)
4. WHEN returning results, THE System SHALL format content as readable text including all relevant details
5. WHEN returning results, THE System SHALL include complete metadata for each record
6. WHEN returning results, THE System SHALL include similarity score for each record
7. THE System SHALL support multi-project isolation through project_id filter

### Requirement 12: Impact Analysis API

**User Story:** As a user, I want to analyze the impact of PRD changes, so that I can identify affected test cases.

#### Acceptance Criteria

1. WHEN a POST request is made to /api/v1/impact-analysis, THE System SHALL accept prd_id and change_description
2. WHEN analyzing impact, THE System SHALL retrieve the PRD and its associated test cases
3. WHEN analyzing impact, THE System SHALL use semantic similarity to find related test cases
4. WHEN analyzing impact, THE System SHALL return affected test cases with impact level (high, medium, low)
5. WHEN analyzing impact, THE System SHALL provide reasoning for each affected test case
6. THE System SHALL support impact analysis across different modules using semantic search

### Requirement 13: Recommendation API

**User Story:** As a user, I want to get test case recommendations based on PRDs, so that I can discover related test cases.

#### Acceptance Criteria

1. WHEN a GET request is made to /api/v1/recommend/:prd_id, THE System SHALL retrieve the PRD content
2. WHEN generating recommendations, THE System SHALL use semantic search to find similar test cases
3. WHEN generating recommendations, THE System SHALL prioritize test cases from the same module
4. WHEN generating recommendations, THE System SHALL return test cases with similarity scores
5. WHEN generating recommendations, THE System SHALL provide reasoning for each recommendation
6. THE System SHALL return top 10 recommendations by default

### Requirement 14: Middleware and Error Handling

**User Story:** As a developer, I want comprehensive middleware and error handling, so that the API is robust and maintainable.

#### Acceptance Criteria

1. THE System SHALL implement CORS middleware with configurable allowed origins
2. THE System SHALL implement request logging middleware that logs method, path, status code, and duration
3. THE System SHALL implement recovery middleware that catches panics and returns 500 errors
4. THE System SHALL implement error handling middleware that converts errors to consistent JSON responses
5. WHEN an error occurs, THE System SHALL return responses with code, message, and optional details fields
6. WHEN validation fails, THE System SHALL return 400 status with descriptive error messages
7. WHEN a resource is not found, THE System SHALL return 404 status
8. WHEN a server error occurs, THE System SHALL return 500 status and log the error

### Requirement 15: Response Format and Pagination

**User Story:** As an API consumer, I want consistent response formats and pagination, so that integration is predictable.

#### Acceptance Criteria

1. THE System SHALL return success responses with format: {code: 200, message: "success", data: {...}}
2. THE System SHALL return error responses with format: {code: 4xx/5xx, message: "error description", details: {...}}
3. WHEN returning paginated lists, THE System SHALL include pagination metadata (page, page_size, total, total_pages)
4. WHEN pagination is requested, THE System SHALL support page and page_size query parameters
5. THE System SHALL use default page_size of 20 and maximum page_size of 100
6. THE System SHALL validate pagination parameters and return errors for invalid values

### Requirement 16: Database Connection Management

**User Story:** As a developer, I want robust database connection management, so that the system handles connection issues gracefully.

#### Acceptance Criteria

1. THE System SHALL implement connection pooling for PostgreSQL with configurable pool size
2. THE System SHALL validate database connection on startup
3. WHEN database connection fails, THE System SHALL retry with exponential backoff
4. WHEN database connection is lost, THE System SHALL attempt to reconnect automatically
5. THE System SHALL log database connection status and errors
6. THE System SHALL implement health check endpoint that verifies database connectivity

### Requirement 17: Batch Synchronization Script

**User Story:** As a developer, I want a batch synchronization script, so that I can sync historical data to Weaviate.

#### Acceptance Criteria

1. THE System SHALL provide a CLI command for batch synchronization
2. WHEN batch sync is executed, THE System SHALL retrieve all PRDs and test cases from Database
3. WHEN batch sync is executed, THE System SHALL synchronize each entity to Vector_Store
4. WHEN batch sync is executed, THE System SHALL update sync_status for each entity
5. WHEN batch sync is executed, THE System SHALL log progress and errors
6. THE System SHALL support dry-run mode for batch sync validation
7. THE System SHALL support filtering by project_id for selective sync
