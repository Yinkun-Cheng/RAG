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
import { mockTestCases, mockAppVersions, mockModules, mockTags, TestCase } from '../../mock/data';

const { Search } = Input;
const { Panel } = Collapse;

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

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const modules: { id: string; name: string }[] = [];
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

  // 优先级配置
  const priorityConfig = {
    high: { text: '高', color: 'red' },
    medium: { text: '中', color: 'orange' },
    low: { text: '低', color: 'blue' },
  };

  // 类型配置
  const typeConfig = {
    functional: { text: '功能', color: 'blue' },
    performance: { text: '性能', color: 'purple' },
    security: { text: '安全', color: 'red' },
    ui: { text: 'UI', color: 'green' },
  };

  // 状态配置
  const statusConfig = {
    active: { text: '有效', badge: 'success' },
    deprecated: { text: '已废弃', badge: 'default' },
  };

  // 过滤当前项目的 App 版本和测试用例
  const projectVersions = mockAppVersions.filter(v => v.projectId === projectId);
  const projectTestCases = mockTestCases.filter(tc => tc.projectId === projectId);

  // 初始化时展开所有面板
  useEffect(() => {
    setActiveKeys(projectVersions.map(v => v.id));
  }, [projectId]);

  // 按 App 版本分组测试用例
  const groupedTestCases = projectVersions.map(version => {
    const testCases = projectTestCases.filter(tc => {
      const matchVersion = tc.appVersionId === version.id;
      const matchSearch =
        !searchText || tc.title.toLowerCase().includes(searchText.toLowerCase());
      const matchModule = !selectedModule || tc.moduleId === selectedModule;
      const matchPriority = !selectedPriority || tc.priority === selectedPriority;
      const matchType = !selectedType || tc.type === selectedType;
      const matchStatus = !selectedStatus || tc.status === selectedStatus;
      const matchTags =
        selectedTags.length === 0 || selectedTags.every(tag => tc.tags.includes(tag));
      return (
        matchVersion &&
        matchSearch &&
        matchModule &&
        matchPriority &&
        matchType &&
        matchStatus &&
        matchTags
      );
    });
    return { version, testCases };
  });

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
      dataIndex: 'moduleName',
      key: 'moduleName',
      width: 150,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: priority => {
        const config = priorityConfig[priority as keyof typeof priorityConfig];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: type => {
        const config = typeConfig[type as keyof typeof typeConfig];
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: status => {
        const config = statusConfig[status as keyof typeof statusConfig];
        return <Badge status={config.badge as any} text={config.text} />;
      },
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: string[]) => (
        <>
          {tags.slice(0, 2).map((tag: string) => {
            const tagInfo = mockTags.find(t => t.name === tag);
            return (
              <Tag key={tag} color={tagInfo?.color || 'default'}>
                {tag}
              </Tag>
            );
          })}
          {tags.length > 2 && <Tag>+{tags.length - 2}</Tag>}
        </>
      ),
    },
    {
      title: '步骤数',
      dataIndex: 'steps',
      key: 'steps',
      width: 80,
      align: 'center',
      render: steps => steps.length,
    },
    {
      title: '更新时间',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      width: 120,
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

  const handleDelete = (testCaseId: string) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: '确定要删除这个测试用例吗？此操作不可恢复。',
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => {
        console.log('删除测试用例:', testCaseId);
        message.success('删除成功');
      },
    });
  };

  // 全部展开
  const handleExpandAll = () => {
    setActiveKeys(projectVersions.map(v => v.id));
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
              options={mockTags.map(t => ({ label: t.name, value: t.name }))}
            />
          </Space>
        </Space>
      </div>

      {/* 按版本分组展示 */}
      <Collapse
        activeKey={activeKeys}
        onChange={keys => setActiveKeys(keys as string[])}
        expandIconPosition="start"
      >
        {groupedTestCases.map(({ version, testCases }) => (
          <Panel
            key={version.id}
            header={
              <div className="flex justify-between items-center w-full pr-4">
                <Space>
                  <FolderOutlined style={{ fontSize: 18, color: '#1890ff' }} />
                  <span className="font-bold">{version.version}</span>
                  <span className="text-gray-500">- {version.description}</span>
                  <Badge count={testCases.length} style={{ backgroundColor: '#52c41a' }} />
                </Space>
                <Button
                  type="primary"
                  size="small"
                  icon={<PlusOutlined />}
                  onClick={e => {
                    e.stopPropagation();
                    navigate(`/project/${projectId}/testcase/new?version=${version.id}`);
                  }}
                >
                  新建测试用例
                </Button>
              </div>
            }
          >
            <Table
              columns={columns}
              dataSource={testCases}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Panel>
        ))}
      </Collapse>
    </div>
  );
}
