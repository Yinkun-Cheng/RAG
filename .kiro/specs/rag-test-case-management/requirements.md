# Requirements Document

## Introduction

本文档定义了测试用例知识库管理系统（RAG）的功能需求。该系统是一个专为 APP 测试工程师设计的知识库管理平台，用于管理 PRD 文档和测试用例，并通过 RAG（检索增强生成）技术与 Dify 集成，提供智能化的测试辅助功能。

系统支持结构化的测试用例管理、多种格式的文档导入、语义检索和智能推荐等功能，旨在提高测试工程师的工作效率和测试质量。

## Glossary

- **System**: 测试用例知识库管理系统
- **PRD**: Product Requirements Document，产品需求文档
- **Test_Case**: 测试用例，包含测试步骤、预期结果等结构化信息
- **Test_Step**: 测试步骤，包含操作、测试数据、预期结果和截图
- **Module**: 功能模块，用于组织 PRD 和测试用例的树形结构
- **Tag**: 标签，用于分类和检索
- **RAG**: Retrieval-Augmented Generation，检索增强生成
- **Vector_Database**: 向量数据库，用于存储和检索文档向量
- **Embedding**: 文本向量化表示
- **Dify**: 外部 AI 应用平台
- **Screenshot**: 测试步骤的截图附件
- **Version**: 文档或用例的版本号
- **Priority**: 测试用例优先级（P0/P1/P2/P3）
- **Test_Type**: 测试用例类型（功能/性能/兼容性/安全/易用性）

## Requirements

### Requirement 1: 功能模块管理

**User Story:** 作为测试工程师，我希望能够创建和管理功能模块的树形结构，以便按照产品功能层次组织 PRD 和测试用例。

#### Acceptance Criteria

1. THE System SHALL support creating modules with name, description, and parent module reference
2. THE System SHALL display modules in a tree structure with expand/collapse functionality
3. WHEN a user deletes a module, THE System SHALL move child modules to the parent level or prompt for confirmation
4. THE System SHALL allow updating module name, description, and parent relationship
5. THE System SHALL support drag-and-drop reordering of modules at the same level

### Requirement 2: PRD 文档基础管理

**User Story:** 作为测试工程师，我希望能够创建、编辑和管理 PRD 文档，以便记录和追踪产品需求。

#### Acceptance Criteria

1. WHEN a user creates a PRD, THE System SHALL require code, title, version, module, and content fields
2. THE System SHALL validate that PRD code is unique across all documents
3. THE System SHALL support Markdown format for PRD content with real-time preview
4. WHEN a user updates a PRD, THE System SHALL allow optional version history creation
5. THE System SHALL support PRD status transitions (draft → review → approved → published → deprecated)
6. THE System SHALL associate PRDs with one or more tags for categorization
7. WHEN a user deletes a PRD, THE System SHALL perform soft delete and preserve version history

### Requirement 3: PRD 版本管理

**User Story:** 作为测试工程师，我希望能够追踪 PRD 的版本历史，以便了解需求的演变过程和影响范围。

#### Acceptance Criteria

1. WHEN a user creates a new version of a PRD, THE System SHALL automatically save the previous version to version history
2. THE System SHALL store version number, title, content, change log, and creation timestamp for each version
3. THE System SHALL allow users to view any historical version of a PRD
4. THE System SHALL display a version comparison view showing differences between versions
5. THE System SHALL prevent deletion of version history records

### Requirement 4: PRD 文档导入

**User Story:** 作为测试工程师，我希望能够从 Word 文档导入 PRD，以便快速迁移现有文档到系统中。

#### Acceptance Criteria

1. WHEN a user uploads a Word document (.docx), THE System SHALL extract text content and convert to Markdown format
2. THE System SHALL preserve basic formatting (headings, lists, bold, italic) during conversion
3. WHEN conversion fails, THE System SHALL provide clear error messages indicating the issue
4. THE System SHALL allow users to preview converted content before saving
5. THE System SHALL support batch import of multiple Word documents

### Requirement 5: 测试用例基础管理

**User Story:** 作为测试工程师，我希望能够创建和管理结构化的测试用例，以便系统化地组织测试工作。

#### Acceptance Criteria

1. WHEN a user creates a test case, THE System SHALL require code, title, module, priority, type, and expected result fields
2. THE System SHALL validate that test case code is unique across all cases
3. THE System SHALL support priority levels (P0, P1, P2, P3) with visual indicators
4. THE System SHALL support test types (functional, performance, compatibility, security, usability)
5. THE System SHALL allow associating test cases with specific PRD and PRD version
6. THE System SHALL support test case status (active, deprecated)
7. THE System SHALL associate test cases with one or more tags
8. WHEN a user deletes a test case, THE System SHALL perform soft delete and preserve version history

### Requirement 6: 测试步骤管理

**User Story:** 作为测试工程师，我希望能够为测试用例添加详细的测试步骤，以便清晰地描述测试过程。

#### Acceptance Criteria

1. WHEN a user adds a test step, THE System SHALL require step number, action, and expected result fields
2. THE System SHALL allow optional test data field for each step
3. THE System SHALL support adding, deleting, and reordering test steps
4. THE System SHALL automatically renumber steps when order changes
5. THE System SHALL validate that step numbers are sequential starting from 1
6. THE System SHALL support rich text formatting in step descriptions

### Requirement 7: 测试步骤截图管理

**User Story:** 作为测试工程师，我希望能够为每个测试步骤上传多张截图，以便直观地展示测试过程和预期结果。

#### Acceptance Criteria

1. WHEN a user uploads a screenshot, THE System SHALL validate file type (PNG, JPG, JPEG, GIF)
2. THE System SHALL validate file size does not exceed 10MB per image
3. THE System SHALL support uploading multiple screenshots for a single test step
4. THE System SHALL store screenshot metadata (filename, file path, file size, MIME type)
5. THE System SHALL generate thumbnail previews for uploaded screenshots
6. WHEN a user deletes a screenshot, THE System SHALL remove both file and database record
7. THE System SHALL support drag-and-drop reordering of screenshots within a step
8. THE System SHALL display screenshots in a gallery view with click-to-enlarge functionality

### Requirement 8: 测试用例批量导入 - Excel

**User Story:** 作为测试工程师，我希望能够从 Excel 批量导入测试用例，以便快速迁移现有用例到系统中。

#### Acceptance Criteria

1. WHEN a user uploads an Excel file, THE System SHALL validate file format (.xlsx)
2. THE System SHALL parse Excel with predefined column headers (code, title, preconditions, steps, expected result, priority, type, tags)
3. THE System SHALL validate each row for required fields and data format
4. WHEN validation fails, THE System SHALL collect all errors and display them with row numbers
5. THE System SHALL support test steps in multi-line format within a single cell
6. THE System SHALL create test cases in a database transaction (all or nothing)
7. THE System SHALL provide a downloadable Excel template with correct format
8. THE System SHALL display import summary (total, success, failed counts)

### Requirement 9: 测试用例批量导入 - XMind

**User Story:** 作为测试工程师，我希望能够从 XMind 思维导图导入测试用例，以便利用思维导图工具设计测试用例。

#### Acceptance Criteria

1. WHEN a user uploads an XMind file, THE System SHALL validate file format (.xmind)
2. THE System SHALL extract XML content from XMind ZIP archive
3. THE System SHALL parse mind map structure and convert to test case hierarchy
4. THE System SHALL map first-level nodes to test case titles
5. THE System SHALL map second-level nodes to test steps
6. WHEN parsing fails, THE System SHALL provide clear error messages
7. THE System SHALL allow users to preview parsed structure before importing
8. THE System SHALL display import summary after completion

### Requirement 10: 标签系统

**User Story:** 作为测试工程师，我希望能够使用标签对 PRD 和测试用例进行分类，以便快速筛选和查找相关内容。

#### Acceptance Criteria

1. THE System SHALL allow creating tags with name, color, and description
2. THE System SHALL validate that tag names are unique
3. THE System SHALL support associating multiple tags with PRDs and test cases
4. THE System SHALL display tag usage count for each tag
5. WHEN a user deletes a tag, THE System SHALL remove all associations but preserve tagged items
6. THE System SHALL provide tag-based filtering in list views
7. THE System SHALL support creating new tags inline during PRD or test case creation

### Requirement 11: 搜索和筛选

**User Story:** 作为测试工程师，我希望能够通过多种条件搜索和筛选 PRD 及测试用例，以便快速找到需要的内容。

#### Acceptance Criteria

1. THE System SHALL support keyword search across PRD titles, content, and test case titles
2. THE System SHALL support filtering PRDs by module, status, and tags
3. THE System SHALL support filtering test cases by module, priority, type, status, and tags
4. THE System SHALL support combined filters (AND logic)
5. THE System SHALL display search results with pagination
6. THE System SHALL highlight matched keywords in search results
7. THE System SHALL support sorting results by creation time, update time, or relevance

### Requirement 12: 语义检索

**User Story:** 作为测试工程师，我希望能够使用自然语言查询相关的 PRD 和测试用例，以便更智能地找到相关内容。

#### Acceptance Criteria

1. WHEN a user submits a natural language query, THE System SHALL generate query embedding using AI model
2. THE System SHALL search vector database for semantically similar documents
3. THE System SHALL return results ranked by similarity score
4. THE System SHALL support filtering semantic search results by type (PRD, test case, or both)
5. THE System SHALL support combining semantic search with structured filters
6. THE System SHALL display similarity scores with search results
7. WHEN semantic search fails, THE System SHALL fall back to keyword search

### Requirement 13: 数据向量化同步

**User Story:** 作为系统管理员，我希望系统能够自动将 PRD 和测试用例同步到向量数据库，以便支持语义检索功能。

#### Acceptance Criteria

1. WHEN a PRD is created, THE System SHALL generate embedding and store in vector database
2. WHEN a PRD is updated, THE System SHALL update corresponding vector in vector database
3. WHEN a PRD is deleted, THE System SHALL remove corresponding vector from vector database
4. WHEN a test case is created, THE System SHALL generate embedding from title, preconditions, steps, and expected result
5. WHEN a test case is updated, THE System SHALL update corresponding vector
6. WHEN a test case is deleted, THE System SHALL remove corresponding vector
7. THE System SHALL handle synchronization failures with retry mechanism
8. THE System SHALL provide manual sync functionality for data consistency recovery

### Requirement 14: 关联推荐

**User Story:** 作为测试工程师，我希望在查看 PRD 时能够看到相关的测试用例推荐，以便了解该需求的测试覆盖情况。

#### Acceptance Criteria

1. WHEN a user views a PRD, THE System SHALL recommend related test cases based on semantic similarity
2. THE System SHALL display top 10 most relevant test cases with relevance scores
3. THE System SHALL consider both explicit associations (PRD ID) and semantic similarity
4. THE System SHALL allow users to adjust recommendation count
5. WHEN a user views a test case, THE System SHALL recommend related PRDs
6. THE System SHALL update recommendations when PRD or test case content changes

### Requirement 15: 影响分析

**User Story:** 作为测试工程师，我希望在 PRD 变更时能够分析影响范围，以便确定需要更新或新增的测试用例。

#### Acceptance Criteria

1. WHEN a user requests impact analysis for a PRD version change, THE System SHALL identify affected test cases
2. THE System SHALL compare old and new PRD versions to extract changes
3. THE System SHALL use semantic similarity to find potentially affected test cases
4. THE System SHALL categorize impact levels (high, medium, low) based on similarity scores
5. THE System SHALL suggest new test cases based on added requirements
6. THE System SHALL identify test cases that may need deprecation based on removed requirements
7. THE System SHALL display impact analysis results in a structured report

### Requirement 16: Dify 外部知识库集成

**User Story:** 作为系统集成者，我希望系统能够作为 Dify 的外部知识库，以便在 Dify AI 应用中检索测试知识。

#### Acceptance Criteria

1. THE System SHALL provide a retrieval API endpoint conforming to Dify external knowledge base specification
2. WHEN Dify sends a retrieval request, THE System SHALL accept query, top_k, and score_threshold parameters
3. THE System SHALL perform semantic search and return results in Dify-compatible format
4. THE System SHALL include content, score, and metadata in each result record
5. THE System SHALL support filtering by document type in retrieval requests
6. THE System SHALL handle authentication if required by Dify
7. THE System SHALL log all Dify API requests for monitoring

### Requirement 17: 统计和仪表盘

**User Story:** 作为测试工程师，我希望能够查看测试用例和 PRD 的统计信息，以便了解整体测试覆盖情况。

#### Acceptance Criteria

1. THE System SHALL display total count of PRDs and test cases
2. THE System SHALL display test case distribution by priority (P0/P1/P2/P3)
3. THE System SHALL display test case distribution by type
4. THE System SHALL display test case distribution by module
5. THE System SHALL display recently updated PRDs and test cases
6. THE System SHALL display test case coverage rate per PRD
7. THE System SHALL support exporting statistics as CSV or Excel

### Requirement 18: 文件存储

**User Story:** 作为系统管理员，我希望系统能够安全地存储上传的截图文件，以便长期保存测试资料。

#### Acceptance Criteria

1. THE System SHALL store uploaded files in local file system with organized directory structure
2. THE System SHALL generate unique file names to prevent conflicts
3. THE System SHALL organize files by date (year/month/day) in directory structure
4. THE System SHALL validate file integrity after upload
5. THE System SHALL provide file access URLs for frontend display
6. THE System SHALL implement file cleanup for orphaned files (no database reference)
7. THE System SHALL support configurable storage location via configuration file

### Requirement 19: 数据导出

**User Story:** 作为测试工程师，我希望能够导出测试用例和 PRD，以便在其他工具中使用或备份。

#### Acceptance Criteria

1. THE System SHALL support exporting test cases to Excel format
2. THE System SHALL support exporting PRDs to Markdown files
3. THE System SHALL support batch export with selected items
4. THE System SHALL include all test case fields in export (including steps and screenshots)
5. THE System SHALL preserve formatting in exported Markdown files
6. WHEN exporting with screenshots, THE System SHALL include screenshot URLs or embed images
7. THE System SHALL generate export files with timestamp in filename

### Requirement 20: 测试用例版本历史

**User Story:** 作为测试工程师，我希望能够追踪测试用例的修改历史，以便了解用例的演变过程。

#### Acceptance Criteria

1. WHEN a user updates a test case with version creation flag, THE System SHALL save current state to version history
2. THE System SHALL store complete test case snapshot including steps in JSON format
3. THE System SHALL record version number, change log, and creator information
4. THE System SHALL allow users to view any historical version of a test case
5. THE System SHALL display version comparison showing differences
6. THE System SHALL prevent deletion of version history records
7. THE System SHALL automatically increment version numbers

### Requirement 21: 批量操作

**User Story:** 作为测试工程师，我希望能够批量操作测试用例，以便提高工作效率。

#### Acceptance Criteria

1. THE System SHALL support batch deletion of selected test cases
2. THE System SHALL support batch status update (active/deprecated)
3. THE System SHALL support batch tag assignment
4. THE System SHALL support batch module reassignment
5. THE System SHALL require confirmation before executing batch operations
6. THE System SHALL display operation results with success and failure counts
7. THE System SHALL perform batch operations in database transactions

### Requirement 22: 系统配置

**User Story:** 作为系统管理员，我希望能够通过配置文件管理系统设置，以便灵活部署和调整系统行为。

#### Acceptance Criteria

1. THE System SHALL load configuration from YAML file on startup
2. THE System SHALL support configuring database connection parameters
3. THE System SHALL support configuring vector database connection parameters
4. THE System SHALL support configuring file storage location and size limits
5. THE System SHALL support configuring server port and mode (debug/release)
6. THE System SHALL validate configuration values on startup
7. WHEN configuration is invalid, THE System SHALL fail to start with clear error messages

### Requirement 23: 错误处理和日志

**User Story:** 作为系统管理员，我希望系统能够记录详细的操作日志和错误信息，以便排查问题和监控系统运行。

#### Acceptance Criteria

1. THE System SHALL log all API requests with timestamp, endpoint, and parameters
2. THE System SHALL log all database operations with execution time
3. THE System SHALL log all errors with stack traces
4. THE System SHALL categorize logs by level (debug, info, warn, error)
5. THE System SHALL rotate log files daily to prevent excessive file size
6. THE System SHALL provide structured logging in JSON format for easy parsing
7. WHEN critical errors occur, THE System SHALL return user-friendly error messages without exposing internal details

### Requirement 24: API 文档

**User Story:** 作为前端开发者，我希望能够查看完整的 API 文档，以便正确调用后端接口。

#### Acceptance Criteria

1. THE System SHALL generate API documentation using Swagger/OpenAPI specification
2. THE System SHALL provide interactive API documentation at /swagger endpoint
3. THE System SHALL document all request parameters, response formats, and error codes
4. THE System SHALL provide example requests and responses for each endpoint
5. THE System SHALL keep API documentation synchronized with code implementation
6. THE System SHALL document authentication requirements if applicable
7. THE System SHALL group API endpoints by functional modules

### Requirement 25: 数据库迁移

**User Story:** 作为系统管理员，我希望系统能够自动管理数据库 schema 变更，以便安全地升级系统版本。

#### Acceptance Criteria

1. THE System SHALL use migration scripts to manage database schema changes
2. THE System SHALL execute pending migrations automatically on startup
3. THE System SHALL track applied migrations in a migrations table
4. THE System SHALL prevent running the same migration twice
5. THE System SHALL support rollback of migrations if needed
6. THE System SHALL validate migration scripts before execution
7. WHEN migration fails, THE System SHALL halt startup and log detailed error information
