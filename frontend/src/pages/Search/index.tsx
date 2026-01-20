import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Input,
  Card,
  Select,
  Button,
  List,
  Tag,
  Badge,
  Empty,
  Spin,
  Space,
  Collapse,
  Divider,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  CheckSquareOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { mockModules, mockAppVersions } from '../../mock/data';

const { Panel } = Collapse;

interface SearchResult {
  id: string;
  type: 'prd' | 'testcase';
  title: string;
  content: string;
  score: number;
  metadata: {
    project_id: string;
    project_name: string;
    app_version: string;
    module: string;
    status: string;
    priority?: string;
    test_type?: string;
    tags: string[];
    created_at: string;
  };
  highlights: string[];
}

export default function Search() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [type, setType] = useState<'all' | 'prd' | 'testcase'>('all');
  const [appVersion, setAppVersion] = useState<string>('');
  const [moduleId, setModuleId] = useState<string>('');
  const [priority, setPriority] = useState<string>('');
  const [status, setStatus] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  const projectVersions = mockAppVersions.filter(v => v.projectId === projectId);

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const modules: { id: string; name: string }[] = [{ id: '', name: '全部模块' }];
    const flatten = (items: typeof mockModules) => {
      items.forEach(item => {
        modules.push({ id: item.id, name: item.name });
        if (item.children) {
          flatten(item.children);
        }
      });
    };
    flatten(mockModules);
    return modules;
  };

  const allModules = getAllModules();

  // Mock 搜索结果
  const mockSearchResults: SearchResult[] = [
    {
      id: 'prd-2',
      type: 'prd',
      title: '用户登录功能需求文档',
      content: `# 用户登录功能需求

## 1. 功能概述
实现用户通过账号密码登录系统。

## 2. 功能需求
- 支持手机号/邮箱登录
- 记住登录状态
- 忘记密码功能`,
      score: 0.95,
      metadata: {
        project_id: 'proj-1',
        project_name: '电商平台',
        app_version: 'v1.0.0',
        module: '用户管理/用户登录',
        status: 'published',
        tags: ['核心功能'],
        created_at: '2025-01-11',
      },
      highlights: ['用户登录', '账号密码', '登录系统'],
    },
    {
      id: 'tc-2',
      type: 'testcase',
      title: '用户登录-密码错误',
      content: `前置条件：用户已注册
测试步骤：
1. 打开登录页面
2. 输入用户名：test@example.com
3. 输入错误密码：wrong123
4. 点击登录按钮
预期结果：提示密码错误`,
      score: 0.92,
      metadata: {
        project_id: 'proj-1',
        project_name: '电商平台',
        app_version: 'v1.0.0',
        module: '用户管理/用户登录',
        status: 'active',
        priority: 'high',
        test_type: 'functional',
        tags: ['核心功能'],
        created_at: '2025-01-11',
      },
      highlights: ['用户登录', '密码错误', '登录页面'],
    },
    {
      id: 'prd-1',
      type: 'prd',
      title: '用户注册功能需求文档',
      content: `# 用户注册功能需求

## 1. 功能概述
实现用户通过手机号或邮箱注册账号的功能。

## 2. 功能需求
- 支持手机号注册
- 支持邮箱注册
- 验证码验证
- 密码强度校验`,
      score: 0.88,
      metadata: {
        project_id: 'proj-1',
        project_name: '电商平台',
        app_version: 'v1.0.0',
        module: '用户管理/用户注册',
        status: 'published',
        tags: ['核心功能', '高优先级'],
        created_at: '2025-01-10',
      },
      highlights: ['用户注册', '手机号', '邮箱注册'],
    },
  ];

  const handleSearch = async () => {
    if (!query.trim()) {
      return;
    }

    setLoading(true);

    // 模拟 API 调用
    setTimeout(() => {
      setResults(mockSearchResults);
      setLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleReset = () => {
    setQuery('');
    setType('all');
    setAppVersion('');
    setModuleId('');
    setPriority('');
    setStatus('');
    setResults([]);
  };

  const getTypeIcon = (type: string) => {
    return type === 'prd' ? <FileTextOutlined /> : <CheckSquareOutlined />;
  };

  const getTypeText = (type: string) => {
    return type === 'prd' ? 'PRD 文档' : '测试用例';
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'green';
    if (score >= 0.7) return 'blue';
    return 'orange';
  };

  const highlightText = (text: string, highlights: string[]) => {
    let result = text;
    highlights.forEach(keyword => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      result = result.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
    });
    return result;
  };

  // 按类型分组结果
  const groupedResults = {
    prd: results.filter(r => r.type === 'prd'),
    testcase: results.filter(r => r.type === 'testcase'),
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <SearchOutlined />
          语义搜索
        </h1>
        <p className="text-gray-500 mt-1">
          使用自然语言搜索 PRD 文档和测试用例，基于 RAG 向量检索技术
        </p>
      </div>

      {/* 搜索区域 */}
      <Card className="mb-6">
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          {/* 搜索框 */}
          <Input.Search
            size="large"
            placeholder="输入搜索内容，例如：用户登录功能的测试用例"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onSearch={handleSearch}
            onKeyPress={handleKeyPress}
            enterButton={
              <Button type="primary" icon={<SearchOutlined />}>
                搜索
              </Button>
            }
            loading={loading}
          />

          {/* 快捷筛选 */}
          <div className="flex items-center gap-4">
            <span className="text-gray-600">类型：</span>
            <Select
              value={type}
              onChange={setType}
              style={{ width: 150 }}
              options={[
                { label: '全部', value: 'all' },
                { label: 'PRD 文档', value: 'prd' },
                { label: '测试用例', value: 'testcase' },
              ]}
            />

            <Button
              icon={<FilterOutlined />}
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? '隐藏' : '显示'}高级筛选
            </Button>

            {(appVersion || moduleId || priority || status) && (
              <Button onClick={handleReset}>清空筛选</Button>
            )}
          </div>

          {/* 高级筛选 */}
          {showFilters && (
            <div className="bg-gray-50 p-4 rounded">
              <div className="grid grid-cols-4 gap-4">
                <div>
                  <div className="mb-2 text-sm text-gray-600">App 版本：</div>
                  <Select
                    placeholder="全部版本"
                    value={appVersion}
                    onChange={setAppVersion}
                    style={{ width: '100%' }}
                    options={[
                      { label: '全部版本', value: '' },
                      ...projectVersions.map(v => ({
                        label: v.version,
                        value: v.id,
                      })),
                    ]}
                  />
                </div>

                <div>
                  <div className="mb-2 text-sm text-gray-600">模块：</div>
                  <Select
                    placeholder="全部模块"
                    value={moduleId}
                    onChange={setModuleId}
                    style={{ width: '100%' }}
                    options={allModules.map(m => ({ label: m.name, value: m.id }))}
                  />
                </div>

                <div>
                  <div className="mb-2 text-sm text-gray-600">优先级：</div>
                  <Select
                    placeholder="全部优先级"
                    value={priority}
                    onChange={setPriority}
                    style={{ width: '100%' }}
                    options={[
                      { label: '全部优先级', value: '' },
                      { label: '高', value: 'high' },
                      { label: '中', value: 'medium' },
                      { label: '低', value: 'low' },
                    ]}
                  />
                </div>

                <div>
                  <div className="mb-2 text-sm text-gray-600">状态：</div>
                  <Select
                    placeholder="全部状态"
                    value={status}
                    onChange={setStatus}
                    style={{ width: '100%' }}
                    options={[
                      { label: '全部状态', value: '' },
                      { label: '有效', value: 'active' },
                      { label: '已发布', value: 'published' },
                      { label: '草稿', value: 'draft' },
                      { label: '已归档', value: 'archived' },
                    ]}
                  />
                </div>
              </div>
            </div>
          )}
        </Space>
      </Card>

      {/* 搜索结果 */}
      {loading ? (
        <Card>
          <div className="text-center py-12">
            <Spin size="large" />
            <p className="mt-4 text-gray-500">正在搜索中...</p>
          </div>
        </Card>
      ) : results.length > 0 ? (
        <div className="space-y-6">
          {/* 结果统计 */}
          <div className="text-gray-600">
            找到 <span className="font-bold text-blue-600">{results.length}</span> 条相关结果
            {groupedResults.prd.length > 0 && (
              <span className="ml-4">
                PRD 文档 <span className="font-bold">{groupedResults.prd.length}</span> 条
              </span>
            )}
            {groupedResults.testcase.length > 0 && (
              <span className="ml-4">
                测试用例 <span className="font-bold">{groupedResults.testcase.length}</span> 条
              </span>
            )}
          </div>

          {/* 分类展示结果 */}
          <Collapse defaultActiveKey={['prd', 'testcase']}>
            {groupedResults.prd.length > 0 && (
              <Panel
                key="prd"
                header={
                  <span className="font-medium">
                    <FileTextOutlined /> PRD 文档 ({groupedResults.prd.length})
                  </span>
                }
              >
                <List
                  dataSource={groupedResults.prd}
                  renderItem={item => (
                    <List.Item
                      className="cursor-pointer hover:bg-gray-50 p-4 rounded"
                      onClick={() => navigate(`/project/${projectId}/prd/${item.id}`)}
                    >
                      <div className="w-full">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {getTypeIcon(item.type)}
                              <span className="font-medium text-lg">{item.title}</span>
                              <Tag color={getScoreColor(item.score)}>
                                相似度: {(item.score * 100).toFixed(0)}%
                              </Tag>
                            </div>
                            <div className="text-sm text-gray-500 space-x-2">
                              <span>{item.metadata.app_version}</span>
                              <span>•</span>
                              <span>{item.metadata.module}</span>
                              <span>•</span>
                              <span>{item.metadata.created_at}</span>
                            </div>
                          </div>
                          <Badge
                            status={item.metadata.status === 'published' ? 'success' : 'default'}
                            text={
                              item.metadata.status === 'published' ? '已发布' : '草稿'
                            }
                          />
                        </div>

                        <div
                          className="text-gray-700 text-sm line-clamp-3 mb-2"
                          dangerouslySetInnerHTML={{
                            __html: highlightText(item.content, item.highlights),
                          }}
                        />

                        <div className="flex gap-1">
                          {item.metadata.tags.map(tag => (
                            <Tag key={tag} color="blue">
                              {tag}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              </Panel>
            )}

            {groupedResults.testcase.length > 0 && (
              <Panel
                key="testcase"
                header={
                  <span className="font-medium">
                    <CheckSquareOutlined /> 测试用例 ({groupedResults.testcase.length})
                  </span>
                }
              >
                <List
                  dataSource={groupedResults.testcase}
                  renderItem={item => (
                    <List.Item
                      className="cursor-pointer hover:bg-gray-50 p-4 rounded"
                      onClick={() => navigate(`/project/${projectId}/testcase/${item.id}`)}
                    >
                      <div className="w-full">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {getTypeIcon(item.type)}
                              <span className="font-medium text-lg">{item.title}</span>
                              <Tag color={getScoreColor(item.score)}>
                                相似度: {(item.score * 100).toFixed(0)}%
                              </Tag>
                            </div>
                            <div className="text-sm text-gray-500 space-x-2">
                              <span>{item.metadata.app_version}</span>
                              <span>•</span>
                              <span>{item.metadata.module}</span>
                              {item.metadata.priority && (
                                <>
                                  <span>•</span>
                                  <Tag
                                    color={
                                      item.metadata.priority === 'high'
                                        ? 'red'
                                        : item.metadata.priority === 'medium'
                                        ? 'orange'
                                        : 'blue'
                                    }
                                  >
                                    {item.metadata.priority === 'high'
                                      ? '高'
                                      : item.metadata.priority === 'medium'
                                      ? '中'
                                      : '低'}
                                  </Tag>
                                </>
                              )}
                            </div>
                          </div>
                          <Badge
                            status={item.metadata.status === 'active' ? 'success' : 'default'}
                            text={item.metadata.status === 'active' ? '有效' : '已废弃'}
                          />
                        </div>

                        <div
                          className="text-gray-700 text-sm line-clamp-3 mb-2"
                          dangerouslySetInnerHTML={{
                            __html: highlightText(item.content, item.highlights),
                          }}
                        />

                        <div className="flex gap-1">
                          {item.metadata.tags.map(tag => (
                            <Tag key={tag} color="blue">
                              {tag}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              </Panel>
            )}
          </Collapse>
        </div>
      ) : query ? (
        <Card>
          <Empty description="未找到相关结果，请尝试其他关键词" />
        </Card>
      ) : null}
    </div>
  );
}
