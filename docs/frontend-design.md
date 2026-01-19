# 前端设计文档

## 技术栈

- **框架**: React 18 + TypeScript 5
- **构建工具**: Vite 5
- **UI 组件库**: Ant Design 5.x
- **路由**: React Router v6
- **状态管理**: 
  - React Query (服务端状态)
  - Zustand (客户端状态)
- **表单**: React Hook Form + Zod
- **编辑器**: Monaco Editor (Markdown)
- **图片上传**: react-dropzone
- **HTTP 客户端**: Axios
- **样式**: Tailwind CSS + Ant Design

## 页面结构

```
┌─────────────────────────────────────────────────────────┐
│                      顶部导航栏                          │
│  Logo | PRD 管理 | 测试用例 | 导入 | 统计                │
└─────────────────────────────────────────────────────────┘
┌──────────┬──────────────────────────────────────────────┐
│          │                                              │
│          │                                              │
│  侧边栏   │              主内容区                         │
│          │                                              │
│  模块树   │                                              │
│          │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

## 页面设计

### 1. 仪表盘（Dashboard）

**路由**: `/`

**功能**:
- 统计卡片（PRD 总数、测试用例总数、按优先级统计）
- 最近更新的 PRD
- 最近更新的测试用例
- 快速操作入口

**组件结构**:
```tsx
<Dashboard>
  <StatisticsCards />
  <RecentPRDs />
  <RecentTestCases />
  <QuickActions />
</Dashboard>
```

### 2. PRD 管理

#### 2.1 PRD 列表页

**路由**: `/prds`

**功能**:
- 列表展示（表格）
- 搜索（关键词、标签）
- 筛选（模块、状态）
- 排序（创建时间、更新时间）
- 批量操作
- 新建 PRD 按钮

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 搜索框 | 筛选器 | 新建按钮                                 │
├─────────────────────────────────────────────────────────┤
│ 编号 | 标题 | 版本 | 模块 | 状态 | 更新时间 | 操作        │
│ PRD_001 | 用户登录 | v1.0 | 登录 | 已发布 | 2025-01-19 | 查看/编辑/删除 │
│ ...                                                      │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<PRDList>
  <SearchBar />
  <FilterBar>
    <ModuleFilter />
    <StatusFilter />
    <TagFilter />
  </FilterBar>
  <PRDTable>
    <PRDRow />
  </PRDTable>
  <Pagination />
</PRDList>
```

#### 2.2 PRD 详情页

**路由**: `/prds/:id`

**功能**:
- 显示 PRD 完整信息
- Markdown 渲染
- 版本历史
- 关联测试用例列表
- 编辑/删除操作

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 返回 | 编辑 | 删除 | 新建版本                             │
├─────────────────────────────────────────────────────────┤
│ PRD_LOGIN_001 | v1.0 | 登录注册 | 已发布                 │
│ 标签: [登录] [认证]                                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│              Markdown 内容渲染区                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ 版本历史 | 关联测试用例                                   │
│ v1.0 (2025-01-19) - 初始版本                            │
│ TC_LOGIN_001 - 正常登录流程验证                          │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<PRDDetail>
  <PRDHeader>
    <ActionButtons />
    <PRDMeta />
  </PRDHeader>
  <MarkdownViewer content={prd.content} />
  <Tabs>
    <TabPane tab="版本历史">
      <VersionHistory />
    </TabPane>
    <TabPane tab="关联测试用例">
      <RelatedTestCases />
    </TabPane>
  </Tabs>
</PRDDetail>
```

#### 2.3 PRD 创建/编辑页

**路由**: `/prds/create` | `/prds/:id/edit`

**功能**:
- 表单录入（编号、标题、版本、模块、状态）
- Markdown 编辑器（实时预览）
- 标签选择
- 保存草稿
- 发布

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 保存草稿 | 发布 | 取消                                     │
├─────────────────────────────────────────────────────────┤
│ 基本信息                                                 │
│ 编号: [PRD_LOGIN_001]  版本: [v1.0]                     │
│ 标题: [用户登录功能需求]                                 │
│ 模块: [下拉选择]  状态: [下拉选择]                       │
│ 标签: [标签选择器]                                       │
├─────────────────────────────────────────────────────────┤
│ 内容编辑                                                 │
│ ┌──────────────┬──────────────┐                        │
│ │ Markdown编辑 │  实时预览     │                        │
│ │              │              │                        │
│ │              │              │                        │
│ └──────────────┴──────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<PRDForm>
  <FormHeader>
    <SaveButton />
    <PublishButton />
  </FormHeader>
  <BasicInfoSection>
    <Input name="code" />
    <Input name="title" />
    <Input name="version" />
    <Select name="module_id" />
    <Select name="status" />
    <TagSelect name="tags" />
  </BasicInfoSection>
  <MarkdownEditor
    value={content}
    onChange={setContent}
    preview={true}
  />
</PRDForm>
```

### 3. 测试用例管理

#### 3.1 测试用例列表页

**路由**: `/testcases`

**功能**:
- 列表展示（表格）
- 多维度筛选（模块、优先级、类型、状态、标签）
- 搜索
- 批量操作
- 导出
- 新建用例按钮

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 搜索框 | 筛选器 | 新建 | 批量导入 | 导出                   │
├─────────────────────────────────────────────────────────┤
│ 编号 | 标题 | PRD | 优先级 | 类型 | 状态 | 标签 | 操作    │
│ TC_001 | 正常登录 | PRD_001 | P0 | 功能 | 激活 | [登录] | 查看/编辑/删除 │
│ ...                                                      │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<TestCaseList>
  <SearchBar />
  <FilterBar>
    <ModuleFilter />
    <PriorityFilter />
    <TypeFilter />
    <StatusFilter />
    <TagFilter />
  </FilterBar>
  <ActionBar>
    <CreateButton />
    <ImportButton />
    <ExportButton />
  </ActionBar>
  <TestCaseTable>
    <TestCaseRow />
  </TestCaseTable>
  <Pagination />
</TestCaseList>
```

#### 3.2 测试用例详情页

**路由**: `/testcases/:id`

**功能**:
- 显示用例完整信息
- 测试步骤展示（含截图）
- 关联 PRD 信息
- 版本历史
- 编辑/删除操作

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 返回 | 编辑 | 删除 | 复制                                 │
├─────────────────────────────────────────────────────────┤
│ TC_LOGIN_001 | 正常登录流程验证                          │
│ 优先级: P0 | 类型: 功能测试 | 状态: 激活                 │
│ 关联 PRD: PRD_LOGIN_001 v1.0                            │
│ 标签: [登录] [冒烟测试]                                  │
├─────────────────────────────────────────────────────────┤
│ 前置条件:                                                │
│ 1. 用户已注册                                            │
│ 2. 账号状态正常                                          │
├─────────────────────────────────────────────────────────┤
│ 测试步骤:                                                │
│ 步骤 1: 打开 APP 登录页面                                │
│   预期: 显示登录页面                                     │
│   [截图1] [截图2]                                        │
│                                                          │
│ 步骤 2: 输入正确的手机号                                 │
│   测试数据: 13800138000                                  │
│   预期: 手机号输入框显示输入内容                          │
│   [截图3]                                                │
├─────────────────────────────────────────────────────────┤
│ 预期结果:                                                │
│ 登录成功，跳转到首页                                     │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<TestCaseDetail>
  <TestCaseHeader>
    <ActionButtons />
    <TestCaseMeta />
  </TestCaseHeader>
  <PreconditionsSection />
  <TestStepsSection>
    <TestStep>
      <StepNumber />
      <StepAction />
      <StepData />
      <StepExpected />
      <Screenshots>
        <ImagePreview />
      </Screenshots>
    </TestStep>
  </TestStepsSection>
  <ExpectedResultSection />
  <Tabs>
    <TabPane tab="版本历史">
      <VersionHistory />
    </TabPane>
  </Tabs>
</TestCaseDetail>
```

#### 3.3 测试用例创建/编辑页

**路由**: `/testcases/create` | `/testcases/:id/edit`

**功能**:
- 基本信息表单
- 动态添加/删除测试步骤
- 每个步骤支持上传多张截图
- 截图预览和删除
- 标签管理
- 保存/提交

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 保存 | 取消                                              │
├─────────────────────────────────────────────────────────┤
│ 基本信息                                                 │
│ 编号: [TC_LOGIN_001]  标题: [正常登录流程验证]           │
│ 关联 PRD: [下拉选择]  版本: [v1.0]                       │
│ 模块: [下拉选择]                                         │
│ 优先级: [P0▼]  类型: [功能测试▼]  状态: [激活▼]         │
│ 标签: [标签选择器]                                       │
├─────────────────────────────────────────────────────────┤
│ 前置条件:                                                │
│ [文本域]                                                 │
├─────────────────────────────────────────────────────────┤
│ 测试步骤: [+ 添加步骤]                                   │
│ ┌───────────────────────────────────────────────────┐  │
│ │ 步骤 1                                    [删除]   │  │
│ │ 操作: [输入框]                                     │  │
│ │ 测试数据: [输入框]                                 │  │
│ │ 预期: [输入框]                                     │  │
│ │ 截图: [上传区域] [预览1] [预览2]                   │  │
│ └───────────────────────────────────────────────────┘  │
│ ┌───────────────────────────────────────────────────┐  │
│ │ 步骤 2                                    [删除]   │  │
│ │ ...                                                │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ 预期结果:                                                │
│ [文本域]                                                 │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<TestCaseForm>
  <FormHeader>
    <SaveButton />
    <CancelButton />
  </FormHeader>
  <BasicInfoSection>
    <Input name="code" />
    <Input name="title" />
    <Select name="prd_id" />
    <Input name="prd_version" />
    <Select name="module_id" />
    <Select name="priority" />
    <Select name="type" />
    <Select name="status" />
    <TagSelect name="tags" />
  </BasicInfoSection>
  <PreconditionsSection>
    <TextArea name="preconditions" />
  </PreconditionsSection>
  <TestStepsSection>
    <TestStepForm>
      <Input name="action" />
      <Input name="test_data" />
      <Input name="expected" />
      <ImageUpload
        multiple
        onUpload={handleUpload}
      />
      <ImagePreviewList />
    </TestStepForm>
    <AddStepButton />
  </TestStepsSection>
  <ExpectedResultSection>
    <TextArea name="expected_result" />
  </ExpectedResultSection>
</TestCaseForm>
```

### 4. 导入页面

#### 4.1 导入页面

**路由**: `/import`

**功能**:
- 选择导入类型（Excel/XMind/Word）
- 文件上传
- 模板下载
- 导入预览
- 错误提示
- 导入结果展示

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 导入类型: [Excel▼] [XMind] [Word]                       │
├─────────────────────────────────────────────────────────┤
│ 目标模块: [下拉选择]                                     │
│ 关联 PRD: [下拉选择（可选）]                             │
├─────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────┐  │
│ │                                                    │  │
│ │         拖拽文件到此处或点击上传                    │  │
│ │                                                    │  │
│ │         [下载模板]                                 │  │
│ │                                                    │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ 导入预览:                                                │
│ 将导入 50 条测试用例                                     │
│ [预览表格]                                               │
├─────────────────────────────────────────────────────────┤
│ [开始导入]                                               │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<ImportPage>
  <ImportTypeSelector />
  <TargetSelector>
    <ModuleSelect />
    <PRDSelect />
  </TargetSelector>
  <FileUploader
    accept=".xlsx,.xmind,.docx"
    onUpload={handleUpload}
  />
  <TemplateDownload />
  <ImportPreview>
    <PreviewTable />
  </ImportPreview>
  <ImportButton />
  <ImportResult>
    <SuccessCount />
    <ErrorList />
  </ImportResult>
</ImportPage>
```

### 5. 搜索页面

**路由**: `/search`

**功能**:
- 全局搜索框
- 语义检索
- 结果分类展示（PRD/测试用例）
- 高亮显示匹配内容
- 筛选器

**布局**:
```
┌─────────────────────────────────────────────────────────┐
│ [搜索框: 如何测试用户登录功能]  [搜索]                   │
│ 类型: [全部▼] [PRD] [测试用例]                          │
├─────────────────────────────────────────────────────────┤
│ PRD 文档 (5 个结果)                                      │
│ ┌───────────────────────────────────────────────────┐  │
│ │ PRD_LOGIN_001 - 用户登录功能需求                   │  │
│ │ ...登录功能描述...高亮匹配内容...                  │  │
│ │ 相关度: 95%                                        │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ 测试用例 (12 个结果)                                     │
│ ┌───────────────────────────────────────────────────┐  │
│ │ TC_LOGIN_001 - 正常登录流程验证                    │  │
│ │ ...测试步骤...高亮匹配内容...                      │  │
│ │ 相关度: 92%                                        │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**组件**:
```tsx
<SearchPage>
  <SearchBar
    onSearch={handleSearch}
  />
  <FilterBar>
    <TypeFilter />
  </FilterBar>
  <SearchResults>
    <PRDResults>
      <PRDResultCard />
    </PRDResults>
    <TestCaseResults>
      <TestCaseResultCard />
    </TestCaseResults>
  </SearchResults>
</SearchPage>
```

## 通用组件

### 1. Layout 组件

```tsx
<AppLayout>
  <Header>
    <Logo />
    <Navigation />
    <UserMenu />
  </Header>
  <Sider>
    <ModuleTree />
  </Sider>
  <Content>
    {children}
  </Content>
</AppLayout>
```

### 2. ModuleTree 组件

功能：
- 树形展示功能模块
- 支持展开/折叠
- 点击筛选对应模块的内容
- 右键菜单（新建/编辑/删除）

### 3. MarkdownEditor 组件

功能：
- Monaco Editor 集成
- 实时预览
- 工具栏（加粗、斜体、插入图片等）
- 全屏模式

### 4. ImageUpload 组件

功能：
- 拖拽上传
- 多文件上传
- 图片预览
- 删除图片
- 进度显示

### 5. TagSelect 组件

功能：
- 下拉选择标签
- 支持创建新标签
- 多选
- 颜色显示

## 状态管理

### React Query

用于管理服务端状态（API 数据）：

```tsx
// 获取 PRD 列表
const { data, isLoading } = useQuery({
  queryKey: ['prds', filters],
  queryFn: () => api.getPRDs(filters)
});

// 创建 PRD
const mutation = useMutation({
  mutationFn: api.createPRD,
  onSuccess: () => {
    queryClient.invalidateQueries(['prds']);
  }
});
```

### Zustand

用于管理客户端状态：

```tsx
// 全局状态
const useAppStore = create((set) => ({
  selectedModule: null,
  setSelectedModule: (module) => set({ selectedModule: module }),
  
  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query })
}));
```

## 路由配置

```tsx
const routes = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: 'prds', element: <PRDList /> },
      { path: 'prds/create', element: <PRDCreate /> },
      { path: 'prds/:id', element: <PRDDetail /> },
      { path: 'prds/:id/edit', element: <PRDEdit /> },
      { path: 'testcases', element: <TestCaseList /> },
      { path: 'testcases/create', element: <TestCaseCreate /> },
      { path: 'testcases/:id', element: <TestCaseDetail /> },
      { path: 'testcases/:id/edit', element: <TestCaseEdit /> },
      { path: 'import', element: <Import /> },
      { path: 'search', element: <Search /> },
      { path: 'statistics', element: <Statistics /> }
    ]
  }
];
```

## 样式规范

### 颜色

- 主色: `#1890ff` (Ant Design 蓝)
- 成功: `#52c41a`
- 警告: `#faad14`
- 错误: `#f5222d`
- 文本: `#000000d9`
- 次要文本: `#00000073`
- 边框: `#d9d9d9`
- 背景: `#f0f2f5`

### 优先级颜色

- P0: `#f5222d` (红色)
- P1: `#fa8c16` (橙色)
- P2: `#1890ff` (蓝色)
- P3: `#52c41a` (绿色)

### 间距

使用 Tailwind 的间距系统：
- `p-4`: 16px
- `m-4`: 16px
- `gap-4`: 16px

## 响应式设计

- 桌面端优先（主要使用场景）
- 最小宽度: 1280px
- 侧边栏可折叠

## 性能优化

1. **代码分割**: 使用 React.lazy 和 Suspense
2. **虚拟滚动**: 长列表使用 react-window
3. **图片懒加载**: 使用 Intersection Observer
4. **缓存策略**: React Query 自动缓存
5. **防抖节流**: 搜索输入使用防抖

## 开发规范

### 文件命名

- 组件: PascalCase (e.g., `PRDList.tsx`)
- 工具函数: camelCase (e.g., `formatDate.ts`)
- 类型定义: PascalCase (e.g., `PRDTypes.ts`)

### 组件结构

```tsx
// 1. 导入
import React from 'react';
import { Button } from 'antd';

// 2. 类型定义
interface Props {
  title: string;
}

// 3. 组件
export const MyComponent: React.FC<Props> = ({ title }) => {
  // 4. Hooks
  const [state, setState] = useState();
  
  // 5. 事件处理
  const handleClick = () => {};
  
  // 6. 渲染
  return <div>{title}</div>;
};
```

### TypeScript 规范

- 所有组件必须有类型定义
- 避免使用 `any`
- 使用接口定义 Props
- API 响应使用类型定义

## 测试

- 单元测试: Vitest + React Testing Library
- E2E 测试: Playwright (可选)
- 测试覆盖率目标: 80%+
