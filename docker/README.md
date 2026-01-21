# RAG 测试用例管理系统 - Docker 部署

本项目使用 Docker Compose 进行部署，包含以下服务：
- PostgreSQL 数据库
- Weaviate 向量数据库
- 后端 API 服务（待添加）
- 前端 Web 服务（待添加）

## 端口说明

| 服务 | 容器端口 | 宿主机端口 | 说明 |
|------|---------|-----------|------|
| PostgreSQL | 5432 | 5432 | 关系型数据库 |
| Weaviate | 8080 | 8009 | 向量数据库（避免与其他项目的 8008 冲突） |
| Backend | 8080 | 8080 | Go API 服务 |
| Frontend | 5173 | 5173 | React 前端 |

## 快速开始

### 1. 启动所有服务

```bash
cd docker
docker-compose up -d
```

### 2. 查看服务状态

```bash
docker-compose ps
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f postgres
docker-compose logs -f weaviate
```

### 4. 停止服务

```bash
docker-compose down
```

### 5. 停止并删除数据卷（慎用）

```bash
docker-compose down -v
```

## 服务访问

### PostgreSQL
```bash
# 连接字符串
postgresql://rag_user:rag_password@localhost:5432/rag_db

# 使用 psql 连接
docker exec -it rag-postgres psql -U rag_user -d rag_db
```

### Weaviate
```bash
# 健康检查
curl http://localhost:8009/v1/meta

# 查看 schema
curl http://localhost:8009/v1/schema
```

## 数据持久化

数据存储在 Docker 卷中：
- `postgres_data`: PostgreSQL 数据
- `weaviate_data`: Weaviate 向量数据

查看数据卷：
```bash
docker volume ls | grep rag
```

## 数据隔离说明

本项目的 Weaviate 实例与其他项目完全隔离：

| 项目 | 容器名 | 端口 | 数据卷 |
|------|--------|------|--------|
| 现有项目 | weaviate | 8008 | ./weaviate_data |
| RAG 项目 | rag-weaviate | 8009 | weaviate_data (Docker 卷) |

**完全独立，互不干扰！**

## 环境变量

可以通过 `.env` 文件配置环境变量：

```bash
# 复制示例文件
cp .env.example .env

# 编辑配置
vim .env
```

## 故障排查

### Weaviate 无法启动

```bash
# 查看日志
docker-compose logs weaviate

# 重启服务
docker-compose restart weaviate
```

### PostgreSQL 连接失败

```bash
# 检查容器状态
docker-compose ps postgres

# 查看日志
docker-compose logs postgres
```

### 端口冲突

如果端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "新端口:8080"
```

## 开发模式

开发时可以只启动数据库服务：

```bash
# 只启动 PostgreSQL 和 Weaviate
docker-compose up -d postgres weaviate

# 本地运行后端
cd ../backend
go run cmd/server/main.go

# 本地运行前端
cd ../frontend
npm run dev
```

## 生产部署

生产环境建议：
1. 修改默认密码
2. 启用 Weaviate 认证
3. 配置 SSL/TLS
4. 使用 Nginx 反向代理
5. 配置日志收集
6. 设置资源限制

## 备份与恢复

### PostgreSQL 备份

```bash
# 备份
docker exec rag-postgres pg_dump -U rag_user rag_db > backup.sql

# 恢复
docker exec -i rag-postgres psql -U rag_user rag_db < backup.sql
```

### Weaviate 备份

```bash
# 备份数据卷
docker run --rm -v docker_weaviate_data:/data -v $(pwd):/backup alpine tar czf /backup/weaviate_backup.tar.gz -C /data .

# 恢复数据卷
docker run --rm -v docker_weaviate_data:/data -v $(pwd):/backup alpine tar xzf /backup/weaviate_backup.tar.gz -C /data
```
