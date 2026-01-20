# RAG 测试用例管理系统 - 后端开发任务列表

## 阶段 1：基础设施搭建

### 1.1 数据库设计与迁移 ✅
- [x] 1.1.1 创建项目表迁移脚本（projects）✅
- [x] 1.1.2 创建模块表迁移脚本（modules）✅
- [x] 1.1.3 创建 PRD 文档表迁移脚本（prd_documents）✅
- [x] 1.1.4 创建 PRD 版本表迁移脚本（prd_versions）✅
- [x] 1.1.5 创建测试用例表迁移脚本（test_cases）✅
- [x] 1.1.6 创建测试步骤表迁移脚本（test_steps）✅
- [x] 1.1.7 创建测试步骤截图表迁移脚本（test_step_screenshots）✅
- [x] 1.1.8 创建标签表迁移脚本（tags）✅
- [x] 1.1.9 创建 PRD 标签关联表迁移脚本（prd_tags）✅
- [x] 1.1.10 创建测试用例标签关联表迁移脚本（test_case_tags）✅
- [x] 1.1.11 创建测试用例版本表迁移脚本（test_case_versions）✅
- [x] 1.1.12 创建 App 版本表迁移脚本（app_versions）✅
- [x] 1.1.13 创建系统配置表迁移脚本（system_settings）✅
- [x] 1.1.14 创建完整数据库 SQL 文件（database_schema.sql）✅
- [x] 1.1.15 在 Navicat 中导入并验证数据库结构 ✅

### 1.2 GORM 模型定义 ✅
- [x] 1.2.1 定义 Project 模型 ✅
- [x] 1.2.2 定义 Module 模型 ✅
- [x] 1.2.3 定义 PRDDocument 模型 ✅
- [x] 1.2.4 定义 PRDVersion 模型 ✅
- [x] 1.2.5 定义 TestCase 模型 ✅
- [x] 1.2.6 定义 TestStep 模型 ✅
- [x] 1.2.7 定义 TestStepScreenshot 模型 ✅
- [x] 1.2.8 定义 Tag 模型 ✅
- [x] 1.2.9 定义模型关联关系 ✅

### 1.3 数据库连接与初始化 ✅
- [x] 1.3.1 实现 PostgreSQL 连接池 ✅
- [x] 1.3.2 实现数据库迁移执行器 ✅
- [x] 1.3.3 实现数据库健康检查 ✅
- [x] 1.3.4 添加数据库连接到配置文件 ✅

### 1.4 基础中间件 ✅
- [x] 1.4.1 实现 CORS 中间件 ✅
- [x] 1.4.2 实现请求日志中间件 ✅
- [x] 1.4.3 实现错误恢复中间件 ✅
- [x] 1.4.4 实现项目 ID 验证中间件 ✅

### 1.5 响应格式封装 ✅
- [x] 1.5.1 定义统一响应结构 ✅
- [x] 1.5.2 实现成功响应封装函数 ✅
- [x] 1.5.3 实现错误响应封装函数 ✅
- [x] 1.5.4 定义错误码常量 ✅

## 阶段 2：项目与模块管理 API

### 2.1 项目管理 API ✅
- [x] 2.1.1 实现创建项目 API（POST /api/v1/projects）✅
- [x] 2.1.2 实现获取项目列表 API（GET /api/v1/projects）✅
- [x] 2.1.3 实现获取项目详情 API（GET /api/v1/projects/:id）✅
- [x] 2.1.4 实现更新项目 API（PUT /api/v1/projects/:id）✅
- [x] 2.1.5 实现删除项目 API（DELETE /api/v1/projects/:id）✅
- [x] 2.1.6 实现项目统计 API（GET /api/v1/projects/:id/statistics）✅

### 2.2 模块管理 API ✅
- [x] 2.2.1 实现获取模块树 API（GET /api/v1/projects/:id/modules/tree）✅
- [x] 2.2.2 实现创建模块 API（POST /api/v1/projects/:id/modules）✅
- [x] 2.2.3 实现更新模块 API（PUT /api/v1/projects/:id/modules/:module_id）✅
- [x] 2.2.4 实现删除模块 API（DELETE /api/v1/projects/:id/modules/:module_id）✅
- [x] 2.2.5 实现模块排序 API（PUT /api/v1/projects/:id/modules/sort）✅

## 阶段 3：标签管理 API

### 3.1 标签 CRUD ✅
- [x] 3.1.1 实现获取所有标签 API（GET /api/v1/projects/:id/tags）✅
- [x] 3.1.2 实现创建标签 API（POST /api/v1/projects/:id/tags）✅
- [x] 3.1.3 实现更新标签 API（PUT /api/v1/projects/:id/tags/:tag_id）✅
- [x] 3.1.4 实现删除标签 API（DELETE /api/v1/projects/:id/tags/:tag_id）✅
- [x] 3.1.5 实现标签使用统计 API（GET /api/v1/projects/:id/tags/:tag_id/usage）✅

## 阶段 4：PRD 文档管理 API

### 4.1 PRD 基础 CRUD ✅
- [x] 4.1.1 实现创建 PRD API（POST /api/v1/projects/:id/prds）✅
- [x] 4.1.2 实现获取 PRD 列表 API（GET /api/v1/projects/:id/prds）✅
  - [x] 支持分页 ✅
  - [x] 支持按模块筛选 ✅
  - [x] 支持按状态筛选 ✅
  - [x] 支持按 App 版本筛选 ✅
  - [x] 支持按标签筛选 ✅
  - [x] 支持关键词搜索 ✅
- [x] 4.1.3 实现获取 PRD 详情 API（GET /api/v1/projects/:id/prds/:prd_id）✅
- [x] 4.1.4 实现更新 PRD API（PUT /api/v1/projects/:id/prds/:prd_id）✅
- [x] 4.1.5 实现删除 PRD API（DELETE /api/v1/projects/:id/prds/:prd_id）✅

### 4.2 PRD 版本管理 ✅
- [x] 4.2.1 实现创建 PRD 版本功能 ✅
- [x] 4.2.2 实现获取 PRD 版本列表 API（GET /api/v1/projects/:id/prds/:prd_id/versions）✅
- [x] 4.2.3 实现获取特定版本内容 API（GET /api/v1/projects/:id/prds/:prd_id/versions/:version）✅
- [x] 4.2.4 实现版本对比 API（GET /api/v1/projects/:id/prds/:prd_id/versions/compare）✅

### 4.3 PRD 状态管理 ✅
- [x] 4.3.1 实现更新 PRD 状态 API（PUT /api/v1/projects/:id/prds/:prd_id/status）✅
- [x] 4.3.2 实现发布 PRD API（POST /api/v1/projects/:id/prds/:prd_id/publish）✅
- [x] 4.3.3 实现归档 PRD API（POST /api/v1/projects/:id/prds/:prd_id/archive）✅

### 4.4 PRD 标签关联 ✅
- [x] 4.4.1 实现添加 PRD 标签 API（POST /api/v1/projects/:id/prds/:prd_id/tags）✅
- [x] 4.4.2 实现删除 PRD 标签 API（DELETE /api/v1/projects/:id/prds/:prd_id/tags/:tag_id）✅

## 阶段 5：测试用例管理 API

### 5.1 测试用例基础 CRUD
- [ ] 5.1.1 实现创建测试用例 API（POST /api/v1/projects/:project_id/testcases）
- [ ] 5.1.2 实现获取测试用例列表 API（GET /api/v1/projects/:project_id/testcases）
  - [ ] 支持分页
  - [ ] 支持按 PRD 筛选
  - [ ] 支持按模块筛选
  - [ ] 支持按优先级筛选
  - [ ] 支持按类型筛选
  - [ ] 支持按状态筛选
  - [ ] 支持按标签筛选
  - [ ] 支持关键词搜索
- [ ] 5.1.3 实现获取测试用例详情 API（GET /api/v1/projects/:project_id/testcases/:id）
- [ ] 5.1.4 实现更新测试用例 API（PUT /api/v1/projects/:project_id/testcases/:id）
- [ ] 5.1.5 实现删除测试用例 API（DELETE /api/v1/projects/:project_id/testcases/:id）
- [ ] 5.1.6 实现批量删除测试用例 API（POST /api/v1/projects/:project_id/testcases/batch-delete）

### 5.2 测试步骤管理
- [ ] 5.2.1 实现创建测试步骤功能（随测试用例创建）
- [ ] 5.2.2 实现更新测试步骤功能（随测试用例更新）
- [ ] 5.2.3 实现删除测试步骤功能（随测试用例删除）
- [ ] 5.2.4 实现步骤排序功能

### 5.3 测试用例标签关联
- [ ] 5.3.1 实现添加测试用例标签 API（POST /api/v1/projects/:project_id/testcases/:id/tags）
- [ ] 5.3.2 实现删除测试用例标签 API（DELETE /api/v1/projects/:project_id/testcases/:id/tags/:tag_id）

### 5.4 测试用例版本管理
- [ ] 5.4.1 实现创建测试用例版本功能
- [ ] 5.4.2 实现获取测试用例版本列表 API（GET /api/v1/projects/:project_id/testcases/:id/versions）
- [ ] 5.4.3 实现获取特定版本内容 API（GET /api/v1/projects/:project_id/testcases/:id/versions/:version）

## 阶段 6：文件上传功能

### 6.1 文件上传基础
- [ ] 6.1.1 实现文件存储目录初始化
- [ ] 6.1.2 实现文件类型验证
- [ ] 6.1.3 实现文件大小验证
- [ ] 6.1.4 实现文件名生成（UUID + 扩展名）
- [ ] 6.1.5 实现文件路径组织（按日期）

### 6.2 截图上传 API
- [ ] 6.2.1 实现上传截图 API（POST /api/v1/projects/:project_id/upload/screenshot）
- [ ] 6.2.2 实现删除截图 API（DELETE /api/v1/projects/:project_id/upload/:id）
- [ ] 6.2.3 实现截图与步骤关联功能
- [ ] 6.2.4 实现静态文件服务（GET /uploads/*）

### 6.3 文件清理
- [ ] 6.3.1 实现孤立文件识别
- [ ] 6.3.2 实现定时清理任务

## 阶段 7：统计功能 API

### 7.1 仪表盘统计
- [ ] 7.1.1 实现项目统计 API（GET /api/v1/projects/:project_id/statistics）
  - [ ] 总 PRD 数量
  - [ ] 总测试用例数量
  - [ ] 按优先级统计
  - [ ] 按类型统计
  - [ ] 按模块统计
  - [ ] 按状态统计

### 7.2 趋势分析
- [ ] 7.2.1 实现创建趋势 API（GET /api/v1/projects/:project_id/statistics/trends）
- [ ] 7.2.2 实现覆盖率统计 API（GET /api/v1/projects/:project_id/statistics/coverage）

## 阶段 8：Weaviate 集成

### 8.1 Weaviate 连接
- [ ] 8.1.1 实现 Weaviate 客户端初始化
- [ ] 8.1.2 实现 Weaviate 健康检查
- [ ] 8.1.3 添加 Weaviate 配置到配置文件

### 8.2 Collection Schema 创建
- [ ] 8.2.1 定义 PRDDocument Collection Schema
- [ ] 8.2.2 定义 TestCase Collection Schema
- [ ] 8.2.3 实现 Schema 自动创建

### 8.3 向量化服务
- [ ] 8.3.1 实现 LLM Embedding API 调用
- [ ] 8.3.2 实现文本向量化函数
- [ ] 8.3.3 实现向量化错误处理

### 8.4 数据同步
- [ ] 8.4.1 实现 PRD 创建时同步到 Weaviate
- [ ] 8.4.2 实现 PRD 更新时同步到 Weaviate
- [ ] 8.4.3 实现 PRD 删除时从 Weaviate 删除
- [ ] 8.4.4 实现测试用例创建时同步到 Weaviate
- [ ] 8.4.5 实现测试用例更新时同步到 Weaviate
- [ ] 8.4.6 实现测试用例删除时从 Weaviate 删除
- [ ] 8.4.7 实现批量同步脚本
- [ ] 8.4.8 实现同步失败重试机制

## 阶段 9：语义检索 API

### 9.1 检索功能
- [ ] 9.1.1 实现语义检索 API（POST /api/v1/projects/:project_id/search）
  - [ ] 支持自然语言查询
  - [ ] 支持类型筛选（PRD/测试用例/全部）
  - [ ] 支持结构化过滤
  - [ ] 支持相似度阈值
  - [ ] 支持结果数量限制
- [ ] 9.1.2 实现结果格式化
- [ ] 9.1.3 实现关键词高亮

### 9.2 关联推荐
- [ ] 9.2.1 实现基于 PRD 的推荐 API（GET /api/v1/projects/:project_id/prds/:id/recommendations）
- [ ] 9.2.2 实现基于测试用例的推荐 API（GET /api/v1/projects/:project_id/testcases/:id/recommendations）

## 阶段 10：影响分析功能

### 10.1 版本对比
- [ ] 10.1.1 实现 PRD 版本内容对比算法
- [ ] 10.1.2 实现变更点识别
- [ ] 10.1.3 实现变更摘要生成

### 10.2 影响评估
- [ ] 10.2.1 实现影响分析 API（POST /api/v1/projects/:project_id/impact-analysis）
- [ ] 10.2.2 实现 LLM 调用封装
- [ ] 10.2.3 实现受影响测试用例识别
- [ ] 10.2.4 实现影响程度评级
- [ ] 10.2.5 实现更新建议生成

### 10.3 测试用例建议
- [ ] 10.3.1 实现新增测试用例建议
- [ ] 10.3.2 实现更新测试用例建议
- [ ] 10.3.3 实现废弃测试用例建议

## 阶段 11：Dify 集成

### 11.1 外部知识库 API
- [ ] 11.1.1 实现 Dify 检索接口（POST /api/v1/dify/retrieval）
  - [ ] 符合 Dify 规范的请求格式
  - [ ] 符合 Dify 规范的响应格式
  - [ ] 支持 top_k 参数
  - [ ] 支持 score_threshold 参数
  - [ ] 支持元数据过滤
- [ ] 11.1.2 实现项目级别数据隔离
- [ ] 11.1.3 实现结果格式化

### 11.2 API 文档
- [ ] 11.2.1 编写 Dify 集成文档
- [ ] 11.2.2 提供配置示例
- [ ] 11.2.3 提供测试用例

## 阶段 12：测试与优化

### 12.1 功能测试
- [ ] 12.1.1 测试项目管理功能
- [ ] 12.1.2 测试模块管理功能
- [ ] 12.1.3 测试 PRD 管理功能
- [ ] 12.1.4 测试测试用例管理功能
- [ ] 12.1.5 测试文件上传功能
- [ ] 12.1.6 测试语义检索功能
- [ ] 12.1.7 测试影响分析功能
- [ ] 12.1.8 测试 Dify 集成

### 12.2 性能优化
- [ ] 12.2.1 优化数据库查询
- [ ] 12.2.2 添加必要的索引
- [ ] 12.2.3 优化 API 响应时间
- [ ] 12.2.4 实现查询结果缓存

### 12.3 错误处理
- [ ] 12.3.1 完善错误处理逻辑
- [ ] 12.3.2 统一错误码
- [ ] 12.3.3 完善错误日志

### 12.4 文档完善
- [ ] 12.4.1 完善 API 文档
- [ ] 12.4.2 完善数据库文档
- [ ] 12.4.3 编写部署文档
- [ ] 12.4.4 编写开发文档

## 阶段 13：Docker 部署

### 13.1 Docker 配置
- [ ] 13.1.1 编写后端 Dockerfile
- [ ] 13.1.2 编写 docker-compose.yml
- [ ] 13.1.3 配置 PostgreSQL 服务
- [ ] 13.1.4 配置 Weaviate 服务
- [ ] 13.1.5 配置 Nginx 反向代理

### 13.2 环境配置
- [ ] 13.2.1 编写 .env.example
- [ ] 13.2.2 配置环境变量
- [ ] 13.2.3 配置数据卷

### 13.3 部署测试
- [ ] 13.3.1 测试 Docker 环境启动
- [ ] 13.3.2 测试数据库连接
- [ ] 13.3.3 测试 API 访问
- [ ] 13.3.4 测试前后端联调

## 进度追踪

- **总任务数**: 150+
- **已完成**: 66 ✅
- **进行中**: 0
- **待开始**: 84+
- **完成度**: 44%

### 最新进度（2025-01-20）
✅ **阶段 1 完成** - 基础设施搭建
✅ **阶段 2.1 完成** - 项目管理 API
✅ **阶段 2.2 完成** - 模块管理 API
✅ **阶段 3.1 完成** - 标签管理 API
✅ **阶段 4.1 完成** - PRD 文档管理 API
- 实现了完整的 PRD CRUD API
- 实现了复杂的列表查询（分页、多条件筛选、关键词搜索）
- 支持按模块、状态、App版本、标签筛选
- 内容更新时自动版本号递增
- 所有 API 测试通过

### 下一步计划
� **阶段 3.1** - 标签管理 API
- 实现标签 CRUD 操作
- 实现标签使用统计

## 里程碑

- [x] **Milestone 1.1**: 数据库设计完成 ✅（2025-01-20）
  - 13 张表结构设计完成
  - 索引和触发器配置完成
  - 初始数据导入完成
  - PostgreSQL 数据库验证通过
- [x] **Milestone 1.2**: GORM 模型定义完成 ✅（2025-01-20）
  - 所有数据库模型定义完成
  - 模型关联关系配置完成
  - 软删除和时间戳自动管理实现
- [x] **Milestone 1.3**: 数据库连接与初始化完成 ✅（2025-01-20）
  - PostgreSQL 连接池实现
  - 数据库健康检查实现
  - 自动迁移功能实现
  - 服务器成功启动并连接数据库
- [x] **Milestone 1.4**: 基础中间件完成 ✅（2025-01-20）
  - CORS 中间件实现
  - 请求日志中间件实现
  - 错误恢复中间件实现
  - 项目 ID 验证中间件实现
- [x] **Milestone 1.5**: 响应格式封装完成 ✅（2025-01-20）
  - 统一响应结构定义
  - 成功/错误响应函数实现
  - 错误码常量定义
- [x] **Milestone 1**: 基础设施完成（阶段 1）✅（2025-01-20）
- [ ] **Milestone 2**: 核心 API 完成（阶段 2-5）
- [ ] **Milestone 3**: 文件上传完成（阶段 6）
- [ ] **Milestone 4**: RAG 功能完成（阶段 8-9）
- [ ] **Milestone 5**: 高级功能完成（阶段 10-11）
- [ ] **Milestone 6**: 测试与部署完成（阶段 12-13）
