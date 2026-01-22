import { useState, useEffect } from 'react';
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
  Spin,
  message,
} from 'antd';
import {
  EditOutlined,
  ArrowLeftOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import api from '../../api';

export default function TestCaseDetail() {
  const { id, projectId } = useParams<{ id: string; projectId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [testCase, setTestCase] = useState<any>(null);

  useEffect(() => {
    if (id && projectId) {
      loadTestCase();
    }
  }, [id, projectId]);

  const loadTestCase = async () => {
    if (!id || !projectId) return;
    
    setLoading(true);
    try {
      const res = await api.testcase.get(projectId, id);
      setTestCase(res.data);
    } catch (error: any) {
      console.error('Failed to load test case:', error);
      message.error(error.message || '加载测试用例失败');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center py-20">
          <Spin size="large" spinning={loading} tip="加载中...">
            <div style={{ minHeight: 200 }} />
          </Spin>
        </div>
      </div>
    );
  }

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
  const statusConfig: Record<string, { text: string; badge: string; icon: any }> = {
    active: { text: '有效', badge: 'success', icon: <CheckCircleOutlined /> },
    deprecated: { text: '已废弃', badge: 'default', icon: <CloseCircleOutlined /> },
    draft: { text: '草稿', badge: 'warning', icon: <CloseCircleOutlined /> },
  };

  const currentStatus = testCase ? statusConfig[testCase.status] : null;

  // 格式化日期
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

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
          <Descriptions.Item label="App 版本">
            {testCase.app_version?.version || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="所属模块">
            {testCase.module?.name || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="关联PRD">
            {testCase.prd ? (
              <a
                onClick={() => navigate(`/project/${projectId}/prd/${testCase.prd_id}`)}
                className="text-blue-600 hover:underline cursor-pointer"
              >
                {testCase.prd.code} - {testCase.prd.title}
              </a>
            ) : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="用例编号">{testCase.code}</Descriptions.Item>
          <Descriptions.Item label="优先级">
            <Tag color={priorityConfig[testCase.priority]?.color || 'default'}>
              {priorityConfig[testCase.priority]?.text || testCase.priority}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="类型">
            <Tag color={typeConfig[testCase.type]?.color || 'default'}>
              {typeConfig[testCase.type]?.text || testCase.type}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            <Space>
              <Badge status={currentStatus?.badge as any} />
              {currentStatus?.icon}
              <span>{currentStatus?.text}</span>
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="步骤数">{testCase.steps?.length || 0}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDate(testCase.created_at)}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{formatDate(testCase.updated_at)}</Descriptions.Item>
          <Descriptions.Item label="标签" span={2}>
            {testCase.tags && testCase.tags.length > 0 ? (
              testCase.tags.map((tag: any) => (
                <Tag key={tag.id} color={tag.color || 'default'}>
                  {tag.name}
                </Tag>
              ))
            ) : '-'}
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
          {testCase.steps && testCase.steps.length > 0 ? (
            <Steps
              direction="vertical"
              current={testCase.steps.length}
              items={testCase.steps.map((step: any) => ({
                title: `步骤 ${step.step_order}`,
                description: (
                  <div className="mt-2">
                    <div className="mb-2">
                      <span className="font-medium">操作：</span>
                      <span className="text-gray-700">{step.description}</span>
                    </div>
                    {step.test_data && (
                      <div className="mb-2">
                        <span className="font-medium">测试数据：</span>
                        <span className="text-gray-700">{step.test_data}</span>
                      </div>
                    )}
                    {step.expected && (
                      <div className="mb-2">
                        <span className="font-medium">预期结果：</span>
                        <span className="text-gray-700">{step.expected}</span>
                      </div>
                    )}
                    {step.screenshots && step.screenshots.length > 0 && (
                      <div className="flex gap-2 flex-wrap mt-2">
                        <Image.PreviewGroup>
                          {step.screenshots.map((screenshot: string, idx: number) => (
                            <Image
                              key={idx}
                              width={100}
                              height={100}
                              src={screenshot}
                              alt={`步骤 ${step.step_order} 截图 ${idx + 1}`}
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
          ) : (
            <div className="text-center text-gray-400 py-4">暂无测试步骤</div>
          )}
        </div>

        {/* 预期结果 */}
        <div>
          <h3 className="text-lg font-bold mb-3">预期结果</h3>
          <div className="bg-green-50 border border-green-200 rounded p-4">
            <p className="text-gray-700">{testCase.expected_result || '-'}</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
