# 快速启动指南

## 📋 前置要求

- Go 1.21+
- Node.js 18+
- PostgreSQL 15+ (可选，用于后续开发)
- Docker & Docker Compose (可选)

## 🚀 快速开始

### 1. 后端启动

#### 方式一：使用启动脚本（推荐）

```powershell
cd backend
.\start.ps1
```

#### 方式二：手动启动

```bash
cd backend
go mod download
go run cmd/server/main.go
```

#### 方式三：使用 Make

```bash
cd backend
make run
```

### 2. 验证后端

打开浏览器访问：
- 健康检查: http://localhost:8080/health
- API 测试: http://localhost:8080/api/v1/ping

或使用测试脚本：

```powershell
cd backend
.\test-server.ps1
```

### 3. 前端启动（待实现）

```bash
cd frontend
npm install
npm run dev
```

访问: http://localhost:5173

## 📁 项目结构

```
RAG/
├── backend/              # Go 后端 ✅ 已完成
│   ├── cmd/             # 应用入口
│   ├── internal/        # 内部包
│   │   ├── api/         # API 层
│   │   ├── domain/      # 领域模型
│   │   ├── repository/  # 数据访问层
│   │   ├── service/     # 业务逻辑层
│   │   └── pkg/         # 工具包
│   ├── migrations/      # 数据库迁移
│   ├── config.yaml      # 配置文件
│   └── go.mod           # Go 模块
├── frontend/            # React 前端 🚧 进行中
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── docker/              # Docker 配置
│   ├── docker-compose.yml
│   └── .env.example
└── docs/                # 文档
    ├── api-design.md
    ├── database-schema.md
    └── frontend-design.md
```

## ✅ 已完成功能

### 后端 (Phase 1.1)

- ✅ 项目结构搭建
- ✅ 配置管理 (Viper)
- ✅ 日志系统 (Zap)
- ✅ HTTP 服务器 (Gin)
- ✅ 中间件 (CORS, Logger, Recovery)
- ✅ 健康检查端点
- ✅ API v1 基础结构

### 前端

- ✅ 项目结构搭建
- ✅ 基础配置文件
- 🚧 组件开发中...

## 🔧 配置说明

### 后端配置 (backend/config.yaml)

```yaml
server:
  port: 8080          # 服务器端口
  mode: debug         # 运行模式: debug/release

database:
  postgres:
    host: localhost
    port: 5432
    user: rag_user
    password: rag_password
    dbname: rag_db

logging:
  level: info         # 日志级别
  format: json        # 日志格式
  output: stdout      # 日志输出
```

### 前端配置 (frontend/.env)

```env
VITE_API_BASE_URL=http://localhost:8080/api/v1
VITE_UPLOAD_MAX_SIZE=10485760
```

## 🐛 故障排除

### 后端端口被占用

修改 `backend/config.yaml` 中的 `server.port`。

### 依赖安装失败

```bash
# 清理缓存
go clean -modcache

# 重新下载
go mod download
```

### 前端启动失败

```bash
# 删除 node_modules 重新安装
rm -rf node_modules
npm install
```

## 📚 更多文档

- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)
- [API 设计](docs/api-design.md)
- [数据库设计](docs/database-schema.md)
- [开发计划](docs/development-plan.md)
- [Phase 1.1 完成报告](PHASE1_COMPLETE.md)

## 🎯 下一步

1. ✅ 完成后端项目初始化
2. 🚧 完成前端项目初始化 (Phase 1.2)
3. ⏳ 数据库设计与迁移 (Phase 2.1)
4. ⏳ Docker 环境配置 (Phase 2.2)
5. ⏳ 模块与标签管理 (Phase 3)

## 💬 获取帮助

如有问题，请查看：
- [开发计划](docs/development-plan.md)
- [API 文档](docs/api-design.md)
- [数据库文档](docs/database-schema.md)

## 🎉 开始开发

现在你可以开始开发了！

```bash
# 启动后端
cd backend
.\start.ps1

# 启动前端（待实现）
cd frontend
npm run dev
```

祝开发顺利！🚀
