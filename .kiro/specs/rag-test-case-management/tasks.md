Tasks
Phase 1: 环境搭建与基础架构
1. Day 1: 项目初始化
1.1 后端项目初始化
[x] 1.1.1 创建 Go 项目目录结构
[x] 1.1.2 初始化 go.mod 并安装核心依赖
[x] 1.1.3 创建配置文件结构 (config.yaml, .env.example)
[x] 1.1.4 实现配置加载模块 (Viper)
[x] 1.1.5 实现日志模块 (Zap)
[x] 1.1.6 创建 main.go 并实现基础 HTTP 服务器
1.2 前端项目初始化
[x] 1.2.1 使用 Vite 创建 React + TypeScript 项目
[x] 1.2.2 安装核心依赖 (Ant Design, React Router, React Query, Axios, Tailwind)
[x] 1.2.3 配置 ESLint 和 Prettier
[x] 1.2.4 配置 Tailwind CSS
[x] 1.2.5 创建基础路由结构
[x] 1.2.6 创建 Layout 组件框架
2. Day 2: 数据库与 Docker 环境
2.1 数据库设计与迁移
[ ] 2.1.1 编写数据库迁移脚本 (001_create_modules.sql)
[ ] 2.1.2 编写数据库迁移脚本 (002_create_prds.sql)
[ ] 2.1.3 编写数据库迁移脚本 (003_create_test_cases.sql)
[ ] 2.1.4 编写数据库迁移脚本 (004_create_tags.sql)
[ ] 2.1.5 编写数据库迁移脚本 (005_create_relations.sql)
[ ] 2.1.6 创建 GORM 模型 (Module, PRDDocument, TestCase, Tag)
[ ] 2.1.7 实现数据库连接和迁移执行逻辑
[ ] 2.1.8 编写数据库初始化脚本 (默认模块和标签)
2.2 Docker 环境配置
[ ] 2.2.1 编写后端 Dockerfile (多阶段构建)
[ ] 2.2.2 编写前端 Dockerfile
[ ] 2.2.3 编写 docker-compose.yml (PostgreSQL, Backend, Frontend, Nginx)
[ ] 2.2.4 编写 Nginx 配置文件
[ ] 2.2.5 编写 .env.example 文件
[ ] 2.2.6 测试 Docker 环境启动和服务连通性
Phase 2: 核心功能 - 模块与标签
3. Day 3: 模块与标签管理
3.1 模块管理后端
[ ] 3.1.1 实现 Module Repository (CRUD 操作)
[ ] 3.1.2 实现 Module Service (业务逻辑，树形结构构建)
[ ] 3.1.3 实现 Module Handler (GET /modules/tree)
[ ] 3.1.4 实现 Module Handler (POST /modules)
[ ] 3.1.5 实现 Module Handler (PUT /modules/:id)
[ ] 3.1.6 实现 Module Handler (DELETE /modules/:id)
[ ] 3.1.7 编写模块管理单元测试
3.2 标签管理后端
[ ] 3.2.1 实现 Tag Repository (CRUD 操作)
[ ] 3.2.2 实现 Tag Service (业务逻辑，使用统计)
[ ] 3.2.3 实现 Tag Handler (GET /tags)
[ ] 3.2.4 实现 Tag Handler (POST /tags)
[ ] 3.2.5 实现 Tag Handler (PUT /tags/:id)
[ ] 3.2.6 实现 Tag Handler (DELETE /tags/:id)
3.3 模块与标签前端
[ ] 3.3.1 创建 ModuleTree 组件 (树形展示)
[ ] 3.3.2 实现 ModuleTree 展开/折叠功能
[ ] 3.3.3 实现 ModuleTree 右键菜单 (新建/编辑/删除)
[ ] 3.3.4 创建 ModuleForm 组件 (创建/编辑模块)
[ ] 3.3.5 创建 TagSelect 组件 (下拉多选)
[ ] 3.3.6 实现 TagSelect 创建新标签功能
[ ] 3.3.7 创建 TagManagement 页面
[ ] 3.3.8 集成 API 调用并测试功能
Phase 3: PRD 文档管理
4. Day 4: PRD 后端 API
4.1 PRD CRUD API
[ ] 4.1.1 实现 PRD Repository (基础 CRUD)
[ ] 4.1.2 实现 PRD Service (业务逻辑)
[ ] 4.1.3 实现 PRD Handler (GET /prds - 列表，分页，筛选)
[ ] 4.1.4 实现 PRD Handler (GET /prds/:id - 详情)
[ ] 4.1.5 实现 PRD Handler (POST /prds - 创建)
[ ] 4.1.6 实现 PRD Handler (PUT /prds/:id - 更新)
[ ] 4.1.7 实现 PRD Handler (DELETE /prds/:id - 软删除)
4.2 PRD 版本管理
[ ] 4.2.1 实现 PRDVersion Repository
[ ] 4.2.2 实现版本自动创建逻辑
[ ] 4.2.3 实现 PRD Handler (GET /prds/:id/versions)
[ ] 4.2.4 实现 PRD Handler (GET /prds/:id/versions/:version)
[ ] 4.2.5 实现 PRD 标签关联逻辑
[ ] 4.2.6 编写 PRD 管理单元测试
5. Day 5: PRD 前端页面
5.1 PRD 列表与详情
[ ] 5.1.1 创建 PRDList 页面 (表格展示)
[ ] 5.1.2 实现 PRD 搜索框
[ ] 5.1.3 实现 PRD 筛选器 (模块、状态、标签)
[ ] 5.1.4 实现 PRD 分页
[ ] 5.1.5 创建 PRDDetail 页面
[ ] 5.1.6 实现 Markdown 渲染 (使用 react-markdown)
[ ] 5.1.7 实现版本历史展示
[ ] 5.1.8 实现关联测试用例列表
5.2 PRD 创建与编辑
[ ] 5.2.1 集成 Monaco Editor
[ ] 5.2.2 实现 Markdown 实时预览
[ ] 5.2.3 创建 MarkdownEditor 组件
[ ] 5.2.4 创建 PRDForm 页面 (基本信息表单)
[ ] 5.2.5 实现 PRD 保存功能
[ ] 5.2.6 实现 PRD 发布功能
[ ] 5.2.7 实现表单验证
[ ] 5.2.8 测试 PRD 完整流程
Phase 4: 测试用例管理
6. Day 6: 测试用例后端 API
6.1 测试用例 CRUD
[ ] 6.1.1 实现 TestCase Repository (基础 CRUD)
[ ] 6.1.2 实现 TestStep Repository (步骤管理)
[ ] 6.1.3 实现 TestCase Service (业务逻辑)
[ ] 6.1.4 实现 TestCase Handler (GET /testcases - 列表)
[ ] 6.1.5 实现 TestCase Handler (GET /testcases/:id - 详情)
[ ] 6.1.6 实现 TestCase Handler (POST /testcases - 创建)
[ ] 6.1.7 实现 TestCase Handler (PUT /testcases/:id - 更新)
[ ] 6.1.8 实现 TestCase Handler (DELETE /testcases/:id - 删除)
[ ] 6.1.9 实现测试步骤自动排序逻辑
6.2 文件上传功能
[ ] 6.2.1 实现文件存储服务 (本地存储)
[ ] 6.2.2 实现文件上传 Handler (POST /upload/screenshot)
[ ] 6.2.3 实现文件删除 Handler (DELETE /upload/:id)
[ ] 6.2.4 实现文件验证 (类型、大小)
[ ] 6.2.5 实现 Screenshot Repository
[ ] 6.2.6 实现截图与步骤关联逻辑
[ ] 6.2.7 配置静态文件服务
[ ] 6.2.8 编写文件上传单元测试
7. Day 7: 测试用例前端 (列表与详情)
7.1 测试用例列表
[ ] 7.1.1 创建 TestCaseList 页面
[ ] 7.1.2 实现测试用例表格展示
[ ] 7.1.3 实现多维度筛选器 (模块、优先级、类型、状态、标签)
[ ] 7.1.4 实现搜索功能
[ ] 7.1.5 实现批量操作 UI
[ ] 7.1.6 实现分页
7.2 测试用例详情
[ ] 7.2.1 创建 TestCaseDetail 页面
[ ] 7.2.2 实现基本信息展示
[ ] 7.2.3 实现前置条件展示
[ ] 7.2.4 实现测试步骤展示
[ ] 7.2.5 创建 ImagePreview 组件 (截图预览)
[ ] 7.2.6 实现截图点击放大功能
[ ] 7.2.7 实现预期结果展示
[ ] 7.2.8 实现版本历史展示
8. Day 8: 测试用例前端 (创建与编辑)
8.1 测试用例表单
[ ] 8.1.1 创建 TestCaseForm 页面
[ ] 8.1.2 实现基本信息表单
[ ] 8.1.3 实现前置条件输入
[ ] 8.1.4 实现预期结果输入
[ ] 8.1.5 实现标签选择
[ ] 8.1.6 实现表单验证
8.2 测试步骤编辑
[ ] 8.2.1 创建 TestStepForm 组件
[ ] 8.2.2 实现添加步骤功能
[ ] 8.2.3 实现删除步骤功能
[ ] 8.2.4 实现步骤排序 (拖拽)
[ ] 8.2.5 创建 ImageUpload 组件
[ ] 8.2.6 实现拖拽上传截图
[ ] 8.2.7 实现多文件上传
[ ] 8.2.8 实现截图预览和删除
[ ] 8.2.9 测试用例创建完整流程
Phase 5: 导入功能 (已取消 - 改为手动添加)
~~9. Day 9: Excel 导入~~
~~9.1 Excel 解析~~
~~[ ] 9.1.1 安装 Excel 解析库 (excelize)~~
~~[ ] 9.1.2 实现 Excel 文件读取~~
~~[ ] 9.1.3 实现表头解析和验证~~
~~[ ] 9.1.4 实现数据行解析~~
~~[ ] 9.1.5 实现数据验证逻辑~~
~~[ ] 9.1.6 实现错误收集机制~~
~~9.2 Excel 导入 API 与前端~~
~~[ ] 9.2.1 实现批量创建测试用例逻辑 (事务)~~
~~[ ] 9.2.2 实现 Import Handler (POST /import/excel)~~
~~[ ] 9.2.3 创建 Excel 模板文件~~
~~[ ] 9.2.4 创建 Import 页面~~
~~[ ] 9.2.5 实现文件上传组件~~
~~[ ] 9.2.6 实现模板下载功能~~
~~[ ] 9.2.7 实现导入预览~~
~~[ ] 9.2.8 实现导入结果展示~~
~~[ ] 9.2.9 测试 Excel 导入功能~~
~~10. Day 10: XMind 和 Word 导入~~
~~10.1 XMind 导入~~
~~[ ] 10.1.1 研究 XMind 文件格式 (ZIP + XML)~~
~~[ ] 10.1.2 实现 XMind 文件解压~~
~~[ ] 10.1.3 实现 XML 内容解析~~
~~[ ] 10.1.4 实现思维导图结构转换为测试用例~~
~~[ ] 10.1.5 实现 Import Handler (POST /import/xmind)~~
~~[ ] 10.1.6 前端集成 XMind 导入~~
~~10.2 Word 导入~~
~~[ ] 10.2.1 安装 Word 解析库~~
~~[ ] 10.2.2 实现 .docx 文件解析~~
~~[ ] 10.2.3 实现文本内容提取~~
~~[ ] 10.2.4 实现 Markdown 转换~~
~~[ ] 10.2.5 实现 Import Handler (POST /import/word)~~
~~[ ] 10.2.6 前端集成 Word 导入~~
~~[ ] 10.2.7 测试所有导入功能~~

**注：导入功能已取消，改为手动精细添加和清洗测试用例数据**
Phase 6: RAG 检索功能
11. Day 11: Weaviate 集成
11.1 Weaviate 配置
[ ] 11.1.1 配置 Weaviate 连接 (复用 Dify 实例)
[ ] 11.1.2 创建 PRDDocument Collection Schema
[ ] 11.1.3 创建 TestCase Collection Schema
[ ] 11.1.4 实现 Weaviate Repository
[ ] 11.1.5 实现向量化服务 (调用 BrConnector Claude 4.5)
11.2 数据同步
[ ] 11.2.1 实现 PRD 创建时同步到 Weaviate
[ ] 11.2.2 实现 PRD 更新时同步到 Weaviate
[ ] 11.2.3 实现 PRD 删除时同步到 Weaviate
[ ] 11.2.4 实现测试用例创建时同步到 Weaviate
[ ] 11.2.5 实现测试用例更新时同步到 Weaviate
[ ] 11.2.6 实现测试用例删除时同步到 Weaviate
[ ] 11.2.7 实现批量同步脚本 (同步历史数据)
[ ] 11.2.8 测试数据同步功能
12. Day 12: 语义检索与推荐
12.1 语义检索 API
[ ] 12.1.1 实现 RAG Service (语义检索逻辑)
[ ] 12.1.2 实现查询向量化
[ ] 12.1.3 实现 Weaviate 向量搜索
[ ] 12.1.4 实现结构化过滤组合
[ ] 12.1.5 实现结果排序和高亮
[ ] 12.1.6 实现 Search Handler (POST /search)
[ ] 12.1.7 实现关联推荐逻辑
[ ] 12.1.8 实现 Recommend Handler (GET /recommend/:prd_id)
12.2 前端搜索页面
[ ] 12.2.1 创建 Search 页面
[ ] 12.2.2 实现搜索框组件
[ ] 12.2.3 实现类型筛选 (PRD/测试用例/全部)
[ ] 12.2.4 实现结果分类展示
[ ] 12.2.5 实现关键词高亮
[ ] 12.2.6 集成全局搜索 (顶部导航栏)
[ ] 12.2.7 实现快捷键支持 (Ctrl+K)
[ ] 12.2.8 测试搜索功能
Phase 7: Dify 集成
13. Day 13: Dify 外部知识库 API
13.1 实现 Dify 接口
[ ] 13.1.1 研究 Dify 外部知识库 API 规范
[ ] 13.1.2 实现 Dify Service (检索逻辑)
[ ] 13.1.3 实现请求格式解析 (query, top_k, score_threshold, filters)
[ ] 13.1.4 实现响应格式化 (records, content, score, metadata)
[ ] 13.1.5 实现 Dify Handler (POST /dify/retrieval)
[ ] 13.1.6 编写 Dify 接口文档
13.2 Dify 配置与测试
[ ] 13.2.1 在 Dify 中配置外部知识库
[ ] 13.2.2 配置 API 端点和认证
[ ] 13.2.3 在 Dify Agent 中测试检索
[ ] 13.2.4 验证返回结果格式
[ ] 13.2.5 实现影响分析 Service
[ ] 13.2.6 实现 Impact Analysis Handler (POST /impact-analysis)
[ ] 13.2.7 测试影响分析功能
Phase 8: 优化与完善
14. Day 14: 功能完善与优化
14.1 功能完善
[ ] 14.1.1 实现统计 Service
[ ] 14.1.2 实现 Statistics Handler (GET /statistics)
[ ] 14.1.3 创建 Dashboard 页面
[ ] 14.1.4 实现统计卡片组件
[ ] 14.1.5 实现图表展示 (使用 recharts)
[ ] 14.1.6 实现最近更新列表
[ ] 14.1.7 实现批量删除 Handler (POST /testcases/batch-delete)
[ ] 14.1.8 实现批量操作前端 UI
14.2 性能优化
[ ] 14.2.1 优化数据库查询 (添加索引)
[ ] 14.2.2 优化 API 响应时间
[ ] 14.2.3 实现前端代码分割
[ ] 14.2.4 实现图片懒加载
[ ] 14.2.5 实现列表虚拟滚动 (react-window)
[ ] 14.2.6 配置 React Query 缓存策略
[ ] 14.2.7 配置静态资源缓存
15. Day 15: 测试、文档与部署
15.1 测试
[ ] 15.1.1 执行完整功能测试 (PRD 管理)
[ ] 15.1.2 执行完整功能测试 (测试用例管理)
[ ] 15.1.3 执行完整功能测试 (导入功能)
[ ] 15.1.4 执行完整功能测试 (RAG 检索)
[ ] 15.1.5 执行完整功能测试 (Dify 集成)
[ ] 15.1.6 执行边界情况测试
[ ] 15.1.7 执行错误处理测试
[ ] 15.1.8 执行性能测试 (大数据量)
[ ] 15.1.9 修复发现的 Bug
15.2 文档与部署
[ ] 15.2.1 完善 API 文档 (Swagger)
[ ] 15.2.2 编写用户使用手册
[ ] 15.2.3 编写部署文档
[ ] 15.2.4 配置生产环境变量
[ ] 15.2.5 构建 Docker 镜像
[ ] 15.2.6 配置 Nginx 生产环境
[ ] 15.2.7 执行正式部署
[ ] 15.2.8 验证所有功能
[ ] 15.2.9 项目交付验收