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
} from 'antd';
import { EditOutlined, ArrowLeftOutlined, HistoryOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { mockPRDs, mockTags, mockTestCases } from '../../mock/data';
import type { ColumnsType } from 'antd/es/table';

export default function PRDDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [showHistory, setShowHistory] = useState(false);

  const prd = mockPRDs.find(p => p.id === id);

  if (!prd) {
    return <div className="p-6">PRD 不存在</div>;
  }

  const statusMap = {
    draft: { text: '草稿', color: 'default' },
    published: { text: '已发布', color: 'success' },
    archived: { text: '已归档', color: 'warning' },
  };

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

  // 关联的测试用例
  const relatedTestCases = mockTestCases.filter(tc => tc.moduleId === prd.moduleId);

  const testCaseColumns: ColumnsType<typeof relatedTestCases[0]> = [
    {
      title: '用例标题',
      dataIndex: 'title',
      key: 'title',
      render: (title, record) => (
        <a
          onClick={() => navigate(`/testcase/${record.id}`)}
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
          functional: '功能测试',
          performance: '性能测试',
          security: '安全测试',
          ui: 'UI测试',
        };
        return map[type as keyof typeof map];
      },
    },
  ];

  return (
    <div className="p-6">
      <div className="mb-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/prd')}>
          返回列表
        </Button>
      </div>

      <Card
        title={
          <div className="flex justify-between items-center">
            <span className="text-xl">{prd.title}</span>
            <Space>
              <Button
                icon={<HistoryOutlined />}
                onClick={() => setShowHistory(!showHistory)}
              >
                版本历史
              </Button>
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => navigate(`/prd/${id}/edit`)}
              >
                编辑
              </Button>
            </Space>
          </div>
        }
      >
        <Descriptions column={2} bordered>
          <Descriptions.Item label="所属模块">{prd.moduleName}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Badge
              status={statusMap[prd.status].color as any}
              text={statusMap[prd.status].text}
            />
          </Descriptions.Item>
          <Descriptions.Item label="当前版本">v{prd.version}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{prd.createdAt}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{prd.updatedAt}</Descriptions.Item>
          <Descriptions.Item label="标签">
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

        <Divider />

        {showHistory && (
          <>
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
            <Divider />
          </>
        )}

        <h3 className="text-lg font-bold mb-4">文档内容</h3>
        <div className="prose max-w-none bg-gray-50 p-4 rounded">
          <ReactMarkdown>{prd.content}</ReactMarkdown>
        </div>

        <Divider />

        <h3 className="text-lg font-bold mb-4">关联测试用例 ({relatedTestCases.length})</h3>
        <Table
          columns={testCaseColumns}
          dataSource={relatedTestCases}
          rowKey="id"
          pagination={false}
        />
      </Card>
    </div>
  );
}
