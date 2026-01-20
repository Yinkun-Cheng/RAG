import { useState } from 'react';
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
import { mockPRDs, mockTags, mockTestCases } from '../../mock/data';
import type { ColumnsType } from 'antd/es/table';

export default function PRDDetail() {
  const { id, projectId } = useParams<{ id: string; projectId: string }>();
  const navigate = useNavigate();
  const [showHistory, setShowHistory] = useState(false);

  const prd = mockPRDs.find(p => p.id === id && p.projectId === projectId);

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

  const currentStatus = statusConfig[prd.status];

  // Mock 版本历史
  const versionHistory = [
    {
      version: 2,
      date: '2025-01-15',
      author: '张三',
      changes: '更新了功能需求章节，添加了非功能需求',
    },
    {
      version: 1,
      date: '2025-01-10',
      author: '李四',
      changes: '初始版本创建',
    },
  ];

  // 关联的测试用例（同一个模块下的）
  const relatedTestCases = mockTestCases.filter(
    tc => tc.moduleId === prd.moduleId && tc.projectId === projectId
  );

  const testCaseColumns: ColumnsType<typeof relatedTestCases[0]> = [
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
        const map = {
          high: { text: '高', color: 'red' },
          medium: { text: '中', color: 'orange' },
          low: { text: '低', color: 'blue' },
        };
        return <Tag color={map[priority].color}>{map[priority].text}</Tag>;
      },
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: type => {
        const map = {
          functional: '功能',
          performance: '性能',
          security: '安全',
          ui: 'UI',
        };
        return <Tag color="blue">{map[type as keyof typeof map]}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: status => {
        const map = {
          active: { text: '有效', badge: 'success' },
          deprecated: { text: '已废弃', badge: 'default' },
        };
        return <Badge status={map[status].badge as any} text={map[status].text} />;
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
          <Descriptions.Item label="App 版本">{prd.appVersion}</Descriptions.Item>
          <Descriptions.Item label="所属模块">{prd.moduleName}</Descriptions.Item>
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
          <Descriptions.Item label="创建时间">{prd.createdAt}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{prd.updatedAt}</Descriptions.Item>
          {prd.status === 'published' && prd.lastSyncTime && (
            <Descriptions.Item label="最后同步时间" span={2}>
              {prd.lastSyncTime}
            </Descriptions.Item>
          )}
          <Descriptions.Item label="标签" span={2}>
            {prd.tags.map(tag => {
              const tagInfo = mockTags.find(t => t.name === tag);
              return (
                <Tag key={tag} color={tagInfo?.color || 'default'}>
                  {tag}
                </Tag>
              );
            })}
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
