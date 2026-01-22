import { useState, useEffect } from 'react';
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
  InputNumber,
  message,
} from 'antd';
import {
  SearchOutlined,
  FileTextOutlined,
  CheckSquareOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import api from '../../api';

const { Panel } = Collapse;

interface SearchResult {
  id: string;
  type: 'prd' | 'testcase';
  title: string;
  content: string;
  score: number;
  metadata: any;
  highlights: string[];
}

interface Module {
  id: string;
  name: string;
  children?: Module[];
}

interface AppVersion {
  id: string;
  version: string;
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
  const [alpha, setAlpha] = useState<number>(1.0); // 混合检索权重，默认纯向量
  const [scoreThreshold, setScoreThreshold] = useState<number>(0.7); // 相似度阈值
  
  // 数据加载状态
  const [modules, setModules] = useState<Module[]>([]);
  const [appVersions, setAppVersions] = useState<AppVersion[]>([]);

  // 加载模块和版本数据
  useEffect(() => {
    if (!projectId) return;

    const loadData = async () => {
      try {
        // 加载模块树
        const moduleRes = await api.module.getTree(projectId);
        setModules(moduleRes.data);

        // 加载 App 版本
        const versionRes = await api.appVersion.list(projectId);
        setAppVersions(versionRes.data);
      } catch (error) {
        console.error('Failed to load data:', error);
        message.error('加载数据失败');
      }
    };

    loadData();
  }, [projectId]);

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const result: { id: string; name: string }[] = [{ id: '', name: '全部模块' }];
    const flatten = (items: Module[], prefix = '') => {
      items.forEach(item => {
        const displayName = prefix ? `${prefix} / ${item.name}` : item.name;
        result.push({ id: item.id, name: displayName });
        if (item.children && item.children.length > 0) {
          flatten(item.children, displayName);
        }
      });
    };
    flatten(modules);
    return result;
  };

  const allModules = getAllModules();

  const handleSearch = async () => {
    if (!query.trim()) {
      message.warning('请输入搜索内容');
      return;
    }

    if (!projectId) {
      message.error('项目ID不存在');
      return;
    }

    setLoading(true);

    try {
      const searchData: any = {
        query: query.trim(),
        type,
        limit: 20,
        score_threshold: scoreThreshold,
        alpha,
      };

      // 添加筛选条件
      if (moduleId) {
        searchData.module_id = moduleId;
      }
      if (appVersion) {
        searchData.app_version_id = appVersion;
      }
      if (status) {
        searchData.status = status;
      }

      const response = await api.search.search(projectId, searchData);
      const results = response.data.results || [];
      setResults(results);
      
      if (results.length === 0) {
        message.info('未找到相关结果');
      }
    } catch (error: any) {
      console.error('Search failed:', error);
      message.error(error.message || '搜索失败');
      setResults([]);
    } finally {
      setLoading(false);
    }
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
    setAlpha(1.0);
    setScoreThreshold(0.7);
    setResults([]);
  };

  const getTypeIcon = (type: string) => {
    return type === 'prd' ? <FileTextOutlined /> : <CheckSquareOutlined />;
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'green';
    if (score >= 0.7) return 'blue';
    return 'orange';
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      draft: '草稿',
      published: '已发布',
      archived: '已归档',
      active: '有效',
      deprecated: '已废弃',
    };
    return statusMap[status] || status;
  };

  const getPriorityText = (priority: string) => {
    const priorityMap: Record<string, string> = {
      high: '高',
      medium: '中',
      low: '低',
    };
    return priorityMap[priority] || priority;
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
            <div className="bg-gray-50 p-4 rounded space-y-4">
              {/* 第一行：常规筛选 */}
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
                        ...appVersions.map(v => ({
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

              <Divider style={{ margin: '12px 0' }} />

              {/* 第二行：搜索参数配置 */}
              <div>
                <div className="mb-3 text-sm font-medium text-gray-700">搜索参数配置</div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="mb-2 text-sm text-gray-600 flex items-center gap-2">
                      混合检索权重（Alpha）：
                      <span className="text-xs text-gray-400">
                        {alpha === 1.0
                          ? '纯向量检索'
                          : alpha === 0
                          ? '纯关键词检索'
                          : `向量 ${(alpha * 100).toFixed(0)}% + 关键词 ${((1 - alpha) * 100).toFixed(0)}%`}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-500 w-16">关键词</span>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={alpha}
                        onChange={e => setAlpha(parseFloat(e.target.value))}
                        className="flex-1"
                      />
                      <span className="text-xs text-gray-500 w-12">向量</span>
                      <InputNumber
                        min={0}
                        max={1}
                        step={0.1}
                        value={alpha}
                        onChange={value => setAlpha(value || 1.0)}
                        style={{ width: 80 }}
                        size="small"
                      />
                    </div>
                    <div className="mt-1 text-xs text-gray-400">
                      💡 向量检索适合语义搜索，关键词检索适合精确匹配
                    </div>
                  </div>

                  <div>
                    <div className="mb-2 text-sm text-gray-600">
                      相似度阈值：
                      <span className="text-xs text-gray-400 ml-2">
                        只显示相似度 ≥ {(scoreThreshold * 100).toFixed(0)}% 的结果
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-500 w-16">宽松</span>
                      <input
                        type="range"
                        min="0.5"
                        max="0.95"
                        step="0.05"
                        value={scoreThreshold}
                        onChange={e => setScoreThreshold(parseFloat(e.target.value))}
                        className="flex-1"
                      />
                      <span className="text-xs text-gray-500 w-12">严格</span>
                      <InputNumber
                        min={0.5}
                        max={0.95}
                        step={0.05}
                        value={scoreThreshold}
                        onChange={value => setScoreThreshold(value || 0.7)}
                        style={{ width: 80 }}
                        size="small"
                      />
                    </div>
                    <div className="mt-1 text-xs text-gray-400">
                      💡 阈值越高，结果越精确但数量可能越少
                    </div>
                  </div>
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
                              {item.metadata.code && <span>{item.metadata.code}</span>}
                              {item.metadata.code && <span>•</span>}
                              <span>{getStatusText(item.metadata.status)}</span>
                              <span>•</span>
                              <span>{formatDate(item.metadata.created_at)}</span>
                            </div>
                          </div>
                          <Badge
                            status={item.metadata.status === 'published' ? 'success' : 'default'}
                            text={getStatusText(item.metadata.status)}
                          />
                        </div>

                        <div className="text-gray-700 text-sm line-clamp-3 mb-2">
                          {item.content}
                        </div>

                        {item.highlights && item.highlights.length > 0 && (
                          <div className="text-xs text-gray-500 bg-yellow-50 p-2 rounded mb-2">
                            <div className="font-medium mb-1">相关片段：</div>
                            {item.highlights.slice(0, 2).map((highlight, idx) => (
                              <div key={idx} className="line-clamp-2">{highlight}</div>
                            ))}
                          </div>
                        )}
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
                              {item.metadata.code && <span>{item.metadata.code}</span>}
                              {item.metadata.code && <span>•</span>}
                              {item.metadata.priority && (
                                <>
                                  <Tag
                                    color={
                                      item.metadata.priority === 'high'
                                        ? 'red'
                                        : item.metadata.priority === 'medium'
                                        ? 'orange'
                                        : 'blue'
                                    }
                                  >
                                    {getPriorityText(item.metadata.priority)}
                                  </Tag>
                                  <span>•</span>
                                </>
                              )}
                              <span>{getStatusText(item.metadata.status)}</span>
                              <span>•</span>
                              <span>{formatDate(item.metadata.created_at)}</span>
                            </div>
                          </div>
                          <Badge
                            status={item.metadata.status === 'active' ? 'success' : 'default'}
                            text={getStatusText(item.metadata.status)}
                          />
                        </div>

                        <div className="text-gray-700 text-sm line-clamp-3 mb-2">
                          {item.content}
                        </div>

                        {item.highlights && item.highlights.length > 0 && (
                          <div className="text-xs text-gray-500 bg-yellow-50 p-2 rounded">
                            <div className="font-medium mb-1">相关片段：</div>
                            {item.highlights.slice(0, 2).map((highlight, idx) => (
                              <div key={idx} className="line-clamp-2">{highlight}</div>
                            ))}
                          </div>
                        )}
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
