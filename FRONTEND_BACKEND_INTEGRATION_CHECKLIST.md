# 前后端联调检查清单

## 联调准备

### 环境检查
- [ ] 后端服务运行正常（http://localhost:8080）
- [ ] 前端服务运行正常（http://localhost:5173）
- [ ] PostgreSQL 数据库连接正常
- [ ] Weaviate 向量数据库运行正常（http://localhost:8009）
- [ ] Embedding 服务配置正确（火山引擎 Ark API）
- [ ] CORS 配置允许前端访问

### 测试数据准备
- [ ] 创建测试项目（至少 2 个）
- [ ] 创建模块树结构（至少 3 层）
- [ ] 创建标签（至少 5 个）
- [ ] 创建 PRD 文档（至少 10 个，不同状态）
- [ ] 创建测试用例（至少 20 个，不同优先级和类型）
- [ ] 确保数据已同步到 Weaviate

---

## 功能联调清单

### 1. 项目管理 ✅

#### 1.1 项目列表页面
- [ ] 获取项目列表
- [ ] 显示项目卡片（名称、描述、统计数据）
- [ ] 创建新项目
- [ ] 进入项目详情

#### 1.2 项目详情/编辑
- [ ] 查看项目详情
- [ ] 编辑项目信息
- [ ] 删除项目（带确认）
- [ ] 查看项目统计

**API 端点**:
- `GET /api/v1/projects` - 获取项目列表
- `POST /api/v1/projects` - 创建项目
- `GET /api/v1/projects/:id` - 获取项目详情
- `PUT /api/v1/projects/:id` - 更新项目
- `DELETE /api/v1/projects/:id` - 删除项目

---

### 2. 模块管理 ✅

#### 2.1 模块树展示
- [ ] 获取模块树
- [ ] 树形结构正确显示
- [ ] 展开/折叠节点
- [ ] 显示模块统计

#### 2.2 模块操作
- [ ] 创建根模块
- [ ] 创建子模块
- [ ] 编辑模块
- [ ] 删除模块（带确认）
- [ ] 模块排序/拖拽

**API 端点**:
- `GET /api/v1/projects/:id/modules/tree` - 获取模块树
- `POST /api/v1/projects/:id/modules` - 创建模块
- `PUT /api/v1/projects/:id/modules/:module_id` - 更新模块
- `DELETE /api/v1/projects/:id/modules/:module_id` - 删除模块
- `PUT /api/v1/projects/:id/modules/sort` - 模块排序

---

### 3. 标签管理 ✅

#### 3.1 标签列表
- [ ] 获取所有标签
- [ ] 显示标签（名称、颜色、使用次数）
- [ ] 创建新标签
- [ ] 编辑标签
- [ ] 删除标签（带确认）

#### 3.2 标签使用统计
- [ ] 查看标签使用情况
- [ ] 显示关联的 PRD 和测试用例数量

**API 端点**:
- `GET /api/v1/projects/:id/tags` - 获取标签列表
- `POST /api/v1/projects/:id/tags` - 创建标签
- `PUT /api/v1/projects/:id/tags/:tag_id` - 更新标签
- `DELETE /api/v1/projects/:id/tags/:tag_id` - 删除标签
- `GET /api/v1/projects/:id/tags/:tag_id/usage` - 标签使用统计

---

### 4. PRD 文档管理 ✅

#### 4.1 PRD 列表页面
- [ ] 获取 PRD 列表（分页）
- [ ] 按模块筛选
- [ ] 按状态筛选
- [ ] 按 App 版本筛选
- [ ] 按标签筛选
- [ ] 关键词搜索
- [ ] 排序功能
- [ ] 创建新 PRD

#### 4.2 PRD 详情页面
- [ ] 查看 PRD 详情
- [ ] Markdown 内容渲染
- [ ] 显示关联的测试用例
- [ ] 显示标签
- [ ] 显示版本信息

#### 4.3 PRD 编辑页面
- [ ] 编辑 PRD 基本信息
- [ ] Markdown 编辑器
- [ ] 选择模块
- [ ] 选择 App 版本
- [ ] 添加/删除标签
- [ ] 保存并创建版本

#### 4.4 PRD 状态管理
- [ ] 更新状态
- [ ] 发布 PRD
- [ ] 归档 PRD

#### 4.5 PRD 版本管理
- [ ] 查看版本列表
- [ ] 查看历史版本内容
- [ ] 版本对比

**API 端点**:
- `GET /api/v1/projects/:id/prds` - 获取 PRD 列表
- `POST /api/v1/projects/:id/prds` - 创建 PRD
- `GET /api/v1/projects/:id/prds/:prd_id` - 获取 PRD 详情
- `PUT /api/v1/projects/:id/prds/:prd_id` - 更新 PRD
- `DELETE /api/v1/projects/:id/prds/:prd_id` - 删除 PRD
- `PUT /api/v1/projects/:id/prds/:prd_id/status` - 更新状态
- `POST /api/v1/projects/:id/prds/:prd_id/publish` - 发布 PRD
- `POST /api/v1/projects/:id/prds/:prd_id/archive` - 归档 PRD
- `GET /api/v1/projects/:id/prds/:prd_id/versions` - 获取版本列表
- `GET /api/v1/projects/:id/prds/:prd_id/versions/:version` - 获取版本内容
- `GET /api/v1/projects/:id/prds/:prd_id/versions/compare` - 版本对比
- `POST /api/v1/projects/:id/prds/:prd_id/tags` - 添加标签
- `DELETE /api/v1/projects/:id/prds/:prd_id/tags/:tag_id` - 删除标签

---

### 5. 测试用例管理 ✅

#### 5.1 测试用例列表页面
- [ ] 获取测试用例列表（分页）
- [ ] 按 PRD 筛选
- [ ] 按模块筛选
- [ ] 按优先级筛选
- [ ] 按类型筛选
- [ ] 按状态筛选
- [ ] 按标签筛选
- [ ] 关键词搜索
- [ ] 排序功能
- [ ] 创建新测试用例
- [ ] 批量删除

#### 5.2 测试用例详情页面
- [ ] 查看测试用例详情
- [ ] 显示测试步骤
- [ ] 显示关联的 PRD
- [ ] 显示标签
- [ ] 显示版本信息

#### 5.3 测试用例编辑页面
- [ ] 编辑基本信息
- [ ] 选择关联 PRD
- [ ] 选择模块
- [ ] 选择 App 版本
- [ ] 设置优先级和类型
- [ ] 添加/删除/排序测试步骤
- [ ] 添加/删除标签
- [ ] 保存并创建版本

#### 5.4 测试步骤管理
- [ ] 动态添加步骤
- [ ] 编辑步骤内容
- [ ] 删除步骤
- [ ] 步骤排序

#### 5.5 测试用例版本管理
- [ ] 查看版本列表
- [ ] 查看历史版本内容

**API 端点**:
- `GET /api/v1/projects/:id/testcases` - 获取测试用例列表
- `POST /api/v1/projects/:id/testcases` - 创建测试用例
- `GET /api/v1/projects/:id/testcases/:testcase_id` - 获取测试用例详情
- `PUT /api/v1/projects/:id/testcases/:testcase_id` - 更新测试用例
- `DELETE /api/v1/projects/:id/testcases/:testcase_id` - 删除测试用例
- `POST /api/v1/projects/:id/testcases/batch-delete` - 批量删除
- `POST /api/v1/projects/:id/testcases/:testcase_id/tags` - 添加标签
- `DELETE /api/v1/projects/:id/testcases/:testcase_id/tags/:tag_id` - 删除标签
- `GET /api/v1/projects/:id/testcases/:testcase_id/versions` - 获取版本列表
- `GET /api/v1/projects/:id/testcases/:testcase_id/versions/:version` - 获取版本内容

---

### 6. 统计功能 ✅

#### 6.1 仪表盘页面
- [ ] 显示项目统计数据
  - [ ] 总 PRD 数量
  - [ ] 总测试用例数量
  - [ ] 按优先级统计
  - [ ] 按类型统计
  - [ ] 按状态统计
  - [ ] 按模块统计

#### 6.2 趋势分析
- [ ] PRD 创建趋势图表
- [ ] 测试用例创建趋势图表
- [ ] 时间范围筛选

#### 6.3 覆盖率统计
- [ ] 整体覆盖率
- [ ] 按模块覆盖率
- [ ] 未覆盖的 PRD 列表

**API 端点**:
- `GET /api/v1/projects/:id/statistics` - 获取项目统计
- `GET /api/v1/projects/:id/statistics/trends` - 获取趋势数据
- `GET /api/v1/projects/:id/statistics/coverage` - 获取覆盖率

---

### 7. 语义检索功能 ✅

#### 7.1 搜索页面
- [ ] 输入搜索关键词
- [ ] 选择搜索类型（PRD/测试用例/全部）
- [ ] 高级筛选
  - [ ] App 版本
  - [ ] 模块
  - [ ] 优先级
  - [ ] 状态
- [ ] 搜索参数配置
  - [ ] 混合检索权重（Alpha）滑块
  - [ ] 相似度阈值滑块
- [ ] 显示搜索结果
  - [ ] 按类型分组
  - [ ] 相似度评分
  - [ ] 高亮显示
  - [ ] 点击跳转详情

#### 7.2 推荐功能
- [ ] PRD 详情页显示相关推荐
- [ ] 测试用例详情页显示相关推荐
- [ ] 推荐结果可点击跳转

**API 端点**:
- `POST /api/v1/projects/:id/search` - 语义搜索
- `GET /api/v1/projects/:id/prds/:prd_id/recommendations` - PRD 推荐
- `GET /api/v1/projects/:id/testcases/:testcase_id/recommendations` - 测试用例推荐

---

### 8. 设置功能 ✅

#### 8.1 搜索配置页面
- [ ] 显示当前搜索配置
  - [ ] 默认混合检索权重
  - [ ] 默认结果数量
  - [ ] 默认相似度阈值
  - [ ] 是否启用混合检索
- [ ] 修改配置
- [ ] 保存配置
- [ ] 配置说明和提示

#### 8.2 Embedding 配置页面
- [ ] 显示 Embedding 配置
- [ ] 修改配置（如果需要）

**API 端点**:
- `GET /api/v1/settings` - 获取所有设置
- `GET /api/v1/settings/:category` - 按类别获取设置
- `PUT /api/v1/settings/:key` - 更新单个设置
- `PUT /api/v1/settings/batch` - 批量更新设置

---

## 常见问题排查

### 1. CORS 错误
**症状**: 前端请求被浏览器拦截，控制台显示 CORS 错误

**解决方案**:
- 检查后端 CORS 中间件配置
- 确认允许的源包含前端地址（http://localhost:5173）
- 检查是否允许必要的 HTTP 方法和头部

### 2. 404 错误
**症状**: API 请求返回 404

**解决方案**:
- 检查 API 路径是否正确
- 检查路由是否正确注册
- 检查项目 ID 是否正确传递

### 3. 500 错误
**症状**: API 请求返回 500 内部服务器错误

**解决方案**:
- 查看后端日志
- 检查数据库连接
- 检查 Weaviate 连接
- 检查 Embedding 服务配置

### 4. 数据不显示
**症状**: 列表为空或数据不完整

**解决方案**:
- 检查数据库中是否有数据
- 检查筛选条件是否过于严格
- 检查分页参数
- 检查项目 ID 是否正确

### 5. 搜索无结果
**症状**: 语义搜索返回空结果

**解决方案**:
- 检查 Weaviate 是否运行
- 检查数据是否已同步到 Weaviate
- 检查 Embedding 服务是否正常
- 降低相似度阈值
- 检查搜索关键词

---

## 测试数据示例

### 项目数据
```json
{
  "name": "电商平台",
  "description": "电商平台测试项目"
}
```

### 模块数据
```
电商平台
├── 用户管理
│   ├── 用户注册
│   ├── 用户登录
│   └── 个人中心
├── 商品管理
│   ├── 商品列表
│   ├── 商品详情
│   └── 商品搜索
└── 订单管理
    ├── 创建订单
    ├── 订单支付
    └── 订单查询
```

### 标签数据
- 核心功能（红色）
- 高优先级（橙色）
- 性能优化（蓝色）
- 安全相关（紫色）
- 用户体验（绿色）

### PRD 示例
- 标题：用户登录功能需求文档
- 模块：用户管理/用户登录
- 状态：已发布
- 内容：包含功能概述、需求详情、交互设计等

### 测试用例示例
- 标题：用户登录-正常登录
- 关联 PRD：用户登录功能需求文档
- 模块：用户管理/用户登录
- 优先级：高
- 类型：功能测试
- 测试步骤：3-5 个步骤

---

## 联调完成标准

### 功能完整性
- [ ] 所有核心功能可正常使用
- [ ] 所有 API 调用成功
- [ ] 数据正确显示和更新
- [ ] 错误提示友好清晰

### 用户体验
- [ ] 页面加载速度合理（< 2s）
- [ ] 操作响应及时
- [ ] 交互流畅自然
- [ ] 无明显 Bug

### 数据一致性
- [ ] 前后端数据一致
- [ ] 数据库数据正确
- [ ] Weaviate 数据同步正常

### 文档完整性
- [ ] API 文档准确
- [ ] 已知问题记录
- [ ] 待优化项列表

---

## 联调报告模板

### 测试环境
- 后端版本：
- 前端版本：
- 数据库版本：
- Weaviate 版本：

### 测试结果
- 通过的功能：
- 失败的功能：
- 发现的 Bug：
- 性能问题：

### 待优化项
1. 
2. 
3. 

### 下一步计划
1. 
2. 
3. 

---

**联调负责人**: ___________
**联调日期**: ___________
**完成日期**: ___________
