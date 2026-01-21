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
  Tooltip,
  Modal,
  Form,
  message,
  Spin,
  Empty,
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
  ExpandOutlined,
  ShrinkOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import api, { PRD, Module, Tag as TagType, AppVersion } from '../../api';

const { Search } = Input;
const { Panel } = Collapse;

export default function PRDList() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const [searchText, setSearchText] = useState('');
  const [selectedModule, setSelectedModule] = useState<string | undefined>();
  const [selectedStatus, setSelectedStatus] = useState<string | undefined>();
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [versionModalVisible, setVersionModalVisible] = useState(false);
  const [activeKeys, setActiveKeys] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [prds, setPrds] = useState<PRD[]>([]);
  const [modules, setModules] = useState<Module[]>([]);
  const [tags, setTags] = useState<TagType[]>([]);
  const [appVersions, setAppVersions] = useState<AppVersion[]>([]);
  const [form] = Form.useForm();

  // 获取所有数据
  useEffect(() => {
    if (projectId) {
      fetchAllData();
    }
  }, [projectId]);

  const fetchAllData = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      // 并行获取所有数据
      const [prdsRes, modulesRes, tagsRes, versionsRes] = await Promise.all([
        api.prd.list(projectId, { page: 1, page_size: 100 }),
        api.module.getTree(projectId),
        api.tag.list(projectId),
        api.appVersion.list(projectId),
      ]);

      setPrds(prdsRes.data.items || []);
      setModules(modulesRes.data || []);
      setTags(tagsRes.data || []);
      setAppVersions(versionsRes.data || []);
      setActiveKeys((versionsRes.data || []).map((v: AppVersion) => v.id));
    } catch (error) {
      console.error('Failed to fetch data:', error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const modulesList: { id: string; name: string }[] = [];
    const flatten = (items: Module[]) => {
      items.forEach(item => {
        modulesList.push({ id: item.id, name: item.name });
        if (item.children) {
          flatten(item.children);
        }
      });
    };
    flatten(modules);
    return modulesList;
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
  const groupedPRDs = appVersions.map(version => {
    const versionPrds = prds.filter(prd => {
      const matchVersion = prd.app_version_id === version.id;
      const matchSearch =
        !searchText || prd.title.toLowerCase().includes(searchText.toLowerCase());
      const matchModule = !selectedModule || prd.module_id === selectedModule;
      const matchStatus = !selectedStatus || prd.status === selectedStatus;
      const matchTags =
        selectedTags.length === 0 || 
        selectedTags.every(tag => prd.tags?.some(t => t.id === tag));
      return matchVersion && matchSearch && matchModule && matchStatus && matchTags;
    });
    return { version, prds: versionPrds };
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
            onClick={() => navigate(`/project/${projectId}/prd/${record.id}`)}
            className="text-blue-600 hover:underline"
          >
            {title}
          </a>
        </Space>
      ),
    },
    {
      title: '所属模块',
      dataIndex: 'module_id',
      key: 'module_id',
      width: 150,
      render: (moduleId) => {
        const module = allModules.find(m => m.id === moduleId);
        return module?.name || '-';
      },
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
      render: (status) => {
        const config = statusConfig[status as keyof typeof statusConfig];
        if (!config) return status;
        return (
          <Tooltip title={config.description}>
            <Space>
              <Badge status={config.badge as any} />
              <span style={{ color: config.color }}>{config.icon}</span>
              <span>{config.text}</span>

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
      render: (prdTags: TagType[]) => (
        <>
          {prdTags?.map((tag: TagType) => (
            <Tag key={tag.id} color={tag.color || 'default'}>
              {tag.name}
            </Tag>
          ))}
        </>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 120,
      render: (date) => new Date(date).toLocaleDateString('zh-CN'),
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
            onClick={() => navigate(`/project/${projectId}/prd/${record.id}`)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => navigate(`/project/${projectId}/prd/${record.id}/edit`)}
          >
            编辑
          </Button>
          {record.status === 'draft' && (
            <Button
              type="link"
              size="small"
              icon={<SyncOutlined />}
              onClick={() => handlePublish(record.id)}
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
              onClick={() => handleArchive(record.id)}
            >
              归档
            </Button>
          )}
          {record.status === 'archived' && (
            <Button
              type="link"
              size="small"
              icon={<SyncOutlined />}
              onClick={() => handlePublish(record.id)}
            >
              重新发布
            </Button>
          )}
        </Space>
      ),
    },
  ];

  const handlePublish = async (prdId: string) => {
    if (!projectId) return;
    
    Modal.confirm({
      title: '确认发布',
      content: '发布后将自动向量化并同步到知识库，AI 可以检索到此文档。确认发布吗？',
      onOk: async () => {
        try {
          await api.prd.publish(projectId, prdId);
          message.success('发布成功！文档已进入知识库');
          fetchAllData();
        } catch (error) {
          console.error('Failed to publish PRD:', error);
          message.error('发布失败');
        }
      },
    });
  };

  const handleArchive = async (prdId: string) => {
    if (!projectId) return;
    
    Modal.confirm({
      title: '确认归档',
      content: '归档后将从知识库中移除，AI 将无法检索到此文档。确认归档吗？',
      onOk: async () => {
        try {
          await api.prd.archive(projectId, prdId);
          message.success('归档成功！文档已从知识库移除');
          fetchAllData();
        } catch (error) {
          console.error('Failed to archive PRD:', error);
          message.error('归档失败');
        }
      },
    });
  };

  const handleCreateVersion = async () => {
    if (!projectId) return;
    
    try {
      const values = await form.validateFields();
      await api.appVersion.create(projectId, {
        version: values.version,
        description: values.description,
      });
      
      message.success(`创建版本 ${values.version} 成功`);
      setVersionModalVisible(false);
      form.resetFields();
      fetchAllData();
    } catch (error) {
      console.error('Failed to create version:', error);
      message.error('创建版本失败');
    }
  };

  const handleDeleteVersion = async (versionId: string, versionName: string, prdCount: number) => {
    if (!projectId) return;
    
    // 检查是否有 PRD
    if (prdCount > 0) {
      Modal.warning({
        title: '无法删除版本',
        content: `版本 ${versionName} 下还有 ${prdCount} 个 PRD 文档，请先删除或移动这些文档后再删除版本。`,
      });
      return;
    }
    
    Modal.confirm({
      title: '确认删除版本',
      content: `确定要删除版本 ${versionName} 吗？此操作不可恢复。`,
      okText: '确定',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await api.appVersion.delete(projectId, versionId);
          message.success(`删除版本 ${versionName} 成功`);
          fetchAllData();
        } catch (error) {
          console.error('Failed to delete version:', error);
          message.error('删除版本失败');
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

  if (!projectId) {
    return (
      <div className="p-6">
        <Empty description="项目 ID 不存在，请从项目列表进入" />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">PRD 文档管理</h1>
        <Space>
          <Button icon={<ExpandOutlined />} onClick={handleExpandAll}>
            全部展开
          </Button>
          <Button icon={<ShrinkOutlined />} onClick={handleCollapseAll}>
            全部折叠
          </Button>
          <Button icon={<FolderOutlined />} onClick={() => setVersionModalVisible(true)}>
            新建版本
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
              options={tags.map(t => ({ label: t.name, value: t.id }))}
            />
          </Space>
        </Space>
      </div>

      {/* 按版本分组展示 */}
      {appVersions.length === 0 ? (
        <Empty description="暂无 App 版本，请先创建版本" />
      ) : (
        <Collapse
          activeKey={activeKeys}
          onChange={keys => setActiveKeys(keys as string[])}
          expandIconPosition="start"
        >
          {groupedPRDs.map(({ version, prds }) => (
            <Panel
              key={version.id}
              header={
                <div className="flex justify-between items-center w-full pr-4">
                  <Space>
                    <FolderOutlined style={{ fontSize: 18, color: '#1890ff' }} />
                    <span className="font-bold">{version.version}</span>
                    <span className="text-gray-500">- {version.description}</span>
                    <Badge count={prds.length} style={{ backgroundColor: '#52c41a' }} />
                  </Space>
                  <Space>
                    <Button
                      type="primary"
                      size="small"
                      icon={<PlusOutlined />}
                      onClick={e => {
                        e.stopPropagation();
                        console.log('PRDList - Navigating with version:', version);
                        navigate(`/project/${projectId}/prd/new?version=${version.id}`);
                      }}
                    >
                      新建 PRD
                    </Button>
                    <Button
                      danger
                      size="small"
                      icon={<DeleteOutlined />}
                      onClick={e => {
                        e.stopPropagation();
                        handleDeleteVersion(version.id, version.version, prds.length);
                      }}
                    >
                      删除版本
                    </Button>
                  </Space>
                </div>
              }
            >
              {prds.length === 0 ? (
                <Empty description="该版本暂无 PRD 文档" className="py-8" />
              ) : (
                <Table
                  columns={columns}
                  dataSource={prds}
                  rowKey="id"
                  pagination={false}
                  size="small"
                />
              )}
            </Panel>
          ))}
        </Collapse>
      )}

      {/* 新建版本 Modal */}
      <Modal
        title="新建 App 版本"
        open={versionModalVisible}
        onOk={handleCreateVersion}
        onCancel={() => {
          setVersionModalVisible(false);
          form.resetFields();
        }}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" className="mt-4">
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
