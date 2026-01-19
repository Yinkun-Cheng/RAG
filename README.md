# 测试用例知识库管理系统（RAG）

## 项目概述

这是一个专为 APP 测试工程师设计的结构化知识库管理系统，用于管理 PRD 文档和测试用例，并通过 RAG（检索增强生成）技术与 Dify 集成，提供智能化的测试辅助功能。

## 核心特性

### 1. PRD 文档管理
- ✅ 版本管理（v1.0, v1.1, v2.0...）
- ✅ 功能模块分类
- ✅ 富文本/Markdown 编辑
- ✅ 文档导入（Word/Markdown）
- ✅ 变更历史追踪

### 2. 测试用例管理
- ✅ 结构化用例录入（标题、前置条件、步骤、预期结果）
- ✅ 测试步骤支持截图附件
- ✅ 优先级管理（P0/P1/P2/P3）
- ✅ 用例类型分类（功能/性能/兼容性/安全）
- ✅ 标签系统
- ✅ 批量导入（Excel/XMind）
- ✅ 用例版本历史

### 3. RAG 检索增强
- ✅ 语义检索（自然语言查询）
- ✅ 结构化过滤（按优先级、类型、标签等）
- ✅ 关联推荐（PRD 关联用例）
- ✅ 影响分析（需求变更影响范围）

### 4. Dify 集成
- ✅ 外部知识库 API 接口
- ✅ 符合 Dify 规范的检索接口
- ✅ 实时数据同步

## 技术架构

### 后端技术栈
- **语言**: Go 1.21+
- **Web 框架**: Gin
- **ORM**: GORM
- **关系数据库**: PostgreSQL 15+
- **向量数据库**: Weaviate（复用 Dify 的实例）
- **文件存储**: MinIO / 本地存储
- **API 文档**: Swagger

### 前端技术栈
- **框架**: React 18 + TypeScript
- **UI 组件**: Ant Design 5.x
- **状态管理**: React Query + Zustand
- **路由**: React Router v6
- **编辑器**: Monaco Editor（Markdown）
- **图片上传**: react-dropzone
- **构建工具**: Vite

### 部署架构
```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (反向代理)                      │
├─────────────────────────────────────────────────────────┤
│  /          → React 前端                                 │
│  /api       → Go 后端 API                                │
│  /dify      → Dify 服务                                  │
└─────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌─────────┐        ┌──────────┐        ┌──────────┐
   │ React   │        │ Go API   │        │  Dify    │
   │ Frontend│        │ Backend  │        │ Service  │
   └─────────┘        └──────────┘        └──────────┘
                            │                    │
                            ▼                    ▼
                      ┌──────────┐        ┌──────────┐
                      │PostgreSQL│        │ Weaviate │
                      └──────────┘        └──────────┘
```

## 项目结构

```
RAG/
├── docs/                          # 文档目录
│   ├── api-design.md             # API 接口设计
│   ├── database-schema.md        # 数据库设计
│   ├── frontend-design.md        # 前端页面设计
│   └── deployment.md             # 部署文档
├── backend/                       # Go 后端
│   ├── cmd/                      # 应用入口
│   │   └── server/
│   │       └── main.go
│   ├── internal/                 # 内部包
│   │   ├── api/                  # API 处理器
│   │   │   ├── handler/          # HTTP 处理器
│   │   │   ├── middleware/       # 中间件
│   │   │   └── router/           # 路由
│   │   ├── domain/               # 领域模型
│   │   │   ├── prd/              # PRD 领域
│   │   │   ├── testcase/         # 测试用例领域
│   │   │   └── common/           # 公共模型
│   │   ├── repository/           # 数据访问层
│   │   │   ├── postgres/         # PostgreSQL 实现
│   │   │   └── weaviate/         # Weaviate 实现
│   │   ├── service/              # 业务逻辑层
│   │   │   ├── prd/
│   │   │   ├── testcase/
│   │   │   ├── rag/              # RAG 检索服务
│   │   │   └── import/           # 导入服务
│   │   └── pkg/                  # 工具包
│   │       ├── config/           # 配置
│   │       ├── logger/           # 日志
│   │       ├── validator/        # 验证器
│   │       └── utils/            # 工具函数
│   ├── migrations/               # 数据库迁移
│   ├── scripts/                  # 脚本
│   ├── go.mod
│   ├── go.sum
│   └── Dockerfile
├── frontend/                      # React 前端
│   ├── public/
│   ├── src/
│   │   ├── api/                  # API 调用
│   │   ├── components/           # 通用组件
│   │   │   ├── Layout/
│   │   │   ├── MarkdownEditor/
│   │   │   ├── ImageUpload/
│   │   │   └── ...
│   │   ├── pages/                # 页面
│   │   │   ├── PRD/              # PRD 管理
│   │   │   │   ├── List.tsx
│   │   │   │   ├── Detail.tsx
│   │   │   │   ├── Create.tsx
│   │   │   │   └── Edit.tsx
│   │   │   ├── TestCase/         # 测试用例管理
│   │   │   │   ├── List.tsx
│   │   │   │   ├── Detail.tsx
│   │   │   │   ├── Create.tsx
│   │   │   │   └── Edit.tsx
│   │   │   ├── Import/           # 导入页面
│   │   │   └── Dashboard/        # 仪表盘
│   │   ├── hooks/                # 自定义 Hooks
│   │   ├── store/                # 状态管理
│   │   ├── types/                # TypeScript 类型
│   │   ├── utils/                # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker/                        # Docker 配置
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.example
└── README.md                      # 本文件
```

## 数据模型概览

### 核心实体

#### 1. PRD 文档（prd_documents）
```go
type PRDDocument struct {
    ID          string    `json:"id"`
    Title       string    `json:"title"`
    Version     string    `json:"version"`
    ModuleID    string    `json:"module_id"`
    Content     string    `json:"content"`      // Markdown 内容
    Status      string    `json:"status"`       // draft/review/approved/published
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
}
```

#### 2. 测试用例（test_cases）
```go
type TestCase struct {
    ID              string         `json:"id"`
    Code            string         `json:"code"`           // TC_LOGIN_001
    Title           string         `json:"title"`
    PRDID           string         `json:"prd_id"`
    PRDVersion      string         `json:"prd_version"`
    ModuleID        string         `json:"module_id"`
    Preconditions   string         `json:"preconditions"`
    Steps           []TestStep     `json:"steps"`
    ExpectedResult  string         `json:"expected_result"`
    Priority        string         `json:"priority"`       // P0/P1/P2/P3
    Type            string         `json:"type"`           // functional/performance/compatibility
    Tags            []string       `json:"tags"`
    Status          string         `json:"status"`         // active/deprecated
    CreatedAt       time.Time      `json:"created_at"`
    UpdatedAt       time.Time      `json:"updated_at"`
}

type TestStep struct {
    StepNumber  int      `json:"step_number"`
    Action      string   `json:"action"`
    Data        string   `json:"data"`
    Expected    string   `json:"expected"`
    Screenshots []string `json:"screenshots"`  // 图片 URL
}
```

## 开发计划

### Phase 1: 基础架构搭建（第 1-2 天）
- [x] 项目结构初始化 ✅
- [x] 后端项目初始化 ✅ (完成时间: 2025-01-19)
  - [x] Go 项目目录结构
  - [x] go.mod 和核心依赖
  - [x] 配置文件结构
  - [x] 配置加载模块 (Viper)
  - [x] 日志模块 (Zap)
  - [x] 基础 HTTP 服务器 (Gin)
  - [x] 中间件 (CORS, Logger, Recovery)
- [ ] 前端项目初始化
- [ ] 数据库设计与迁移
- [ ] Go 后端基础框架
- [ ] React 前端基础框架
- [ ] Docker 环境配置

### Phase 2: PRD 文档管理（第 3-4 天）
- [ ] PRD CRUD API
- [ ] PRD 前端页面
- [ ] Markdown 编辑器集成
- [ ] 版本管理功能

### Phase 3: 测试用例管理（第 5-7 天）
- [ ] 测试用例 CRUD API
- [ ] 测试用例前端页面
- [ ] 步骤管理（含截图上传）
- [ ] 标签系统

### Phase 4: 导入功能（第 8-9 天）
- [ ] Excel 导入解析
- [ ] XMind 导入解析
- [ ] Word 文档导入
- [ ] 批量导入前端

### Phase 5: RAG 检索（第 10-12 天）
- [ ] Weaviate 向量化集成
- [ ] 语义检索 API
- [ ] 结构化过滤
- [ ] 关联推荐算法

### Phase 6: Dify 集成（第 13-14 天）
- [ ] 外部知识库 API 实现
- [ ] Dify 配置与测试
- [ ] 影响分析功能

### Phase 7: 优化与部署（第 15 天）
- [ ] 性能优化
- [ ] 文档完善
- [ ] Docker 部署
- [ ] 测试与验收

## 快速开始

### 前置要求
- Go 1.21+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Weaviate（可复用 Dify 的实例）

### 开发环境启动

1. **启动数据库**
```bash
cd RAG/docker
docker-compose up -d postgres
```

2. **启动后端**
```bash
cd RAG/backend
go mod download
go run cmd/server/main.go
```

3. **启动前端**
```bash
cd RAG/frontend
npm install
npm run dev
```

4. **访问应用**
- 前端: http://localhost:5173
- 后端 API: http://localhost:8080
- API 文档: http://localhost:8080/swagger

## 配置说明

### 后端配置（backend/config.yaml）
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
    host: localhost
    port: 8080
    scheme: http

storage:
  type: local  # local / minio
  local_path: ./uploads
```

### 前端配置（frontend/.env）
```env
VITE_API_BASE_URL=http://localhost:8080/api
VITE_UPLOAD_MAX_SIZE=10485760  # 10MB
```

## API 接口概览

### PRD 文档
- `GET    /api/v1/prds` - 获取 PRD 列表
- `GET    /api/v1/prds/:id` - 获取 PRD 详情
- `POST   /api/v1/prds` - 创建 PRD
- `PUT    /api/v1/prds/:id` - 更新 PRD
- `DELETE /api/v1/prds/:id` - 删除 PRD

### 测试用例
- `GET    /api/v1/testcases` - 获取用例列表
- `GET    /api/v1/testcases/:id` - 获取用例详情
- `POST   /api/v1/testcases` - 创建用例
- `PUT    /api/v1/testcases/:id` - 更新用例
- `DELETE /api/v1/testcases/:id` - 删除用例

### RAG 检索
- `POST   /api/v1/search` - 语义检索
- `GET    /api/v1/recommend/:prd_id` - 关联推荐
- `POST   /api/v1/impact-analysis` - 影响分析

### Dify 外部知识库接口
- `POST   /api/v1/dify/retrieval` - Dify 检索接口

### 导入
- `POST   /api/v1/import/excel` - Excel 导入
- `POST   /api/v1/import/xmind` - XMind 导入
- `POST   /api/v1/import/word` - Word 导入

## 贡献指南

本项目为个人使用项目，暂不接受外部贡献。

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue。
