import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Timeline,
  Table,
  Badge,
  Divider,
  Tooltip,
  Spin,
  Empty,
  message,
} from 'antd';
import {
  EditOutlined,
  ArrowLeftOutlined,
  HistoryOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css';
import api, { PRD, Module, TestCase } from '../../api';
import type { ColumnsType } from 'antd/es/table';

export default function PRDDetail() {
  const { id, projectId } = useParams<{ id: string; projectId: string }>();
  const navigate = useNavigate();
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);
  const [prd, setPrd] = useState<PRD | null>(null);
  const [module, setModule] = useState<Module | null>(null);
  const [relatedTestCases, setRelatedTestCases] = useState<TestCase[]>([]);

  useEffect(() => {
    if (projectId && id) {
      fetchData();
    }
  }, [projectId, id]);

  const fetchData = async () => {
    if (!projectId || !id) return;
    
    setLoading(true);
    try {
      // 获取 PRD 详情
      const prdRes = await api.prd.get(projectId, id);
      const prdData = prdRes.data;
      setPrd(prdData);

      // 获取模块信息
      const modulesRes = await api.module.getTree(projectId);
      const findModule = (modules: Module[], moduleId: string): Module | null => {
        for (const m of modules) {
          if (m.id === moduleId) return m;
          if (m.children) {
            const found = findModule(m.children, moduleId);
            if (found) return found;
          }
        }
        return null;
      };
      const moduleData = findModule(modulesRes.data || [], prdData.module_id);
      setModule(moduleData);

      // 获取关联的测试用例（同一个模块下的）
      const testCasesRes = await api.testcase.list(projectId, {
        module_id: prdData.module_id,
        page: 1,
        page_size: 100,
      });
      setRelatedTestCases(testCasesRes.data.items || []);
    } catch (error) {
      console.error('Failed to fetch PRD detail:', error);
      message.error('获取 PRD 详情失败');
    } finally {
      setLoading(false);
    }
  };

  if (!projectId || !id) {
    return (
      <div className="p-6">
        <Empty description="项目 ID 或 PRD ID 不存在" />
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

  if (!prd) {
    return (
      <div className="p-6">
        <div className="text-center py-20">
          <p className="text-xl text-gray-500">PRD 不存在</p>
          <Button
            type="primary"
            className="mt-4"
            onClick={() => navigate(`/project/${projectId}/prd`)}
          >
            返回列表
          </Button>
        </div>
      </div>
    );
  }

  // 状态配置
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

  const currentStatus = statusConfig[prd.status as keyof typeof statusConfig] || statusConfig.draft;

  // Mock 版本历史（TODO: 实现真实的版本历史 API）
  const versionHistory = [
    {
      version: prd.version,
      date: new Date(prd.updated_at).toLocaleDateString('zh-CN'),
      author: prd.author,
      changes: '当前版本',
    },
  ];

  const testCaseColumns: ColumnsType<TestCase> = [
    {
      title: '用例标题',
      dataIndex: 'title',
      key: 'title',
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
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: priority => {
        const map: Record<string, { text: string; color: string }> = {
          high: { text: '高', color: 'red' },
          medium: { text: '中', color: 'orange' },
          low: { text: '低', color: 'blue' },
        };
        const config = map[priority] || { text: priority, color: 'default' };
        return <Tag color={config.color}>{config.text}</Tag>;
      },
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: type => {
        const map: Record<string, string> = {
          functional: '功能',
          performance: '性能',
          security: '安全',
          ui: 'UI',
        };
        return <Tag color="blue">{map[type] || type}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: status => {
        const map: Record<string, { text: string; badge: string }> = {
          active: { text: '有效', badge: 'success' },
          deprecated: { text: '已废弃', badge: 'default' },
        };
        const config = map[status] || { text: status, badge: 'default' };
        return <Badge status={config.badge as any} text={config.text} />;
      },
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(`/project/${projectId}/prd`)}
        >
          返回列表
        </Button>
      </div>

      <Card
        title={
          <div className="flex justify-between items-center">
            <span className="text-xl font-bold">{prd.title}</span>
            <Space>
              <Button
                icon={<HistoryOutlined />}
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? '隐藏历史' : '版本历史'}
              </Button>
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => navigate(`/project/${projectId}/prd/${id}/edit`)}
              >
                编辑
              </Button>
            </Space>
          </div>
        }
      >
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="App 版本">{prd.app_version_id}</Descriptions.Item>
          <Descriptions.Item label="所属模块">{module?.name || '-'}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tooltip title={currentStatus.description}>
              <Space>
                <Badge status={currentStatus.badge as any} />
                <span style={{ color: currentStatus.color }}>{currentStatus.icon}</span>
                <span>{currentStatus.text}</span>
              </Space>
            </Tooltip>
          </Descriptions.Item>
          <Descriptions.Item label="文档版本">v{prd.version}</Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(prd.created_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {new Date(prd.updated_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
          <Descriptions.Item label="作者">{prd.author}</Descriptions.Item>
          <Descriptions.Item label="标签">
            {prd.tags?.map(tag => (
              <Tag key={tag.id} color={tag.color || 'default'}>
                {tag.name}
              </Tag>
            ))}
          </Descriptions.Item>
        </Descriptions>

        {showHistory && (
          <>
            <Divider />
            <h3 className="text-lg font-bold mb-4">版本历史</h3>
            <Timeline
              items={versionHistory.map(v => ({
                children: (
                  <div>
                    <div className="font-bold">
                      v{v.version} - {v.date} - {v.author}
                    </div>
                    <div className="text-gray-600">{v.changes}</div>
                  </div>
                ),
              }))}
            />
          </>
        )}

        <Divider />

        <h3 className="text-lg font-bold mb-4">文档内容</h3>
        <div className="prose max-w-none bg-white border rounded p-6">
          <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{prd.content}</ReactMarkdown>
        </div>

        <Divider />

        <h3 className="text-lg font-bold mb-4">
          关联测试用例 ({relatedTestCases.length})
        </h3>
        {relatedTestCases.length > 0 ? (
          <Table
            columns={testCaseColumns}
            dataSource={relatedTestCases}
            rowKey="id"
            pagination={false}
            size="small"
          />
        ) : (
          <div className="text-center py-8 text-gray-400">暂无关联测试用例</div>
        )}
      </Card>
    </div>
  );
}
