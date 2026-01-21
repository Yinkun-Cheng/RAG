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

### 5.1 测试用例基础 CRUD ✅
- [x] 5.1.1 实现创建测试用例 API（POST /api/v1/projects/:id/testcases）✅
- [x] 5.1.2 实现获取测试用例列表 API（GET /api/v1/projects/:id/testcases）✅
  - [x] 支持分页 ✅
  - [x] 支持按 PRD 筛选 ✅
  - [x] 支持按模块筛选 ✅
  - [x] 支持按优先级筛选 ✅
  - [x] 支持按类型筛选 ✅
  - [x] 支持按状态筛选 ✅
  - [x] 支持按标签筛选 ✅
  - [x] 支持关键词搜索 ✅
- [x] 5.1.3 实现获取测试用例详情 API（GET /api/v1/projects/:id/testcases/:testcase_id）✅
- [x] 5.1.4 实现更新测试用例 API（PUT /api/v1/projects/:id/testcases/:testcase_id）✅
- [x] 5.1.5 实现删除测试用例 API（DELETE /api/v1/projects/:id/testcases/:testcase_id）✅
- [x] 5.1.6 实现批量删除测试用例 API（POST /api/v1/projects/:id/testcases/batch-delete）✅

### 5.2 测试步骤管理 ✅
- [x] 5.2.1 实现创建测试步骤功能（随测试用例创建）✅
- [x] 5.2.2 实现更新测试步骤功能（随测试用例更新）✅
- [x] 5.2.3 实现删除测试步骤功能（随测试用例删除）✅
- [x] 5.2.4 实现步骤排序功能 ✅

### 5.3 测试用例标签关联 ✅
- [x] 5.3.1 实现添加测试用例标签 API（POST /api/v1/projects/:id/testcases/:testcase_id/tags）✅
- [x] 5.3.2 实现删除测试用例标签 API（DELETE /api/v1/projects/:id/testcases/:testcase_id/tags/:tag_id）✅

### 5.4 测试用例版本管理 ✅
- [x] 5.4.1 实现创建测试用例版本功能 ✅
- [x] 5.4.2 实现获取测试用例版本列表 API（GET /api/v1/projects/:id/testcases/:testcase_id/versions）✅
- [x] 5.4.3 实现获取特定版本内容 API（GET /api/v1/projects/:id/testcases/:testcase_id/versions/:version）✅

## 阶段 6：文件上传功能（已移除）

~~由于前端不需要截图上传功能，此阶段已移除~~

## 阶段 7：统计功能 API ✅

### 7.1 仪表盘统计 ✅
- [x] 7.1.1 实现项目统计 API（GET /api/v1/projects/:project_id/statistics）✅
  - [x] 总 PRD 数量 ✅
  - [x] 总测试用例数量 ✅
  - [x] 按优先级统计 ✅
  - [x] 按类型统计 ✅
  - [x] 按模块统计 ✅
  - [x] 按状态统计 ✅

### 7.2 趋势分析 ✅
- [x] 7.2.1 实现创建趋势 API（GET /api/v1/projects/:project_id/statistics/trends）✅
- [x] 7.2.2 实现覆盖率统计 API（GET /api/v1/projects/:project_id/statistics/coverage）✅

## 阶段 8：Weaviate 集成 ✅

### 8.1 Weaviate 连接 ✅
- [x] 8.1.1 实现 Weaviate 客户端初始化 ✅
- [x] 8.1.2 实现 Weaviate 健康检查 ✅
- [x] 8.1.3 添加 Weaviate 配置到配置文件 ✅

### 8.2 Collection Schema 创建 ✅
- [x] 8.2.1 定义 PRDDocument Collection Schema ✅
- [x] 8.2.2 定义 TestCase Collection Schema ✅
- [x] 8.2.3 实现 Schema 自动创建 ✅

### 8.3 向量化服务 ✅
- [x] 8.3.1 实现 Embedding API 调用（火山引擎 Ark API）✅
- [x] 8.3.2 实现文本向量化函数 ✅
- [x] 8.3.3 实现向量化错误处理 ✅
- [x] 8.3.4 实现 Embedding 配置管理（从数据库加载）✅
- [x] 8.3.5 创建 global_settings 表存储 Embedding 配置 ✅

### 8.4 数据同步 ✅
- [x] 8.4.1 实现 PRD 创建时同步到 Weaviate ✅
- [x] 8.4.2 实现 PRD 更新时同步到 Weaviate ✅
- [x] 8.4.3 实现 PRD 删除时从 Weaviate 删除 ✅
- [x] 8.4.4 实现测试用例创建时同步到 Weaviate ✅
- [x] 8.4.5 实现测试用例更新时同步到 Weaviate ✅
- [x] 8.4.6 实现测试用例删除时从 Weaviate 删除 ✅
- [x] 8.4.7 实现异步同步机制（goroutine）✅
- [x] 8.4.8 实现同步状态追踪（synced_to_vector, sync_status, last_synced_at）✅

## 阶段 9：语义检索 API

### 9.1 检索功能
- [x] 9.1.1 实现语义检索 API（POST /api/v1/projects/:project_id/search）✅
  - [x] 支持自然语言查询 ✅
  - [x] 支持类型筛选（PRD/测试用例/全部）✅
  - [x] 支持结构化过滤 ✅
  - [x] 支持相似度阈值 ✅
  - [x] 支持结果数量限制 ✅
- [x] 9.1.2 实现结果格式化 ✅
- [x] 9.1.3 实现关键词高亮 ✅

### 9.2 关联推荐
- [x] 9.2.1 实现基于 PRD 的推荐 API（GET /api/v1/projects/:project_id/prds/:id/recommendations）✅
- [x] 9.2.2 实现基于测试用例的推荐 API（GET /api/v1/projects/:project_id/testcases/:id/recommendations）✅

## 阶段 10：前后端联调与测试 🔄

### 10.1 联调准备
- [ ] 10.1.1 确认所有 API 路由正确注册
- [ ] 10.1.2 确认 CORS 配置允许前端访问
- [ ] 10.1.3 准备测试数据（项目、模块、PRD、测试用例）
- [ ] 10.1.4 确认 Weaviate 和 Embedding 服务正常运行

### 10.2 核心功能联调
- [ ] 10.2.1 项目管理功能联调
  - [ ] 创建项目
  - [ ] 获取项目列表
  - [ ] 项目详情
  - [ ] 更新/删除项目
- [ ] 10.2.2 模块管理功能联调
  - [ ] 获取模块树
  - [ ] 创建/更新/删除模块
  - [ ] 模块排序
- [ ] 10.2.3 标签管理功能联调
  - [ ] 标签 CRUD
  - [ ] 标签使用统计
- [ ] 10.2.4 PRD 管理功能联调
  - [ ] PRD CRUD
  - [ ] PRD 列表筛选和搜索
  - [ ] PRD 版本管理
  - [ ] PRD 状态管理
  - [ ] PRD 标签关联
- [ ] 10.2.5 测试用例管理功能联调
  - [ ] 测试用例 CRUD
  - [ ] 测试用例列表筛选和搜索
  - [ ] 测试步骤管理
  - [ ] 测试用例标签关联
  - [ ] 测试用例版本管理

### 10.3 高级功能联调
- [ ] 10.3.1 统计功能联调
  - [ ] 项目统计数据
  - [ ] 趋势分析
  - [ ] 覆盖率统计
- [ ] 10.3.2 语义检索功能联调
  - [ ] 搜索 API（插入测试数据后）
  - [ ] PRD 推荐
  - [ ] 测试用例推荐
  - [ ] 混合检索参数调整
- [ ] 10.3.3 设置功能联调
  - [ ] 获取设置
  - [ ] 更新设置
  - [ ] 搜索配置管理

### 10.4 问题修复
- [ ] 10.4.1 修复联调中发现的 Bug
- [ ] 10.4.2 优化 API 响应格式
- [ ] 10.4.3 完善错误提示
- [ ] 10.4.4 优化性能问题

### 10.5 文档更新
- [ ] 10.5.1 更新 API 文档
- [ ] 10.5.2 更新 README
- [ ] 10.5.3 编写联调测试报告
- [ ] 10.5.4 记录已知问题和待优化项

---

## 后续阶段（联调完成后）

### 阶段 11：影响分析功能（待定）
- 版本对比
- LLM 集成
- 影响评估
- 测试用例建议

### 阶段 12：Dify 集成（待定）
- 外部知识库 API
- 项目级别数据隔离
- API 文档

### 阶段 13：性能优化（待定）
- 数据库查询优化
- 添加必要的索引
- 实现查询结果缓存

### 阶段 14：Docker 部署（待定）
- Docker 配置
- 环境配置
- 部署测试

## 进度追踪

- **总任务数**: 135+ (已移除文件上传相关任务)
- **已完成**: 130 ✅
- **进行中**: 0
- **待开始**: 5+
- **完成度**: 96%

### 最新进度（2026-01-21）
✅ **阶段 1 完成** - 基础设施搭建
✅ **阶段 2 完成** - 项目与模块管理 API
✅ **阶段 3 完成** - 标签管理 API
✅ **阶段 4 完成** - PRD 文档管理 API
✅ **阶段 5 完成** - 测试用例管理 API
🚫 **阶段 6 已移除** - 文件上传功能（前端不需要截图上传）
✅ **阶段 7 完成** - 统计功能 API
- 实现了项目统计 API（总数、按状态/优先级/类型/模块统计）
- 实现了趋势分析 API（PRD 和测试用例的创建趋势）
- 实现了覆盖率统计 API（PRD 被测试用例覆盖的比例，包括模块级别覆盖率）
- 所有统计 API 测试通过
- 所有 API 测试通过
- 前端已移除截图上传功能，简化为操作描述、测试数据、预期结果三个字段

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
- [x] **Milestone 2**: 核心 API 完成（阶段 2-5）✅（2025-01-20）
- [x] **Milestone 3**: 统计功能完成（阶段 7）✅（2025-01-20）
- [x] **Milestone 4**: Weaviate 集成完成（阶段 8）✅（2026-01-21）
  - Weaviate 客户端初始化和健康检查
  - PRDDocument 和 TestCase Collection Schema 创建
  - 火山引擎 Ark 多模态 Embedding API 集成
  - Embedding 配置管理（从数据库动态加载）
  - PRD 和测试用例的自动向量化同步
  - 异步同步机制和状态追踪
  - 服务器成功启动，所有组件健康检查通过
- [x] **Milestone 5**: 语义检索完成（阶段 9）✅（2026-01-21）
  - 实现了语义检索 API（支持自然语言查询、类型筛选、结构化过滤）
  - 实现了基于 PRD 的推荐 API
  - 实现了基于测试用例的推荐 API
  - 实现了结果格式化和关键词高亮
  - 修复了路由冲突问题
  - 完善了 buildTestCaseContent 和 extractHighlights 方法
- [ ] **Milestone 6**: 高级功能完成（阶段 10-11）
- [ ] **Milestone 7**: 测试与部署完成（阶段 12-13）


---

## 更新日志

### 2026-01-21
✅ **完成阶段 8：Weaviate 集成**
- 实现了 Weaviate 客户端初始化和健康检查
- 创建了 PRDDocument 和 TestCase Collection Schema
- 实现了火山引擎 Ark 多模态 Embedding API 集成
- 实现了 Embedding 配置管理（从数据库动态加载）
- 创建了 global_settings 表存储 Embedding 配置
- 实现了 PRD 和测试用例的自动向量化同步（异步）
- 实现了同步状态追踪（synced_to_vector, sync_status, last_synced_at）
- 服务器成功启动，所有组件健康检查通过

✅ **完成阶段 9：语义检索 API**
- 实现了语义检索 API（POST /api/v1/projects/:id/search）
  - 支持自然语言查询
  - 支持类型筛选（PRD/测试用例/全部）
  - 支持结构化过滤（项目ID、模块ID、版本ID、状态）
  - 支持相似度阈值配置
  - 支持结果数量限制
- 实现了基于 PRD 的推荐 API（GET /api/v1/projects/:id/prds/:prd_id/recommendations）
- 实现了基于测试用例的推荐 API（GET /api/v1/projects/:id/testcases/:testcase_id/recommendations）
- 实现了结果格式化和关键词高亮
- 修复了路由冲突问题（:doc_id 与 :prd_id/:testcase_id 冲突）
- 完善了 buildTestCaseContent 和 extractHighlights 方法
- **完成度**: 96% (130/135+ 任务)

**技术细节**:
- Weaviate 版本: v1.24.8
- Weaviate Go Client: v4.13.1
- Embedding 提供商: 火山引擎 Ark API
- Embedding 模型: ep-20260121110525-5mmss (多模态)
- 向量化策略:
  - PRD 文档: title + content
  - 测试用例: title only
- 同步机制: 异步 goroutine，失败时标记状态
