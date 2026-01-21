// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1';

// 通用请求函数
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ code: number; message: string; data: T }> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || `HTTP error! status: ${response.status}`);
    }
    
    return result;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// ============================================
// 项目管理 API
// ============================================

export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export const projectAPI = {
  // 获取项目列表
  list: () => request<{ total: number; items: Project[] }>('/projects'),
  
  // 创建项目
  create: (data: { name: string; description: string }) =>
    request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取项目详情
  get: (id: string) => request<Project>(`/projects/${id}`),
  
  // 更新项目
  update: (id: string, data: { name: string; description: string }) =>
    request<Project>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除项目
  delete: (id: string) =>
    request<null>(`/projects/${id}`, {
      method: 'DELETE',
    }),
};

// ============================================
// 模块管理 API
// ============================================

export interface Module {
  id: string;
  project_id: string;
  name: string;
  description: string;
  parent_id: string | null;
  sort_order: number;
  children?: Module[];
  created_at: string;
  updated_at: string;
}

export const moduleAPI = {
  // 获取模块树
  getTree: (projectId: string) =>
    request<Module[]>(`/projects/${projectId}/modules/tree`),
  
  // 创建模块
  create: (projectId: string, data: {
    name: string;
    description: string;
    parent_id?: string;
  }) =>
    request<Module>(`/projects/${projectId}/modules`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 更新模块
  update: (projectId: string, moduleId: string, data: {
    name: string;
    description: string;
  }) =>
    request<Module>(`/projects/${projectId}/modules/${moduleId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除模块
  delete: (projectId: string, moduleId: string) =>
    request<null>(`/projects/${projectId}/modules/${moduleId}`, {
      method: 'DELETE',
    }),
  
  // 模块排序
  sort: (projectId: string, data: { module_id: string; sort_order: number }[]) =>
    request<null>(`/projects/${projectId}/modules/sort`, {
      method: 'PUT',
      body: JSON.stringify({ modules: data }),
    }),
};

// ============================================
// 标签管理 API
// ============================================

export interface Tag {
  id: string;
  project_id: string;
  name: string;
  color: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export const tagAPI = {
  // 获取标签列表
  list: (projectId: string) =>
    request<Tag[]>(`/projects/${projectId}/tags`),
  
  // 创建标签
  create: (projectId: string, data: {
    name: string;
    color: string;
    description: string;
  }) =>
    request<Tag>(`/projects/${projectId}/tags`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 更新标签
  update: (projectId: string, tagId: string, data: {
    name: string;
    color: string;
    description: string;
  }) =>
    request<Tag>(`/projects/${projectId}/tags/${tagId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除标签
  delete: (projectId: string, tagId: string) =>
    request<null>(`/projects/${projectId}/tags/${tagId}`, {
      method: 'DELETE',
    }),
  
  // 获取标签使用统计
  getUsage: (projectId: string, tagId: string) =>
    request<{ prd_count: number; testcase_count: number }>(
      `/projects/${projectId}/tags/${tagId}/usage`
    ),
};

// ============================================
// App 版本管理 API
// ============================================

export interface AppVersion {
  id: string;
  project_id: string;
  version: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export const appVersionAPI = {
  // 获取 App 版本列表
  list: (projectId: string) =>
    request<AppVersion[]>(`/projects/${projectId}/app-versions`),
  
  // 创建 App 版本
  create: (projectId: string, data: {
    version: string;
    description: string;
  }) =>
    request<AppVersion>(`/projects/${projectId}/app-versions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取 App 版本详情
  get: (projectId: string, versionId: string) =>
    request<AppVersion>(`/projects/${projectId}/app-versions/${versionId}`),
  
  // 删除 App 版本
  delete: (projectId: string, versionId: string) =>
    request<null>(`/projects/${projectId}/app-versions/${versionId}`, {
      method: 'DELETE',
    }),
};

// ============================================
// PRD 文档管理 API
// ============================================

export interface PRD {
  id: string;
  project_id: string;
  code: string;
  title: string;
  version: string;
  app_version_id: string;
  module_id: string;
  content: string;
  status: string;
  author: string;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export interface PRDListParams {
  page?: number;
  page_size?: number;
  module_id?: string;
  app_version_id?: string;
  status?: string;
  tag_id?: string;
  keyword?: string;
}

export const prdAPI = {
  // 获取 PRD 列表
  list: (projectId: string, params?: PRDListParams) => {
    const query = new URLSearchParams(params as any).toString();
    return request<{
      total: number;
      page: number;
      page_size: number;
      items: PRD[];
    }>(`/projects/${projectId}/prds${query ? `?${query}` : ''}`);
  },
  
  // 创建 PRD
  create: (projectId: string, data: {
    code: string;
    title: string;
    version: string;
    app_version_id: string;
    module_id: string;
    content: string;
    author: string;
  }) =>
    request<PRD>(`/projects/${projectId}/prds`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取 PRD 详情
  get: (projectId: string, prdId: string) =>
    request<PRD>(`/projects/${projectId}/prds/${prdId}`),
  
  // 更新 PRD
  update: (projectId: string, prdId: string, data: {
    title: string;
    version: string;
    app_version_id: string;
    module_id: string;
    content: string;
    create_version?: boolean;
  }) =>
    request<PRD>(`/projects/${projectId}/prds/${prdId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除 PRD
  delete: (projectId: string, prdId: string) =>
    request<null>(`/projects/${projectId}/prds/${prdId}`, {
      method: 'DELETE',
    }),
  
  // 更新 PRD 状态
  updateStatus: (projectId: string, prdId: string, status: string) =>
    request<PRD>(`/projects/${projectId}/prds/${prdId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    }),
  
  // 发布 PRD
  publish: (projectId: string, prdId: string) =>
    request<PRD>(`/projects/${projectId}/prds/${prdId}/publish`, {
      method: 'POST',
    }),
  
  // 归档 PRD
  archive: (projectId: string, prdId: string) =>
    request<PRD>(`/projects/${projectId}/prds/${prdId}/archive`, {
      method: 'POST',
    }),
  
  // 添加标签
  addTag: (projectId: string, prdId: string, tagId: string) =>
    request<null>(`/projects/${projectId}/prds/${prdId}/tags`, {
      method: 'POST',
      body: JSON.stringify({ tag_id: tagId }),
    }),
  
  // 删除标签
  removeTag: (projectId: string, prdId: string, tagId: string) =>
    request<null>(`/projects/${projectId}/prds/${prdId}/tags/${tagId}`, {
      method: 'DELETE',
    }),
  
  // 获取版本列表
  getVersions: (projectId: string, prdId: string) =>
    request<any[]>(`/projects/${projectId}/prds/${prdId}/versions`),
  
  // 获取特定版本
  getVersion: (projectId: string, prdId: string, version: string) =>
    request<any>(`/projects/${projectId}/prds/${prdId}/versions/${version}`),
  
  // 版本对比
  compareVersions: (projectId: string, prdId: string, v1: string, v2: string) =>
    request<any>(
      `/projects/${projectId}/prds/${prdId}/versions/compare?v1=${v1}&v2=${v2}`
    ),
};

// ============================================
// 测试用例管理 API
// ============================================

export interface TestStep {
  step_number: number;
  operation: string;
  test_data: string;
  expected_result: string;
}

export interface TestCase {
  id: string;
  project_id: string;
  code: string;
  title: string;
  prd_id: string;
  module_id: string;
  app_version_id: string;
  precondition: string;
  expected_result: string;
  priority: string;
  type: string;
  status: string;
  steps: TestStep[];
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export interface TestCaseListParams {
  page?: number;
  page_size?: number;
  prd_id?: string;
  module_id?: string;
  app_version_id?: string;
  priority?: string;
  type?: string;
  status?: string;
  tag_id?: string;
  keyword?: string;
}

export const testcaseAPI = {
  // 获取测试用例列表
  list: (projectId: string, params?: TestCaseListParams) => {
    const query = new URLSearchParams(params as any).toString();
    return request<{
      total: number;
      page: number;
      page_size: number;
      items: TestCase[];
    }>(`/projects/${projectId}/testcases${query ? `?${query}` : ''}`);
  },
  
  // 创建测试用例
  create: (projectId: string, data: {
    code: string;
    title: string;
    prd_id: string;
    module_id: string;
    app_version_id: string;
    precondition: string;
    expected_result: string;
    priority: string;
    type: string;
    steps: TestStep[];
  }) =>
    request<TestCase>(`/projects/${projectId}/testcases`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // 获取测试用例详情
  get: (projectId: string, testcaseId: string) =>
    request<TestCase>(`/projects/${projectId}/testcases/${testcaseId}`),
  
  // 更新测试用例
  update: (projectId: string, testcaseId: string, data: {
    title: string;
    prd_id: string;
    module_id: string;
    app_version_id: string;
    precondition: string;
    expected_result: string;
    priority: string;
    type: string;
    status: string;
    steps: TestStep[];
    create_version?: boolean;
  }) =>
    request<TestCase>(`/projects/${projectId}/testcases/${testcaseId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  // 删除测试用例
  delete: (projectId: string, testcaseId: string) =>
    request<null>(`/projects/${projectId}/testcases/${testcaseId}`, {
      method: 'DELETE',
    }),
  
  // 批量删除
  batchDelete: (projectId: string, ids: string[]) =>
    request<null>(`/projects/${projectId}/testcases/batch-delete`, {
      method: 'POST',
      body: JSON.stringify({ ids }),
    }),
  
  // 添加标签
  addTag: (projectId: string, testcaseId: string, tagId: string) =>
    request<null>(`/projects/${projectId}/testcases/${testcaseId}/tags`, {
      method: 'POST',
      body: JSON.stringify({ tag_id: tagId }),
    }),
  
  // 删除标签
  removeTag: (projectId: string, testcaseId: string, tagId: string) =>
    request<null>(
      `/projects/${projectId}/testcases/${testcaseId}/tags/${tagId}`,
      { method: 'DELETE' }
    ),
  
  // 获取版本列表
  getVersions: (projectId: string, testcaseId: string) =>
    request<any[]>(`/projects/${projectId}/testcases/${testcaseId}/versions`),
  
  // 获取特定版本
  getVersion: (projectId: string, testcaseId: string, version: string) =>
    request<any>(
      `/projects/${projectId}/testcases/${testcaseId}/versions/${version}`
    ),
};

// ============================================
// 统计功能 API
// ============================================

export const statisticsAPI = {
  // 获取项目统计
  getProjectStats: (projectId: string) =>
    request<any>(`/projects/${projectId}/statistics`),
  
  // 获取趋势数据
  getTrends: (projectId: string, params?: { days?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return request<any>(
      `/projects/${projectId}/statistics/trends${query ? `?${query}` : ''}`
    );
  },
  
  // 获取覆盖率
  getCoverage: (projectId: string) =>
    request<any>(`/projects/${projectId}/statistics/coverage`),
};

// ============================================
// 语义检索 API
// ============================================

export interface SearchRequest {
  query: string;
  type: 'prd' | 'testcase' | 'all';
  limit?: number;
  score_threshold?: number;
  alpha?: number;
  module_id?: string;
  app_version_id?: string;
  status?: string;
}

export interface SearchResult {
  type: 'prd' | 'testcase';
  id: string;
  title: string;
  content: string;
  score: number;
  metadata: any;
  highlights: string[];
}

export const searchAPI = {
  // 语义搜索
  search: (projectId: string, data: SearchRequest) =>
    request<{
      results: SearchResult[];
      total: number;
      query: string;
      type: string;
    }>(`/projects/${projectId}/search`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  // PRD 推荐
  getPRDRecommendations: (projectId: string, prdId: string, limit?: number) => {
    const query = limit ? `?limit=${limit}` : '';
    return request<{
      results: SearchResult[];
      total: number;
    }>(`/projects/${projectId}/prds/${prdId}/recommendations${query}`);
  },
  
  // 测试用例推荐
  getTestCaseRecommendations: (
    projectId: string,
    testcaseId: string,
    limit?: number
  ) => {
    const query = limit ? `?limit=${limit}` : '';
    return request<{
      results: SearchResult[];
      total: number;
    }>(
      `/projects/${projectId}/testcases/${testcaseId}/recommendations${query}`
    );
  },
};

// ============================================
// 设置管理 API
// ============================================

export interface Setting {
  id: string;
  key: string;
  value: string;
  type: string;
  description: string;
}

export const settingsAPI = {
  // 获取所有设置
  getAll: () => request<Setting[]>('/settings'),
  
  // 按类别获取设置
  getByCategory: (category: string) =>
    request<Setting[]>(`/settings/${category}`),
  
  // 更新单个设置
  update: (key: string, value: string) =>
    request<{ message: string }>(`/settings/${key}`, {
      method: 'PUT',
      body: JSON.stringify({ value }),
    }),
  
  // 批量更新设置
  batchUpdate: (updates: Record<string, string>) =>
    request<{ message: string }>('/settings/batch', {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
};

// 导出所有 API
export default {
  project: projectAPI,
  module: moduleAPI,
  tag: tagAPI,
  appVersion: appVersionAPI,
  prd: prdAPI,
  testcase: testcaseAPI,
  statistics: statisticsAPI,
  search: searchAPI,
  settings: settingsAPI,
};
