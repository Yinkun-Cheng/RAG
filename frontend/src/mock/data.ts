// Mock 数据

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  prdCount: number;
  testCaseCount: number;
}

export interface Module {
  id: string;
  name: string;
  parentId: string | null;
  children?: Module[];
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  usageCount: number;
}

export interface AppVersion {
  id: string;
  projectId: string;
  version: string;
  description: string;
  createdAt: string;
  prdCount: number;
}

export interface PRD {
  id: string;
  projectId: string;
  projectName: string;
  title: string;
  appVersionId: string;
  appVersion: string;
  moduleId: string;
  moduleName: string;
  status: 'draft' | 'published' | 'archived';
  syncStatus?: 'syncing' | 'synced' | 'failed';
  lastSyncTime?: string;
  version: number;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  content: string;
}

export interface TestCase {
  id: string;
  projectId: string;
  projectName: string;
  appVersionId: string;
  appVersion: string;
  title: string;
  moduleId: string;
  moduleName: string;
  priority: 'high' | 'medium' | 'low';
  type: 'functional' | 'performance' | 'security' | 'ui';
  status: 'active' | 'deprecated';
  tags: string[];
  precondition: string;
  expectedResult: string;
  steps: TestStep[];
  createdAt: string;
  updatedAt: string;
}

export interface TestStep {
  id: string;
  order: number;
  description: string;
  screenshots: string[];
}

// Mock 项目数据
export const mockProjects: Project[] = [
  {
    id: 'proj-1',
    name: '电商平台',
    description: '电商平台核心功能开发',
    createdAt: '2025-01-01',
    prdCount: 6,
    testCaseCount: 3,
  },
];

// Mock App 版本数据
export const mockAppVersions: AppVersion[] = [
  {
    id: 'v1',
    projectId: 'proj-1',
    version: 'v1.0.0',
    description: '初始版本 - 基础功能',
    createdAt: '2025-01-01',
    prdCount: 3,
  },
  {
    id: 'v2',
    projectId: 'proj-1',
    version: 'v1.1.0',
    description: '功能优化版本',
    createdAt: '2025-01-10',
    prdCount: 2,
  },
  {
    id: 'v3',
    projectId: 'proj-1',
    version: 'v2.0.0',
    description: '架构升级版本',
    createdAt: '2025-01-15',
    prdCount: 1,
  },
];

// Mock 模块数据（树形结构）
export const mockModules: Module[] = [
  {
    id: '1',
    name: '用户管理',
    parentId: null,
    children: [
      { id: '1-1', name: '用户注册', parentId: '1' },
      { id: '1-2', name: '用户登录', parentId: '1' },
      { id: '1-3', name: '个人资料', parentId: '1' },
    ],
  },
  {
    id: '2',
    name: '订单管理',
    parentId: null,
    children: [
      { id: '2-1', name: '创建订单', parentId: '2' },
      { id: '2-2', name: '订单支付', parentId: '2' },
      { id: '2-3', name: '订单查询', parentId: '2' },
    ],
  },
  {
    id: '3',
    name: '商品管理',
    parentId: null,
    children: [
      { id: '3-1', name: '商品列表', parentId: '3' },
      { id: '3-2', name: '商品详情', parentId: '3' },
      { id: '3-3', name: '商品搜索', parentId: '3' },
    ],
  },
];

// Mock 标签数据
export const mockTags: Tag[] = [
  { id: '1', name: '核心功能', color: 'red', usageCount: 25 },
  { id: '2', name: '高优先级', color: 'orange', usageCount: 18 },
  { id: '3', name: '需求变更', color: 'blue', usageCount: 12 },
  { id: '4', name: 'Bug修复', color: 'green', usageCount: 8 },
  { id: '5', name: '性能优化', color: 'purple', usageCount: 6 },
  { id: '6', name: '安全相关', color: 'volcano', usageCount: 4 },
];

// Mock PRD 数据
export const mockPRDs: PRD[] = [
  {
    id: '1',
    projectId: 'proj-1',
    projectName: '电商平台',
    title: '用户注册功能需求文档',
    appVersionId: 'v1',
    appVersion: 'v1.0.0',
    moduleId: '1-1',
    moduleName: '用户注册',
    status: 'published',
    syncStatus: 'synced',
    lastSyncTime: '2025-01-15 14:30:00',
    version: 2,
    tags: ['核心功能', '高优先级'],
    createdAt: '2025-01-10',
    updatedAt: '2025-01-15',
    content: `# 用户注册功能需求

## 1. 功能概述
实现用户通过手机号或邮箱注册账号的功能。

## 2. 功能需求
- 支持手机号注册
- 支持邮箱注册
- 验证码验证
- 密码强度校验

## 3. 非功能需求
- 注册响应时间 < 2s
- 支持并发 1000 用户同时注册`,
  },
  {
    id: '2',
    projectId: 'proj-1',
    projectName: '电商平台',
    title: '用户登录功能需求文档',
    appVersionId: 'v1',
    appVersion: 'v1.0.0',
    moduleId: '1-2',
    moduleName: '用户登录',
    status: 'published',
    syncStatus: 'synced',
    lastSyncTime: '2025-01-12 10:20:00',
    version: 1,
    tags: ['核心功能'],
    createdAt: '2025-01-11',
    updatedAt: '2025-01-12',
    content: `# 用户登录功能需求

## 1. 功能概述
实现用户通过账号密码登录系统。

## 2. 功能需求
- 支持手机号/邮箱登录
- 记住登录状态
- 忘记密码功能`,
  },
  {
    id: '3',
    projectId: 'proj-1',
    projectName: '电商平台',
    title: '个人资料管理需求文档',
    appVersionId: 'v1',
    appVersion: 'v1.0.0',
    moduleId: '1-3',
    moduleName: '个人资料',
    status: 'draft',
    version: 1,
    tags: ['核心功能'],
    createdAt: '2025-01-13',
    updatedAt: '2025-01-13',
    content: `# 个人资料管理需求

## 1. 功能描述
用户可以查看和编辑个人资料。`,
  },
  {
    id: '4',
    projectId: 'proj-1',
    projectName: '电商平台',
    title: '订单支付流程优化',
    appVersionId: 'v2',
    appVersion: 'v1.1.0',
    moduleId: '2-2',
    moduleName: '订单支付',
    status: 'published',
    syncStatus: 'synced',
    lastSyncTime: '2025-01-12 16:45:00',
    version: 1,
    tags: ['核心功能', '性能优化'],
    createdAt: '2025-01-12',
    updatedAt: '2025-01-12',
    content: `# 订单支付流程优化

## 1. 背景
当前支付流程存在性能瓶颈，需要优化。

## 2. 优化方案
- 异步处理支付回调
- 增加支付状态缓存
- 优化数据库查询`,
  },
  {
    id: '5',
    projectId: 'proj-1',
    projectName: '电商平台',
    title: '商品搜索功能',
    appVersionId: 'v2',
    appVersion: 'v1.1.0',
    moduleId: '3-3',
    moduleName: '商品搜索',
    status: 'archived',
    version: 1,
    tags: ['核心功能'],
    createdAt: '2025-01-14',
    updatedAt: '2025-01-16',
    content: `# 商品搜索功能

## 1. 功能描述
实现商品的全文搜索和筛选功能。`,
  },
  {
    id: '6',
    projectId: 'proj-1',
    projectName: '电商平台',
    title: '新架构设计文档',
    appVersionId: 'v3',
    appVersion: 'v2.0.0',
    moduleId: '1',
    moduleName: '用户管理',
    status: 'draft',
    version: 1,
    tags: ['需求变更'],
    createdAt: '2025-01-18',
    updatedAt: '2025-01-18',
    content: `# 新架构设计文档

## 1. 架构升级
微服务架构改造方案。`,
  },
];

// Mock 测试用例数据
export const mockTestCases: TestCase[] = [
  {
    id: '1',
    projectId: 'proj-1',
    projectName: '电商平台',
    appVersionId: 'v1',
    appVersion: 'v1.0.0',
    title: '用户注册-手机号注册成功',
    moduleId: '1-1',
    moduleName: '用户注册',
    priority: 'high',
    type: 'functional',
    status: 'active',
    tags: ['核心功能', '高优先级'],
    precondition: '用户未注册，手机号有效',
    expectedResult: '注册成功，跳转到首页',
    steps: [
      {
        id: 's1',
        order: 1,
        description: '打开注册页面',
        screenshots: [],
      },
      {
        id: 's2',
        order: 2,
        description: '输入手机号：13800138000',
        screenshots: [],
      },
      {
        id: 's3',
        order: 3,
        description: '点击获取验证码',
        screenshots: [],
      },
      {
        id: 's4',
        order: 4,
        description: '输入验证码：123456',
        screenshots: [],
      },
      {
        id: 's5',
        order: 5,
        description: '输入密码：Test@123',
        screenshots: [],
      },
      {
        id: 's6',
        order: 6,
        description: '点击注册按钮',
        screenshots: [],
      },
    ],
    createdAt: '2025-01-10',
    updatedAt: '2025-01-15',
  },
  {
    id: '2',
    projectId: 'proj-1',
    projectName: '电商平台',
    appVersionId: 'v1',
    appVersion: 'v1.0.0',
    title: '用户登录-密码错误',
    moduleId: '1-2',
    moduleName: '用户登录',
    priority: 'high',
    type: 'functional',
    status: 'active',
    tags: ['核心功能'],
    precondition: '用户已注册',
    expectedResult: '提示密码错误',
    steps: [
      {
        id: 's1',
        order: 1,
        description: '打开登录页面',
        screenshots: [],
      },
      {
        id: 's2',
        order: 2,
        description: '输入用户名：test@example.com',
        screenshots: [],
      },
      {
        id: 's3',
        order: 3,
        description: '输入错误密码：wrong123',
        screenshots: [],
      },
      {
        id: 's4',
        order: 4,
        description: '点击登录按钮',
        screenshots: [],
      },
    ],
    createdAt: '2025-01-11',
    updatedAt: '2025-01-11',
  },
  {
    id: '3',
    projectId: 'proj-1',
    projectName: '电商平台',
    appVersionId: 'v2',
    appVersion: 'v1.1.0',
    title: '订单创建-正常流程',
    moduleId: '2-1',
    moduleName: '创建订单',
    priority: 'high',
    type: 'functional',
    status: 'active',
    tags: ['核心功能', '高优先级'],
    precondition: '用户已登录，购物车有商品',
    expectedResult: '订单创建成功',
    steps: [
      {
        id: 's1',
        order: 1,
        description: '进入购物车页面',
        screenshots: [],
      },
      {
        id: 's2',
        order: 2,
        description: '选择商品',
        screenshots: [],
      },
      {
        id: 's3',
        order: 3,
        description: '点击结算',
        screenshots: [],
      },
      {
        id: 's4',
        order: 4,
        description: '填写收货地址',
        screenshots: [],
      },
      {
        id: 's5',
        order: 5,
        description: '提交订单',
        screenshots: [],
      },
    ],
    createdAt: '2025-01-12',
    updatedAt: '2025-01-14',
  },
];
