import { useState } from 'react';
import {
  Collapse,
  Table,
  Button,
  Input,
  Select,
  Tag,
  Space,
  Badge,
  Tooltip,
  Modal,
  Form,
  message,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  FolderOutlined,
  FileTextOutlined,
  SyncOutlined,
  InboxOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import { mockPRDs, mockAppVersions, mockModules, mockTags, PRD } from '../../mock/data';

const { Search } = Input;
const { Panel } = Collapse;

export default function PRDList() {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');
  const [selectedModule, setSelectedModule] = useState<string | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>();
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [versionModalVisible, setVersionModalVisible] = useState(false);
  const [form] = Form.useForm();

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

  // 状态配置（带详细说明）
  const statusConfig = {
    draft: {
      text: '草稿',
      badge: 'default',
      icon: <ClockCircleOutlined />,
      description: '文档正在编辑，未进入知识库',
      color: '#d9d9d9',
    },
    published: {
      text: '已发布',
      badge: 'success',
      icon: <CheckCircleOutlined />,
      description: '已向量化并同步到知识库，可被 AI 检索',
      color: '#52c41a',
    },
    archived: {
      text: '已归档',
      badge: 'warning',
      icon: <InboxOutlined />,
      description: '已从知识库移除，不再被 AI 检索',
      color: '#faad14',
    },
  };

  // 按 App 版本分组 PRD
  const groupedPRDs = mockAppVersions.map(version => {
    const prds = mockPRDs.filter(prd => {
      const matchVersion = prd.appVersionId === version.id;
      const matchSearch =
        !searchText || prd.title.toLowerCase().includes(searchText.toLowerCase());
      const matchModule = !selectedModule || prd.moduleId === selectedModule;
      const matchStatus = !selectedStatus || prd.status === selectedStatus;
      const matchTags =
        selectedTags.length === 0 || selectedTags.every(tag => prd.tags.includes(tag));
      return matchVersion && matchSearch && matchModule && matchStatus && matchTags;
    });
    return { version, prds };
  });

  const columns: ColumnsType<PRD> = [
    {
      title: '文档标题',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (title, record) => (
        <Space>
          <FileTextOutlined />
          <a
            onClick={() => navigate(`/prd/${record.id}`)}
            className="text-blue-600 hover:underline"
          >
            {title}
          </a>
        </Space>
      ),
    },
    {
      title: '所属模块',
      dataIndex: 'moduleName',
      key: 'moduleName',
      width: 150,
    },
    {
      title: (
        <Tooltip title="草稿：编辑中 | 已发布：在知识库中 | 已归档：已下线">
          <Space>
            状态
            <span className="text-gray-400 text-xs">(悬停查看说明)</span>
          </Space>
        </Tooltip>
      ),
      dataIndex: 'status',
      key: 'status',
      width: 180,
      render: (status, record) => {
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <Tooltip title={config.description}>
            <Space>
              <Badge status={config.badge as any} />
              <span style={{ color: config.color }}>{config.icon}</span>
              <span>{config.text}</span>
              {status === 'published' && record.lastSyncTime && (
                <span className="text-xs text-gray-400">
                  {record.lastSyncTime}
                </span>
              )}
            </Space>
          </Tooltip>
        );
      },
    },
    {
      title: '版本',
      dataIndex: 'version',
      key: 'version',
      width: 80,
      render: version => `v${version}`,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: string[]) => (
        <>
          {tags.map((tag: string) => {
            const tagInfo = mockTags.find(t => t.name === tag);
            return (
              <Tag key={tag} color={tagInfo?.color || 'default'}>
                {tag}
              </Tag>
            );
          })}
        </>
      ),
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
      width: 250,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/prd/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/prd/${record.id}/edit`)}
          >
            编辑
          </Button>
          {record.status === 'draft' && (
            <Button
              type="link"
              size="small"
              icon={<SyncOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: '确认发布',
                  content: '发布后将自动向量化并同步到知识库，AI 可以检索到此文档。确认发布吗？',
                  onOk: () => {
                    message.loading('正在发布并同步到知识库...', 1);
                    setTimeout(() => message.success('发布成功！文档已进入知识库'), 1500);
                  },
                });
              }}
            >
              发布
            </Button>
          )}
          {record.status === 'published' && (
            <Button
              type="link"
              size="small"
              danger
              icon={<InboxOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: '确认归档',
                  content: '归档后将从知识库中移除，AI 将无法检索到此文档。确认归档吗？',
                  onOk: () => {
                    message.loading('正在从知识库移除...', 1);
                    setTimeout(() => message.success('归档成功！文档已从知识库移除'), 1500);
                  },
                });
              }}
            >
              归档
            </Button>
          )}
          {record.status === 'archived' && (
            <Button
              type="link"
              size="small"
              icon={<SyncOutlined />}
              onClick={() => {
                Modal.confirm({
                  title: '确认重新发布',
                  content: '重新发布后将再次向量化并同步到知识库。确认重新发布吗？',
                  onOk: () => {
                    message.loading('正在重新发布...', 1);
                    setTimeout(() => message.success('重新发布成功！'), 1500);
                  },
                });
              }}
            >
              重新发布
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const handleCreateVersion = () => {
    form.validateFields().then(values => {
      message.success(`创建版本 ${values.version} 成功`);
      setVersionModalVisible(false);
      form.resetFields();
    });
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">PRD 文档管理</h1>
        <Space>
          <Button icon={<FolderOutlined />} onClick={() => setVersionModalVisible(true)}>
            新建版本
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/prd/new')}
          >
            新建 PRD
          </Button>
        </Space>
      </div>

      {/* 筛选区域 */}
      <div className="bg-white p-4 rounded mb-4">
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <Search
            placeholder="搜索 PRD 标题"
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
              placeholder="选择状态"
              style={{ width: 200 }}
              allowClear
              value={selectedStatus}
              onChange={setSelectedStatus}
            >
              {Object.entries(statusConfig).map(([key, config]) => (
                <Select.Option key={key} value={key}>
                  <Space>
                    {config.icon}
                    {config.text}
                  </Space>
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
        defaultActiveKey={mockAppVersions.map(v => v.id)}
        expandIconPosition="start"
      >
        {groupedPRDs.map(({ version, prds }) => (
          <Panel
            key={version.id}
            header={
              <Space>
                <FolderOutlined style={{ fontSize: 18, color: '#1890ff' }} />
                <span className="font-bold">{version.version}</span>
                <span className="text-gray-500">- {version.description}</span>
                <Badge count={prds.length} style={{ backgroundColor: '#52c41a' }} />
              </Space>
            }
          >
            <Table
              columns={columns}
              dataSource={prds}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Panel>
        ))}
      </Collapse>

      {/* 新建版本 Modal */}
      <Modal
        title="新建 App 版本"
        open={versionModalVisible}
        onOk={handleCreateVersion}
        onCancel={() => {
          setVersionModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="version"
            label="版本号"
            rules={[{ required: true, message: '请输入版本号' }]}
          >
            <Input placeholder="例如: v1.2.0" />
          </Form.Item>
          <Form.Item
            name="description"
            label="版本描述"
            rules={[{ required: true, message: '请输入版本描述' }]}
          >
            <Input.TextArea placeholder="描述这个版本的主要内容" rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
