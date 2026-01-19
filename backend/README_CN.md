# RAG 后端服务

Go 语言实现的 RAG 测试用例管理系统后端。

## 项目结构

```
backend/
├── cmd/
│   └── server/          # 应用入口
│       └── main.go      # 主程序
├── internal/
│   ├── api/             # API 层
│   │   ├── handler/     # HTTP 处理器
│   │   ├── middleware/  # 中间件（日志、CORS、恢复）
│   │   └── router/      # 路由配置
│   ├── domain/          # 领域模型
│   │   ├── prd/         # PRD 领域
│   │   ├── testcase/    # 测试用例领域
│   │   └── common/      # 公共模型（响应格式）
│   ├── repository/      # 数据访问层
│   │   ├── postgres/    # PostgreSQL 实现
│   │   └── weaviate/    # Weaviate 实现
│   ├── service/         # 业务逻辑层
│   │   ├── prd/
│   │   ├── testcase/
│   │   ├── rag/
│   │   └── import/
│   └── pkg/             # 工具包
│       ├── config/      # 配置加载
│       ├── logger/      # 日志模块
│       └── utils/       # 工具函数
├── migrations/          # 数据库迁移脚本
├── scripts/             # 辅助脚本
├── config.yaml          # 配置文件
├── .env.example         # 环境变量示例
├── go.mod               # Go 模块定义
├── Makefile             # Make 命令
└── README.md            # 本文件
```

## 快速开始

### 1. 安装依赖

```bash
go mod download
```

或使用 Make:

```bash
make install-deps
```

### 2. 配置

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `config.yaml` 配置数据库连接等信息。

### 3. 启动服务器

```bash
go run cmd/server/main.go
```

或使用 Make:

```bash
make run
```

### 4. 测试

访问健康检查端点：

```bash
curl http://localhost:8080/health
```

或使用 PowerShell 测试脚本：

```powershell
.\test-server.ps1
```

## 可用命令

### Make 命令

- `make run` - 运行应用
- `make build` - 编译应用
- `make test` - 运行测试
- `make clean` - 清理构建产物
- `make install-deps` - 安装依赖
- `make fmt` - 格式化代码
- `make lint` - 代码检查

### Go 命令

```bash
# 运行
go run cmd/server/main.go

# 编译
go build -o bin/server cmd/server/main.go

# 测试
go test -v ./...

# 格式化
go fmt ./...
```

## API 端点

### 健康检查

```
GET /health
```

响应：
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

响应：
```json
{
  "message": "pong"
}
```

## 配置说明

### config.yaml

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
    sslmode: disable
  
  weaviate:
    host: localhost
    port: 8080
    scheme: http
    api_key: ""

storage:
  type: local                    # 存储类型: local/minio
  local_path: ./uploads          # 本地存储路径
  max_file_size: 10485760        # 最大文件大小 (10MB)

logging:
  level: info                    # 日志级别: debug/info/warn/error
  format: json                   # 日志格式: json/console
  output: stdout                 # 日志输出: stdout/文件路径
```

## 开发

### 技术栈

- **语言**: Go 1.21+
- **Web 框架**: Gin
- **ORM**: GORM
- **数据库**: PostgreSQL 15+
- **向量数据库**: Weaviate
- **配置管理**: Viper
- **日志**: Zap

### 代码规范

- 使用 `gofmt` 格式化代码
- 遵循 Go 官方代码规范
- 使用有意义的变量和函数名
- 添加必要的注释

### 项目架构

采用分层架构：

1. **API 层**: 处理 HTTP 请求和响应
2. **Service 层**: 实现业务逻辑
3. **Repository 层**: 数据访问
4. **Domain 层**: 领域模型定义

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t rag-backend .

# 运行容器
docker run -p 8080:8080 rag-backend
```

### 使用 Docker Compose

```bash
cd ../docker
docker-compose up -d
```

## 故障排除

### 端口被占用

如果 8080 端口被占用，修改 `config.yaml` 中的 `server.port`。

### 数据库连接失败

检查 `config.yaml` 中的数据库配置是否正确，确保 PostgreSQL 服务正在运行。

### 日志查看

日志默认输出到 stdout，可以在 `config.yaml` 中修改 `logging.output` 指定日志文件路径。

## 许可证

MIT License
