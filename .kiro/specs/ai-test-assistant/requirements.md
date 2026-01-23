# Requirements Document

## Introduction

AI 测试助手（ai-test-assistant）是一个基于 LangChain 和 Claude 4.5 Sonnet 的智能测试用例生成系统。该系统在现有的 Go + React 测试用例知识库管理系统基础上，新增 AI 对话能力，帮助测试工程师通过自然语言交互自动生成高质量测试用例。系统采用 Agent 架构，能够基于历史 PRD 和测试用例进行智能推理，大幅提升测试用例编写效率。

## Glossary

- **AI_Assistant**: AI 测试助手系统，包含前端对话界面、Python AI 服务和 Go 后端集成
- **Python_AI_Service**: 基于 FastAPI + LangChain 的独立 Python 服务，负责 AI 推理和测试用例生成
- **Go_Backend**: 现有的 Go 后端服务，作为前端和 Python 服务的中间层
- **React_Frontend**: 现有的 React 前端应用，新增 AI 对话页面
- **TestEngineerAgent**: 主 Agent，负责协调测试用例生成流程
- **BRConnector**: Claude API 代理服务，提供 Claude 4.5 Sonnet 模型访问
- **Weaviate**: 向量数据库，存储 PRD 和测试用例的向量表示
- **RAG_System**: 检索增强生成系统，基于历史知识进行推理
- **Test_Case**: 测试用例，包含标题、前置条件、测试步骤、预期结果等字段
- **Streaming_Output**: 流式输出，实时显示 AI 生成内容的打字机效果
- **Conversation_History**: 对话历史，记录用户和 AI 的多轮交互

## Requirements

### Requirement 1: AI 对话界面

**User Story:** 作为测试工程师，我希望有一个 AI 对话界面，这样我可以通过自然语言与 AI 交流，让 AI 帮我生成测试用例。

#### Acceptance Criteria

1. WHEN a user navigates to the AI assistant page, THEN THE React_Frontend SHALL display a chat interface with message history and input field
2. WHEN a user types a message and submits, THEN THE React_Frontend SHALL send the message to the Go_Backend and display it in the chat history
3. WHEN the AI responds, THEN THE React_Frontend SHALL display the response with streaming output effect
4. WHEN multiple messages are exchanged, THEN THE React_Frontend SHALL maintain conversation context and display all messages in chronological order
5. WHEN a user refreshes the page, THEN THE React_Frontend SHALL preserve the conversation history from the current session

### Requirement 2: Python AI 服务架构

**User Story:** 作为系统架构师，我希望有一个独立的 Python AI 服务，这样可以利用 LangChain 框架实现灵活的 Agent 架构。

#### Acceptance Criteria

1. THE Python_AI_Service SHALL be implemented using FastAPI framework
2. THE Python_AI_Service SHALL use LangChain framework for Agent implementation
3. THE Python_AI_Service SHALL expose HTTP API endpoints for the Go_Backend to invoke
4. WHEN the Python_AI_Service starts, THEN it SHALL initialize within 5 seconds
5. WHEN the Python_AI_Service receives a request, THEN it SHALL support at least 10 concurrent requests
6. THE Python_AI_Service SHALL implement TestEngineerAgent with extensible Workflow architecture

### Requirement 3: Go 后端集成

**User Story:** 作为后端开发者，我希望 Go 后端能够集成 AI 服务，这样可以统一管理 API 接口和数据访问。

#### Acceptance Criteria

1. WHEN a frontend request arrives, THEN THE Go_Backend SHALL validate the request and forward it to the Python_AI_Service
2. WHEN the Python_AI_Service returns a response, THEN THE Go_Backend SHALL process it and return to the frontend
3. THE Go_Backend SHALL provide RESTful API endpoints for AI chat functionality
4. THE Go_Backend SHALL handle authentication and authorization for AI endpoints
5. WHEN an error occurs in the Python_AI_Service, THEN THE Go_Backend SHALL return a user-friendly error message

### Requirement 4: 测试用例自动生成

**User Story:** 作为测试工程师，我希望输入需求描述后，AI 能自动生成测试用例，这样我可以节省大量编写测试用例的时间。

#### Acceptance Criteria

1. WHEN a user provides a requirement description, THEN THE TestEngineerAgent SHALL analyze the requirement and generate test cases
2. WHEN generating test cases, THEN THE TestEngineerAgent SHALL include title, preconditions, test steps, and expected results
3. WHEN generating test cases, THEN THE TestEngineerAgent SHALL cover main flow, exception flow, and boundary value scenarios
4. WHEN the generation is complete, THEN THE AI_Assistant SHALL return structured test case data in JSON format
5. WHEN the AI response time exceeds 10 seconds (excluding LLM call time), THEN THE Python_AI_Service SHALL log a performance warning

### Requirement 5: 基于历史知识推理

**User Story:** 作为测试工程师，我希望 AI 能基于历史 PRD 和测试用例进行推理，这样生成的测试用例更符合项目规范和历史经验。

#### Acceptance Criteria

1. WHEN generating test cases, THEN THE TestEngineerAgent SHALL query Weaviate for relevant historical PRDs and test cases
2. WHEN querying Weaviate, THEN THE Python_AI_Service SHALL use the requirement description to generate embeddings via the Volcano Engine Embedding API
3. WHEN relevant historical data is found, THEN THE TestEngineerAgent SHALL use it as context for test case generation
4. WHEN no relevant historical data is found, THEN THE TestEngineerAgent SHALL generate test cases based on general testing best practices
5. THE RAG_System SHALL retrieve at least top 5 most relevant historical documents for context

### Requirement 6: BRConnector API 集成

**User Story:** 作为系统集成者，我希望系统能够调用 BRConnector API 访问 Claude 4.5 Sonnet 模型，这样可以利用先进的 LLM 能力。

#### Acceptance Criteria

1. THE Python_AI_Service SHALL use BRConnector API endpoint at https://d106f995v5mndm.cloudfront.net
2. THE Python_AI_Service SHALL use claude-4-5-sonnet as the model name
3. WHEN calling BRConnector API, THEN THE Python_AI_Service SHALL include the API key in the request headers
4. WHEN the BRConnector API returns an error, THEN THE Python_AI_Service SHALL retry up to 3 times with exponential backoff
5. THE Python_AI_Service SHALL NOT expose the API key in logs or error messages

### Requirement 7: 流式输出支持

**User Story:** 作为用户，我希望能实时看到 AI 的生成过程，这样可以更好地理解 AI 的思考过程并提前预览结果。

#### Acceptance Criteria

1. WHEN the AI generates a response, THEN THE Python_AI_Service SHALL support streaming output via Server-Sent Events (SSE)
2. WHEN streaming output is enabled, THEN THE Go_Backend SHALL forward the stream to the React_Frontend
3. WHEN the React_Frontend receives streaming data, THEN it SHALL display the content with a typewriter effect
4. WHEN the stream is complete, THEN THE React_Frontend SHALL mark the message as complete
5. WHEN the stream is interrupted, THEN THE React_Frontend SHALL display an error message and allow retry

### Requirement 8: 测试用例编辑和保存

**User Story:** 作为测试工程师，我希望能编辑 AI 生成的测试用例，并保存到系统中，这样我可以对生成结果进行调整和完善。

#### Acceptance Criteria

1. WHEN AI generates test cases, THEN THE React_Frontend SHALL display them in an editable form
2. WHEN a user modifies a test case field, THEN THE React_Frontend SHALL update the local state
3. WHEN a user clicks save, THEN THE React_Frontend SHALL send the test case data to the Go_Backend
4. WHEN the Go_Backend receives test case data, THEN it SHALL validate and save it to PostgreSQL
5. WHEN the save is successful, THEN THE React_Frontend SHALL display a success message and navigate to the test case detail page

### Requirement 9: 错误处理和日志记录

**User Story:** 作为系统运维人员，我希望系统有完善的错误处理和日志记录，这样可以快速定位和解决问题。

#### Acceptance Criteria

1. WHEN an error occurs in any component, THEN THE system SHALL log the error with timestamp, component name, and error details
2. WHEN the Python_AI_Service encounters an error, THEN it SHALL return a structured error response with error code and message
3. WHEN the Go_Backend receives an error from Python_AI_Service, THEN it SHALL log the error and return a user-friendly message to the frontend
4. WHEN the React_Frontend receives an error response, THEN it SHALL display an error notification with actionable guidance
5. THE Python_AI_Service SHALL log all LLM API calls including request parameters and response metadata

### Requirement 10: 配置管理和安全性

**User Story:** 作为系统管理员，我希望敏感配置信息能够安全管理，这样可以防止 API 密钥泄露和未授权访问。

#### Acceptance Criteria

1. THE Python_AI_Service SHALL read BRConnector API key from environment variables or configuration files
2. THE Python_AI_Service SHALL read Volcano Engine Embedding API key from environment variables or configuration files
3. THE Go_Backend SHALL NOT expose API keys in any API responses or logs
4. THE React_Frontend SHALL NOT contain any hardcoded API keys or sensitive credentials
5. WHEN configuration is missing or invalid, THEN THE system SHALL fail to start with a clear error message

### Requirement 11: Agent 架构可扩展性

**User Story:** 作为开发者，我希望 Agent 架构支持后续添加新的 Workflow，这样可以不断扩展系统功能。

#### Acceptance Criteria

1. THE TestEngineerAgent SHALL use a modular Workflow architecture where Workflows can be added or removed independently
2. WHEN a new Workflow is added, THEN THE TestEngineerAgent SHALL automatically discover and register it
3. THE Python_AI_Service SHALL define a clear Workflow interface that all Workflows must implement
4. THE Python_AI_Service SHALL provide Tool abstractions for common operations like database queries and API calls
5. WHEN a Workflow is invoked, THEN THE TestEngineerAgent SHALL handle errors gracefully and continue with other Workflows

### Requirement 12: 性能和并发处理

**User Story:** 作为系统用户，我希望系统能够快速响应并支持多用户并发使用，这样可以提高工作效率。

#### Acceptance Criteria

1. WHEN the Python_AI_Service processes a request (excluding LLM call time), THEN it SHALL respond within 10 seconds
2. WHEN multiple users send requests simultaneously, THEN THE Python_AI_Service SHALL handle at least 10 concurrent requests
3. WHEN the Go_Backend forwards requests to Python_AI_Service, THEN it SHALL use connection pooling to optimize performance
4. WHEN the system is under load, THEN it SHALL maintain response times within acceptable limits without crashing
5. THE Python_AI_Service SHALL implement request queuing when concurrent requests exceed capacity
