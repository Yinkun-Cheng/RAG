import { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Select,
  Button,
  Space,
  Spin,
  Alert,
  Collapse,
  Tag,
  List,
  Divider,
  Empty,
  Statistic,
  Row,
  Col,
  message,
} from 'antd';
import {
  ThunderboltOutlined,
  FileTextOutlined,
  CheckSquareOutlined,
  ExclamationCircleOutlined,
  DownloadOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { mockAppVersions, mockModules } from '../../mock/data';

const { Panel } = Collapse;

interface ImpactAnalysisResult {
  overall_impact: 'high' | 'medium' | 'low';
  impact_summary: string;
  prd_changes: {
    added: number;
    modified: number;
    deleted: number;
  };
  testcase_impact: {
    need_create: number;
    need_update: number;
    need_deprecate: number;
  };
  details: Array<{
    prd_id: string;
    prd_title: string;
    change_type: 'added' | 'modified' | 'deleted';
    change_description: string;
    impact_level: 'high' | 'medium' | 'low';
    affected_testcases: Array<{
      testcase_id: string | null;
      testcase_title: string;
      action: 'update' | 'create' | 'deprecate' | 'keep';
      reason: string;
      suggestions: string[];
    }>;
  }>;
}

export default function ImpactAnalysis() {
  const { projectId } = useParams<{ projectId: string }>();
  const [baseVersion, setBaseVersion] = useState<string>('');
  const [compareVersion, setCompareVersion] = useState<string>('');
  const [moduleId, setModuleId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImpactAnalysisResult | null>(null);

  const projectVersions = mockAppVersions.filter(v => v.projectId === projectId);

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const modules: { id: string; name: string }[] = [{ id: '', name: '全部模块' }];
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

  // Mock 分析结果
  const mockAnalysisResult: ImpactAnalysisResult = {
    overall_impact: 'high',
    impact_summary:
      '从 v1.0.0 到 v1.1.0 版本，共有 2 个 PRD 新增，3 个 PRD 修改。这些变更会影响 8 个现有测试用例需要更新，建议新增 5 个测试用例，2 个测试用例需要废弃。',
    prd_changes: {
      added: 2,
      modified: 3,
      deleted: 0,
    },
    testcase_impact: {
      need_create: 5,
      need_update: 8,
      need_deprecate: 2,
    },
    details: [
      {
        prd_id: 'prd-2',
        prd_title: '用户登录功能需求文档',
        change_type: 'modified',
        change_description: '新增短信验证码登录方式',
        impact_level: 'high',
        affected_testcases: [
          {
            testcase_id: 'tc-2',
            testcase_title: '用户登录-密码错误',
            action: 'update',
            reason:
              '新增了短信验证码登录方式后，登录流程发生变化。原测试用例只覆盖了密码登录，需要补充短信登录的错误场景。',
            suggestions: [
              '在测试步骤中增加"选择登录方式"步骤',
              '新增短信验证码错误的测试场景',
              '更新预期结果，区分密码错误和验证码错误的提示',
            ],
          },
          {
            testcase_id: 'tc-1',
            testcase_title: '用户登录-正常流程',
            action: 'update',
            reason: '需要明确测试的是密码登录还是短信登录，避免测试覆盖不全。',
            suggestions: [
              '将测试用例拆分为"密码登录-正常流程"和"短信登录-正常流程"',
              '或者在测试步骤中明确测试两种登录方式',
            ],
          },
          {
            testcase_id: null,
            testcase_title: '用户登录-短信验证码登录成功',
            action: 'create',
            reason: '新增了短信验证码登录功能，需要测试正常流程',
            suggestions: [
              '测试场景：输入正确的手机号',
              '测试场景：获取验证码',
              '测试场景：输入正确的验证码',
              '测试场景：登录成功',
            ],
          },
          {
            testcase_id: null,
            testcase_title: '用户登录-验证码过期',
            action: 'create',
            reason: '验证码有时效性，需要测试过期场景',
            suggestions: [
              '测试场景：获取验证码',
              '测试场景：等待验证码过期（通常5分钟）',
              '测试场景：输入过期的验证码',
              '测试场景：提示验证码已过期',
            ],
          },
        ],
      },
      {
        prd_id: 'prd-4',
        prd_title: '订单支付流程优化',
        change_type: 'added',
        change_description: '新增异步支付回调处理和支付状态缓存',
        impact_level: 'medium',
        affected_testcases: [
          {
            testcase_id: null,
            testcase_title: '订单支付-异步回调测试',
            action: 'create',
            reason: '新增了异步支付回调功能，需要测试回调处理逻辑',
            suggestions: [
              '测试场景：模拟支付成功回调',
              '测试场景：模拟支付失败回调',
              '测试场景：测试回调超时处理',
            ],
          },
          {
            testcase_id: 'tc-3',
            testcase_title: '订单创建-正常流程',
            action: 'update',
            reason: '支付流程优化后，需要验证订单创建到支付的完整流程',
            suggestions: ['增加支付状态缓存的验证步骤', '验证异步回调后订单状态更新'],
          },
        ],
      },
    ],
  };

  const handleAnalyze = async () => {
    if (!baseVersion || !compareVersion) {
      message.warning('请选择基准版本和对比版本');
      return;
    }

    if (baseVersion === compareVersion) {
      message.warning('基准版本和对比版本不能相同');
      return;
    }

    setLoading(true);

    // 模拟 API 调用
    setTimeout(() => {
      setResult(mockAnalysisResult);
      setLoading(false);
      message.success('分析完成');
    }, 2000);
  };

  const handleReset = () => {
    setBaseVersion('');
    setCompareVersion('');
    setModuleId('');
    setResult(null);
  };

  const handleExport = () => {
    message.info('导出功能开发中...');
  };

  const getImpactLevelConfig = (level: 'high' | 'medium' | 'low') => {
    const config = {
      high: { text: '高影响', color: 'red', icon: '🔴' },
      medium: { text: '中影响', color: 'orange', icon: '🟡' },
      low: { text: '低影响', color: 'blue', icon: '🟢' },
    };
    return config[level];
  };

  const getActionConfig = (action: string) => {
    const config = {
      update: { text: '需要更新', color: 'orange' },
      create: { text: '建议新增', color: 'green' },
      deprecate: { text: '建议废弃', color: 'red' },
      keep: { text: '保持不变', color: 'default' },
    };
    return config[action as keyof typeof config] || config.keep;
  };

  const getChangeTypeConfig = (type: string) => {
    const config = {
      added: { text: '新增', color: 'green' },
      modified: { text: '修改', color: 'blue' },
      deleted: { text: '删除', color: 'red' },
    };
    return config[type as keyof typeof config];
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ThunderboltOutlined />
          影响分析
        </h1>
        <p className="text-gray-500 mt-1">
          基于 AI 的版本对比影响分析，帮助您评估 PRD 变更对测试用例的影响
        </p>
      </div>

      {/* 版本选择区域 */}
      <Card className="mb-6">
        <div className="mb-4">
          <h3 className="text-lg font-bold mb-3">📊 版本对比设置</h3>
        </div>

        <Row gutter={16}>
          <Col span={8}>
            <div className="mb-2 font-medium">选择基准版本：</div>
            <Select
              placeholder="请选择基准版本"
              value={baseVersion}
              onChange={setBaseVersion}
              style={{ width: '100%' }}
              size="large"
              options={projectVersions.map(v => ({
                label: `${v.version} - ${v.description}`,
                value: v.id,
              }))}
            />
          </Col>

          <Col span={8}>
            <div className="mb-2 font-medium">选择对比版本：</div>
            <Select
              placeholder="请选择对比版本"
              value={compareVersion}
              onChange={setCompareVersion}
              style={{ width: '100%' }}
              size="large"
              options={projectVersions.map(v => ({
                label: `${v.version} - ${v.description}`,
                value: v.id,
              }))}
            />
          </Col>

          <Col span={8}>
            <div className="mb-2 font-medium">选择模块（可选）：</div>
            <Select
              placeholder="全部模块"
              value={moduleId}
              onChange={setModuleId}
              style={{ width: '100%' }}
              size="large"
              options={allModules.map(m => ({ label: m.name, value: m.id }))}
            />
          </Col>
        </Row>

        <div className="mt-6 flex justify-center gap-3">
          <Button
            type="primary"
            size="large"
            icon={<ThunderboltOutlined />}
            onClick={handleAnalyze}
            loading={loading}
          >
            开始分析
          </Button>
          <Button size="large" icon={<ReloadOutlined />} onClick={handleReset}>
            重置
          </Button>
        </div>
      </Card>

      {/* 加载状态 */}
      {loading && (
        <Card>
          <div className="text-center py-12">
            <Spin size="large" />
            <p className="mt-4 text-gray-500">AI 正在分析中，请稍候...</p>
            <p className="text-sm text-gray-400 mt-2">
              正在对比版本差异、检索相关测试用例、生成影响分析报告
            </p>
          </div>
        </Card>
      )}

      {/* 分析结果 */}
      {!loading && result && (
        <>
          {/* 整体摘要 */}
          <Card className="mb-6">
            <div className="mb-4 flex justify-between items-center">
              <h3 className="text-lg font-bold">📈 分析结果摘要</h3>
              <Button icon={<DownloadOutlined />} onClick={handleExport}>
                导出报告
              </Button>
            </div>

            <Alert
              message={
                <span className="font-medium">
                  整体影响程度：
                  {getImpactLevelConfig(result.overall_impact).icon}{' '}
                  {getImpactLevelConfig(result.overall_impact).text}
                </span>
              }
              description={result.impact_summary}
              type={
                result.overall_impact === 'high'
                  ? 'error'
                  : result.overall_impact === 'medium'
                  ? 'warning'
                  : 'info'
              }
              showIcon
              className="mb-4"
            />

            <Row gutter={16}>
              <Col span={12}>
                <Card size="small" className="bg-blue-50">
                  <Statistic
                    title={
                      <span className="flex items-center gap-2">
                        <FileTextOutlined /> PRD 变更统计
                      </span>
                    }
                    value={
                      result.prd_changes.added +
                      result.prd_changes.modified +
                      result.prd_changes.deleted
                    }
                    suffix="个"
                  />
                  <div className="mt-3 text-sm space-y-1">
                    <div>
                      <Tag color="green">新增 {result.prd_changes.added}</Tag>
                      <Tag color="blue">修改 {result.prd_changes.modified}</Tag>
                      <Tag color="red">删除 {result.prd_changes.deleted}</Tag>
                    </div>
                  </div>
                </Card>
              </Col>

              <Col span={12}>
                <Card size="small" className="bg-green-50">
                  <Statistic
                    title={
                      <span className="flex items-center gap-2">
                        <CheckSquareOutlined /> 测试用例影响统计
                      </span>
                    }
                    value={
                      result.testcase_impact.need_create +
                      result.testcase_impact.need_update +
                      result.testcase_impact.need_deprecate
                    }
                    suffix="个"
                  />
                  <div className="mt-3 text-sm space-y-1">
                    <div>
                      <Tag color="green">需要新增 {result.testcase_impact.need_create}</Tag>
                      <Tag color="orange">需要更新 {result.testcase_impact.need_update}</Tag>
                      <Tag color="red">需要废弃 {result.testcase_impact.need_deprecate}</Tag>
                    </div>
                  </div>
                </Card>
              </Col>
            </Row>
          </Card>

          {/* 详细影响列表 */}
          <Card>
            <h3 className="text-lg font-bold mb-4">📋 详细影响列表</h3>

            {result.details.length === 0 ? (
              <Empty description="未发现影响" />
            ) : (
              <Collapse defaultActiveKey={result.details.map((_, i) => i.toString())}>
                {result.details.map((detail, index) => {
                  const impactConfig = getImpactLevelConfig(detail.impact_level);
                  const changeConfig = getChangeTypeConfig(detail.change_type);

                  return (
                    <Panel
                      key={index.toString()}
                      header={
                        <div className="flex items-center justify-between">
                          <span className="font-medium">
                            {impactConfig.icon} {detail.prd_title}
                          </span>
                          <Space>
                            <Tag color={changeConfig.color}>{changeConfig.text}</Tag>
                            <Tag color={impactConfig.color}>{impactConfig.text}</Tag>
                          </Space>
                        </div>
                      }
                    >
                      <div className="space-y-4">
                        {/* PRD 变更描述 */}
                        <div className="bg-blue-50 p-3 rounded">
                          <div className="font-medium mb-2">变更内容：</div>
                          <div className="text-gray-700">{detail.change_description}</div>
                        </div>

                        <Divider />

                        {/* 受影响的测试用例 */}
                        <div>
                          <div className="font-medium mb-3">
                            影响的测试用例 ({detail.affected_testcases.length})：
                          </div>

                          <List
                            dataSource={detail.affected_testcases}
                            renderItem={tc => {
                              const actionConfig = getActionConfig(tc.action);
                              return (
                                <List.Item className="border rounded p-4 mb-3 bg-gray-50">
                                  <div className="w-full">
                                    <div className="flex items-center justify-between mb-2">
                                      <span className="font-medium text-base">
                                        {tc.testcase_title}
                                      </span>
                                      <Tag color={actionConfig.color}>{actionConfig.text}</Tag>
                                    </div>

                                    <div className="mb-3">
                                      <div className="text-sm text-gray-500 mb-1">
                                        <ExclamationCircleOutlined /> 影响原因：
                                      </div>
                                      <div className="text-gray-700">{tc.reason}</div>
                                    </div>

                                    {tc.suggestions.length > 0 && (
                                      <div>
                                        <div className="text-sm text-gray-500 mb-1">
                                          💡 AI 建议：
                                        </div>
                                        <ul className="list-disc list-inside space-y-1 text-gray-700">
                                          {tc.suggestions.map((suggestion, idx) => (
                                            <li key={idx} className="text-sm">
                                              {suggestion}
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}

                                    <div className="mt-3 flex gap-2">
                                      {tc.testcase_id ? (
                                        <>
                                          <Button
                                            type="link"
                                            size="small"
                                            onClick={() =>
                                              (window.location.href = `/project/${projectId}/testcase/${tc.testcase_id}`)
                                            }
                                          >
                                            查看测试用例
                                          </Button>
                                          {tc.action === 'update' && (
                                            <Button
                                              type="link"
                                              size="small"
                                              onClick={() =>
                                                (window.location.href = `/project/${projectId}/testcase/${tc.testcase_id}/edit`)
                                              }
                                            >
                                              立即更新
                                            </Button>
                                          )}
                                        </>
                                      ) : (
                                        <Button
                                          type="link"
                                          size="small"
                                          onClick={() =>
                                            (window.location.href = `/project/${projectId}/testcase/new`)
                                          }
                                        >
                                          创建测试用例
                                        </Button>
                                      )}
                                    </div>
                                  </div>
                                </List.Item>
                              );
                            }}
                          />
                        </div>
                      </div>
                    </Panel>
                  );
                })}
              </Collapse>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
