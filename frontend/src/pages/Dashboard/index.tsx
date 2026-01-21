import { useParams } from 'react-router-dom';
import { Card, Row, Col, Statistic, List, Tag } from 'antd';
import {
  FileTextOutlined,
  CheckSquareOutlined,
  TagOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { mockPRDs, mockTestCases, mockTags, mockProjects } from '../../mock/data';

export default function Dashboard() {
  const { projectId } = useParams<{ projectId: string }>();

  // 过滤当前项目的数据
  const projectPRDs = mockPRDs.filter(p => p.projectId === projectId);
  const projectTestCases = mockTestCases.filter(tc => tc.projectId === projectId);
  const project = mockProjects.find(p => p.id === projectId);

  // 获取最近更新的 PRD（前5条）
  const recentPRDs = [...projectPRDs]
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5);

  // 获取最近更新的测试用例（前5条）
  const recentTestCases = [...projectTestCases]
    .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
    .slice(0, 5);

  // 统计状态
  const prdStatusCount = {
    draft: projectPRDs.filter(p => p.status === 'draft').length,
    published: projectPRDs.filter(p => p.status === 'published').length,
    archived: projectPRDs.filter(p => p.status === 'archived').length,
  };

  const testCaseStatusCount = {
    active: projectTestCases.filter(tc => tc.status === 'active').length,
    deprecated: projectTestCases.filter(tc => tc.status === 'deprecated').length,
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{project?.name} - 仪表盘</h1>
        <p className="text-gray-500 mt-1">{project?.description}</p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} className="mb-6">
        <Col span={8}>
          <Card>
            <Statistic
              title="PRD 文档"
              value={projectPRDs.length}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
            <div className="mt-2 text-sm text-gray-500">
              草稿 {prdStatusCount.draft} / 已发布 {prdStatusCount.published} / 已归档 {prdStatusCount.archived}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="测试用例"
              value={projectTestCases.length}
              prefix={<CheckSquareOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div className="mt-2 text-sm text-gray-500">
              有效 {testCaseStatusCount.active} / 已废弃 {testCaseStatusCount.deprecated}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="标签"
              value={mockTags.length}
              prefix={<TagOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 最近更新的 PRD */}
        <Col span={12}>
          <Card title="最近更新的 PRD" extra={<ClockCircleOutlined />}>
            <List
              dataSource={recentPRDs}
              renderItem={prd => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <a href={`/project/${projectId}/prd/${prd.id}`}>
                        {prd.title}
                      </a>
                    }
                    description={
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">{prd.moduleName}</span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-500">{prd.appVersion}</span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-500">{prd.updatedAt}</span>
                      </div>
                    }
                  />
                  <div>
                    {prd.status === 'draft' && <Tag color="default">草稿</Tag>}
                    {prd.status === 'published' && <Tag color="green">已发布</Tag>}
                    {prd.status === 'archived' && <Tag color="red">已归档</Tag>}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 最近更新的测试用例 */}
        <Col span={12}>
          <Card title="最近更新的测试用例" extra={<ClockCircleOutlined />}>
            <List
              dataSource={recentTestCases}
              renderItem={tc => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <a href={`/project/${projectId}/testcase/${tc.id}`}>
                        {tc.title}
                      </a>
                    }
                    description={
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">{tc.moduleName}</span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-500">{tc.appVersion}</span>
                        <span className="text-gray-400">•</span>
                        <span className="text-gray-500">{tc.updatedAt}</span>
                      </div>
                    }
                  />
                  <div className="flex gap-1">
                    {tc.priority === 'high' && <Tag color="red">高</Tag>}
                    {tc.priority === 'medium' && <Tag color="orange">中</Tag>}
                    {tc.priority === 'low' && <Tag color="blue">低</Tag>}
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
