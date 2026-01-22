import { useState, useEffect } from 'react';
import {
  Collapse,
  Table,
  Button,
  Input,
  Select,
  Tag,
  Space,
  Badge,
  Modal,
  message,
  Spin,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  FolderOutlined,
  ExpandOutlined,
  ShrinkOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import api from '../../api';

const { Search } = Input;
const { Panel } = Collapse;

// 定义类型接口
interface TestCase {
  id: string;
  code: string;
  title: string;
  module_id?: string;
  prd_id?: string;
  precondition: string;
  expected_result: string;
  priority: string;
  type: string;
  status: string;
  app_version_id: string;
  created_at: string;
  updated_at: string;
  tags?: any[];
  steps?: any[];
  module?: { name: string };
  prd?: { code: string; title: string };
}

interface PRD {
  id: string;
  code: string;
  title: string;
  status: string;
  app_version_id: string;
}

interface AppVersion {
  id: string;
  version: string;
  description: string;
}

interface Module {
  id: string;
  name: string;
  children?: Module[];
}

interface Tag {
  id: string;
  name: string;
  color: string;
}

export default function TestCaseList() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const [searchText, setSearchText] = useState('');
  const [selectedModule, setSelectedModule] = useState<string | undefined>();
  const [selectedPriority, setSelectedPriority] = useState<string | undefined>();
  const [selectedType, setSelectedType] = useState<string | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>();
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [activeKeys, setActiveKeys] = useState<string[]>([]);
  
  // 数据状态
  const [loading, setLoading] = useState(false);
  const [testCases, setTestCases] = useState<TestCase[]>([]);
  const [appVersions, setAppVersions] = useState<AppVersion[]>([]);
  const [prds, setPrds] = useState<PRD[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);

  // 加载数据
  useEffect(() => {
    if (!projectId) return;
    loadData();
  }, [projectId]);

  const loadData = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      // 并行加载所有数据
      const [testCaseRes, versionRes, prdRes, moduleRes, tagRes] = await Promise.all([
        api.testcase.list(projectId, { page: 1, page_size: 100 }),
        api.appVersion.list(projectId),
        api.prd.list(projectId, { page: 1, page_size: 100 }),
        api.module.getTree(projectId),
        api.tag.list(projectId),
      ]);

      setTestCases(testCaseRes.data.items || []);
      setAppVersions(versionRes.data || []);
      setPrds(prdRes.data.items || []);
      setModules(moduleRes.data || []);
      setTags(tagRes.data || []);
      
      // 初始化时展开所有面板
      setActiveKeys((versionRes.data || []).map((v: AppVersion) => v.id));
    } catch (error: any) {
      console.error('Failed to load data:', error);
      message.error(error.message || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const result: { id: string; name: string }[] = [];
    const flatten = (items: Module[]) => {
      items.forEach(item => {
        result.push({ id: item.id, name: item.name });
        if (item.children) {
          flatten(item.children);
        }
      });
    };
    flatten(modules);
    return result;
  };

  const allModules = getAllModules();

  // 优先级配置
  const priorityConfig: Record<string, { text: string; color: string }> = {
    P0: { text: 'P0', color: 'red' },
    P1: { text: 'P1', color: 'orange' },
    P2: { text: 'P2', color: 'blue' },
    P3: { text: 'P3', color: 'default' },
  };

  // 类型配置
  const typeConfig: Record<string, { text: string; color: string }> = {
    functional: { text: '功能', color: 'blue' },
    performance: { text: '性能', color: 'purple' },
    security: { text: '安全', color: 'red' },
    ui: { text: 'UI', color: 'green' },
  };

  // 状态配置
  const statusConfig: Record<string, { text: string; badge: string }> = {
    active: { text: '有效', badge: 'success' },
    deprecated: { text: '已废弃', badge: 'default' },
    draft: { text: '草稿', badge: 'warning' },
  };

  // 按 App 版本 -> PRD -> 测试用例 三层分组
  const groupedTestCases = appVersions.map(version => {
    // 获取该版本下的所有 PRD
    const versionPRDs = prds.filter(prd => prd.app_version_id === version.id);
    
    // 为每个 PRD 分组测试用例
    const prdGroups = versionPRDs.map(prd => {
      const prdTestCases = testCases.filter(tc => {
        const matchPRD = tc.prd_id === prd.id;
        const matchSearch =
          !searchText || tc.title.toLowerCase().includes(searchText.toLowerCase());
        const matchModule = !selectedModule || tc.module_id === selectedModule;
        const matchPriority = !selectedPriority || tc.priority === selectedPriority;
        const matchType = !selectedType || tc.type === selectedType;
        const matchStatus = !selectedStatus || tc.status === selectedStatus;
        const matchTags =
          selectedTags.length === 0 || 
          (tc.tags && tc.tags.length > 0 && selectedTags.every(tagId => tc.tags!.some((t: any) => t.id === tagId)));
        return (
          matchPRD &&
          matchSearch &&
          matchModule &&
          matchPriority &&
          matchType &&
          matchStatus &&
          matchTags
        );
      });
      return { prd, testCases: prdTestCases };
    });
    
    return { version, prdGroups };
  });

  // 格式化日期
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const columns: ColumnsType<TestCase> = [
    {
      title: '用例标题',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (title, record) => (
        <a
          onClick={() => navigate(`/project/${projectId}/testcase/${record.id}`)}
          className="text-blue-600 hover:underline"
        >
          {title}
        </a>
      ),
    },
    {
      title: '所属模块',
      dataIndex: 'module_id',
      key: 'module_id',
      width: 150,
      render: (moduleId: string, record) => {
        // 优先使用 module 对象的 name
        if (record.module?.name) {
          return record.module.name;
        }
        // 否则从 modules 列表中查找
        const module = allModules.find(m => m.id === moduleId);
        return module?.name || '-';
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: (priority: string) => {
        const config = priorityConfig[priority] || { text: priority, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const config = typeConfig[type] || { text: type, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const config = statusConfig[status] || { text: status, badge: 'default' };
        return <Badge status={config.badge as any} text={config.text} />;
      },
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tags: any[]) => {
        if (!tags || tags.length === 0) return '-';
        return (
          <>
            {tags.slice(0, 2).map((tag: any) => (
              <Tag key={tag.id} color={tag.color || 'default'}>
                {tag.name}
              </Tag>
            ))}
            {tags.length > 2 && <Tag>+{tags.length - 2}</Tag>}
          </>
        );
      },
    },
    {
      title: '步骤数',
      dataIndex: 'steps',
      key: 'steps',
      width: 80,
      align: 'center',
      render: (steps: any[]) => steps?.length || 0,
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 120,
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/project/${projectId}/testcase/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/project/${projectId}/testcase/${record.id}/edit`)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleDelete = async (testCaseId: string) => {
    if (!projectId) return;
    
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: '确定要删除这个测试用例吗？此操作不可恢复。',
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await api.testcase.delete(projectId, testCaseId);
          message.success('删除成功');
          loadData(); // 重新加载数据
        } catch (error: any) {
          console.error('Failed to delete test case:', error);
          message.error(error.message || '删除失败');
        }
      },
    });
  };

  // 全部展开
  const handleExpandAll = () => {
    setActiveKeys(appVersions.map(v => v.id));
  };

  // 全部折叠
  const handleCollapseAll = () => {
    setActiveKeys([]);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">测试用例管理</h1>
        <Space>
          <Button icon={<ExpandOutlined />} onClick={handleExpandAll}>
            全部展开
          </Button>
          <Button icon={<ShrinkOutlined />} onClick={handleCollapseAll}>
            全部折叠
          </Button>
        </Space>
      </div>

      {/* 筛选区域 */}
      <div className="bg-white p-4 rounded mb-4">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Search
            placeholder="搜索测试用例标题"
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={setSearchText}
            onChange={e => setSearchText(e.target.value)}
          />
          <Space wrap>
            <Select
              placeholder="选择模块"
              style={{ width: 200 }}
              allowClear
              value={selectedModule}
              onChange={setSelectedModule}
              options={allModules.map(m => ({ label: m.name, value: m.id }))}
            />
            <Select
              placeholder="选择优先级"
              style={{ width: 150 }}
              allowClear
              value={selectedPriority}
              onChange={setSelectedPriority}
            >
              {Object.entries(priorityConfig).map(([key, config]) => (
                <Select.Option key={key} value={key}>
                  <Tag color={config.color}>{config.text}</Tag>
                </Select.Option>
              ))}
            </Select>
            <Select
              placeholder="选择类型"
              style={{ width: 150 }}
              allowClear
              value={selectedType}
              onChange={setSelectedType}
            >
              {Object.entries(typeConfig).map(([key, config]) => (
                <Select.Option key={key} value={key}>
                  <Tag color={config.color}>{config.text}</Tag>
                </Select.Option>
              ))}
            </Select>
            <Select
              placeholder="选择状态"
              style={{ width: 150 }}
              allowClear
              value={selectedStatus}
              onChange={setSelectedStatus}
            >
              {Object.entries(statusConfig).map(([key, config]) => (
                <Select.Option key={key} value={key}>
                  <Badge status={config.badge as any} text={config.text} />
                </Select.Option>
              ))}
            </Select>
            <Select
              mode="multiple"
              placeholder="选择标签"
              style={{ width: 300 }}
              allowClear
              value={selectedTags}
              onChange={setSelectedTags}
              options={tags.map(t => ({ label: t.name, value: t.id }))}
            />
          </Space>
        </Space>
      </div>

      {/* 加载状态 */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Spin size="large" spinning={loading} tip="加载中...">
            <div style={{ minHeight: 200 }} />
          </Spin>
        </div>
      ) : groupedTestCases.length === 0 ? (
        <div className="bg-white p-8 rounded text-center text-gray-500">
          暂无测试用例数据
        </div>
      ) : (
        /* 按版本 -> PRD -> 测试用例 三层分组展示 */
        <Collapse
          activeKey={activeKeys}
          onChange={keys => setActiveKeys(keys as string[])}
          expandIconPosition="start"
        >
          {groupedTestCases.map(({ version, prdGroups }) => (
            <Panel
              key={version.id}
              header={
                <div className="flex justify-between items-center w-full pr-4">
                  <Space>
                    <FolderOutlined style={{ fontSize: 18, color: '#1890ff' }} />
                    <span className="font-bold">{version.version}</span>
                    <span className="text-gray-500">- {version.description}</span>
                    <Badge 
                      count={prdGroups.reduce((sum, pg) => sum + pg.testCases.length, 0)} 
                      style={{ backgroundColor: '#52c41a' }} 
                    />
                  </Space>
                </div>
              }
            >
              {/* PRD 二级折叠 */}
              <Collapse
                className="ml-4"
                expandIconPosition="start"
                defaultActiveKey={prdGroups.map(pg => pg.prd.id)}
              >
                {prdGroups.map(({ prd, testCases: prdTestCases }) => (
                  <Panel
                    key={prd.id}
                    header={
                      <div className="flex justify-between items-center w-full pr-4">
                        <Space>
                          <span className="text-blue-600 font-medium">{prd.code}</span>
                          <span>{prd.title}</span>
                          <Badge count={prdTestCases.length} style={{ backgroundColor: '#52c41a' }} />
                        </Space>
                        <Button
                          type="primary"
                          size="small"
                          icon={<PlusOutlined />}
                          onClick={e => {
                            e.stopPropagation();
                            navigate(`/project/${projectId}/testcase/new?version=${version.id}&prd=${prd.id}`);
                          }}
                        >
                          新建测试用例
                        </Button>
                      </div>
                    }
                  >
                    {prdTestCases.length > 0 ? (
                      <Table
                        columns={columns}
                        dataSource={prdTestCases}
                        rowKey="id"
                        pagination={false}
                        size="small"
                      />
                    ) : (
                      <div className="text-center text-gray-400 py-4">
                        暂无测试用例
                      </div>
                    )}
                  </Panel>
                ))}
              </Collapse>
            </Panel>
          ))}
        </Collapse>
      )}
    </div>
  );
}
