import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Steps,
  Badge,
  Divider,
  Image,
} from 'antd';
import {
  EditOutlined,
  ArrowLeftOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { mockTestCases, mockTags } from '../../mock/data';

export default function TestCaseDetail() {
  const { id, projectId } = useParams<{ id: string; projectId: string }>();
  const navigate = useNavigate();

  const testCase = mockTestCases.find(tc => tc.id === id && tc.projectId === projectId);

  if (!testCase) {
    return (
      <div className="p-6">
        <div className="text-center py-20">
          <p className="text-xl text-gray-500">测试用例不存在</p>
          <Button
            type="primary"
            className="mt-4"
            onClick={() => navigate(`/project/${projectId}/testcase`)}
          >
            返回列表
          </Button>
        </div>
      </div>
    );
  }

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
    active: { text: '有效', badge: 'success', icon: <CheckCircleOutlined /> },
    deprecated: { text: '已废弃', badge: 'default', icon: <CloseCircleOutlined /> },
  };

  const currentStatus = statusConfig[testCase.status];

  return (
    <div className="p-6">
      <div className="mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(`/project/${projectId}/testcase`)}
        >
          返回列表
        </Button>
      </div>

      <Card
        title={
          <div className="flex justify-between items-center">
            <span className="text-xl font-bold">{testCase.title}</span>
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={() => navigate(`/project/${projectId}/testcase/${id}/edit`)}
            >
              编辑
            </Button>
          </div>
        }
      >
        {/* 基本信息 */}
        <Descriptions column={2} bordered size="small">
          <Descriptions.Item label="App 版本">{testCase.appVersion}</Descriptions.Item>
          <Descriptions.Item label="所属模块">{testCase.moduleName}</Descriptions.Item>
          <Descriptions.Item label="优先级">
            <Tag color={priorityConfig[testCase.priority].color}>
              {priorityConfig[testCase.priority].text}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="类型">
            <Tag color={typeConfig[testCase.type].color}>
              {typeConfig[testCase.type].text}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            <Space>
              <Badge status={currentStatus.badge as any} />
              {currentStatus.icon}
              <span>{currentStatus.text}</span>
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="步骤数">{testCase.steps.length}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{testCase.createdAt}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{testCase.updatedAt}</Descriptions.Item>
          <Descriptions.Item label="标签" span={2}>
            {testCase.tags.map(tag => {
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

        {/* 前置条件 */}
        <div className="mb-6">
          <h3 className="text-lg font-bold mb-3">前置条件</h3>
          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <p className="text-gray-700">{testCase.precondition}</p>
          </div>
        </div>

        {/* 测试步骤 */}
        <div className="mb-6">
          <h3 className="text-lg font-bold mb-3">测试步骤</h3>
          <Steps
            direction="vertical"
            current={testCase.steps.length}
            items={testCase.steps.map((step) => ({
              title: `步骤 ${step.order}`,
              description: (
                <div className="mt-2">
                  <p className="text-gray-700 mb-2">{step.description}</p>
                  {step.screenshots && step.screenshots.length > 0 && (
                    <div className="flex gap-2 flex-wrap">
                      <Image.PreviewGroup>
                        {step.screenshots.map((screenshot, idx) => (
                          <Image
                            key={idx}
                            width={100}
                            height={100}
                            src={screenshot}
                            alt={`步骤 ${step.order} 截图 ${idx + 1}`}
                            className="object-cover rounded"
                          />
                        ))}
                      </Image.PreviewGroup>
                    </div>
                  )}
                </div>
              ),
              status: 'finish',
            }))}
          />
        </div>

        {/* 预期结果 */}
        <div>
          <h3 className="text-lg font-bold mb-3">预期结果</h3>
          <div className="bg-green-50 border border-green-200 rounded p-4">
            <p className="text-gray-700">{testCase.expectedResult}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
