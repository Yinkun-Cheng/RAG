import { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Button,
  Tabs,
  Switch,
  InputNumber,
  message,
  Divider,
  Alert,
  Space,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';

const { TabPane } = Tabs;
const { TextArea } = Input;

export default function Settings() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<{
    weaviate?: 'success' | 'error';
    embedding?: 'success' | 'error';
  }>({});

  // 测试 Weaviate 连接
  const testWeaviateConnection = async () => {
    setTestingConnection(true);
    try {
      // 模拟测试连接
      await new Promise(resolve => setTimeout(resolve, 1000));
      setConnectionStatus({ ...connectionStatus, weaviate: 'success' });
      message.success('Weaviate 连接成功');
    } catch (error) {
      setConnectionStatus({ ...connectionStatus, weaviate: 'error' });
      message.error('Weaviate 连接失败');
    } finally {
      setTestingConnection(false);
    }
  };

  // 测试 Embedding 模型
  const testEmbeddingModel = async () => {
    setTestingConnection(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      setConnectionStatus({ ...connectionStatus, embedding: 'success' });
      message.success('Embedding 模型连接成功');
    } catch (error) {
      setConnectionStatus({ ...connectionStatus, embedding: 'error' });
      message.error('Embedding 模型连接失败');
    } finally {
      setTestingConnection(false);
    }
  };

  // 保存配置
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // 模拟保存
      setTimeout(() => {
        setLoading(false);
        message.success('配置保存成功');
      }, 1000);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">系统配置</h1>
        <Space>
          <Button icon={<ReloadOutlined />}>重置</Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSave}
            loading={loading}
          >
            保存配置
          </Button>
        </Space>
      </div>

      <Tabs defaultActiveKey="weaviate">
        {/* LLM 大模型配置 */}
        <TabPane tab="LLM 大模型" key="llm">
          <Card>
            <Alert
              message="LLM 大模型配置"
              description="配置用于影响分析、智能推荐等功能的 LLM 大模型，支持 OpenAI、Claude、本地模型等"
              type="info"
              showIcon
              className="mb-6"
            />

            <Form form={form} layout="vertical">
              <Form.Item
                name="llm_provider"
                label="模型提供商"
                rules={[{ required: true, message: '请选择模型提供商' }]}
                initialValue="claude"
              >
                <Select>
                  <Select.Option value="openai">OpenAI</Select.Option>
                  <Select.Option value="claude">Claude (Anthropic)</Select.Option>
                  <Select.Option value="azure">Azure OpenAI</Select.Option>
                  <Select.Option value="local">本地模型 (Ollama)</Select.Option>
                  <Select.Option value="custom">自定义 API</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="llm_model"
                label="模型名称"
                rules={[{ required: true, message: '请输入模型名称' }]}
                initialValue="claude-3-5-sonnet-20241022"
                tooltip="推荐使用 Claude 3.5 Sonnet 或 GPT-4 Turbo"
              >
                <Input placeholder="例如: claude-3-5-sonnet-20241022 或 gpt-4-turbo" />
              </Form.Item>

              <Form.Item
                name="llm_api_key"
                label="API Key"
                rules={[{ required: true, message: '请输入 API Key' }]}
              >
                <Input.Password placeholder="请输入 API Key" />
              </Form.Item>

              <Form.Item name="llm_api_base" label="API Base URL（可选）">
                <Input placeholder="例如: https://api.anthropic.com 或 https://api.openai.com/v1" />
              </Form.Item>

              <Form.Item
                name="llm_temperature"
                label="Temperature（温度）"
                initialValue={0.3}
                tooltip="控制输出的随机性，0-1 之间。影响分析建议使用较低的温度（0.3）以保证输出稳定"
              >
                <InputNumber min={0} max={1} step={0.1} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="llm_max_tokens"
                label="Max Tokens（最大令牌数）"
                initialValue={4000}
                tooltip="单次请求的最大令牌数，影响分析建议 4000 以上"
              >
                <InputNumber min={1000} max={8000} step={1000} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    onClick={testEmbeddingModel}
                    loading={testingConnection}
                    icon={
                      connectionStatus.embedding === 'success' ? (
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      ) : connectionStatus.embedding === 'error' ? (
                        <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                      ) : undefined
                    }
                  >
                    测试 LLM 连接
                  </Button>
                  {connectionStatus.embedding === 'success' && (
                    <span className="text-green-600">LLM 可用</span>
                  )}
                  {connectionStatus.embedding === 'error' && (
                    <span className="text-red-600">LLM 不可用</span>
                  )}
                </Space>
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">使用场景配置</h3>

              <Form.Item
                name="llm_enable_impact_analysis"
                label="启用影响分析"
                valuePropName="checked"
                initialValue={true}
                tooltip="使用 LLM 分析 PRD 变更对测试用例的影响"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="llm_enable_recommendation"
                label="启用智能推荐"
                valuePropName="checked"
                initialValue={true}
                tooltip="使用 LLM 推荐相关的 PRD 和测试用例"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="llm_enable_test_generation"
                label="启用测试用例生成建议"
                valuePropName="checked"
                initialValue={true}
                tooltip="使用 LLM 根据 PRD 生成测试用例建议"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">成本控制</h3>

              <Form.Item
                name="llm_cache_enabled"
                label="启用结果缓存"
                valuePropName="checked"
                initialValue={true}
                tooltip="缓存 LLM 分析结果，减少重复调用，降低成本"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="llm_cache_ttl"
                label="缓存过期时间（小时）"
                initialValue={24}
                tooltip="缓存结果的有效期，过期后重新调用 LLM"
              >
                <InputNumber min={1} max={168} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="llm_rate_limit"
                label="调用频率限制（次/分钟）"
                initialValue={10}
                tooltip="限制 LLM 调用频率，避免超出 API 限额"
              >
                <InputNumber min={1} max={60} style={{ width: '100%' }} />
              </Form.Item>

              <Divider />

              <Alert
                message="模型推荐"
                description={
                  <div className="mt-2">
                    <p className="mb-2">
                      <strong>Claude 3.5 Sonnet（推荐）</strong>：理解能力强，输出稳定，适合影响分析
                    </p>
                    <p className="mb-2">
                      <strong>GPT-4 Turbo</strong>：也很好，但成本稍高
                    </p>
                    <p className="mb-2">
                      <strong>本地模型（Ollama）</strong>：如果有隐私要求，可以使用 Llama 3 等本地模型
                    </p>
                    <p className="text-sm text-gray-500 mt-3">
                      💡 提示：影响分析建议使用 Temperature=0.3，保证输出稳定性
                    </p>
                  </div>
                }
                type="success"
              />
            </Form>
          </Card>
        </TabPane>

        {/* Weaviate 配置 */}
        <TabPane tab="向量数据库" key="weaviate">
          <Card>
            <Alert
              message="Weaviate 配置"
              description="配置 Weaviate 向量数据库连接，用于存储和检索向量化的测试知识"
              type="info"
              showIcon
              className="mb-6"
            />

            <Form form={form} layout="vertical">
              <Form.Item
                name="weaviate_host"
                label="Weaviate 地址"
                rules={[{ required: true, message: '请输入 Weaviate 地址' }]}
                initialValue="localhost"
              >
                <Input placeholder="例如: localhost 或 weaviate.example.com" />
              </Form.Item>

              <Form.Item
                name="weaviate_port"
                label="端口"
                rules={[{ required: true, message: '请输入端口' }]}
                initialValue={8080}
              >
                <InputNumber min={1} max={65535} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="weaviate_scheme"
                label="协议"
                rules={[{ required: true, message: '请选择协议' }]}
                initialValue="http"
              >
                <Select>
                  <Select.Option value="http">HTTP</Select.Option>
                  <Select.Option value="https">HTTPS</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item name="weaviate_api_key" label="API Key（可选）">
                <Input.Password placeholder="如果 Weaviate 需要认证，请输入 API Key" />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    onClick={testWeaviateConnection}
                    loading={testingConnection}
                    icon={
                      connectionStatus.weaviate === 'success' ? (
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      ) : connectionStatus.weaviate === 'error' ? (
                        <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                      ) : undefined
                    }
                  >
                    测试连接
                  </Button>
                  {connectionStatus.weaviate === 'success' && (
                    <span className="text-green-600">连接成功</span>
                  )}
                  {connectionStatus.weaviate === 'error' && (
                    <span className="text-red-600">连接失败</span>
                  )}
                </Space>
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">Collection 配置</h3>

              <Form.Item
                name="prd_collection_name"
                label="PRD Collection 名称"
                initialValue="PRDDocuments"
              >
                <Input placeholder="PRD 文档的 Collection 名称" />
              </Form.Item>

              <Form.Item
                name="testcase_collection_name"
                label="TestCase Collection 名称"
                initialValue="TestCases"
              >
                <Input placeholder="测试用例的 Collection 名称" />
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        {/* Embedding 模型配置 */}
        <TabPane tab="向量化模型" key="embedding">
          <Card>
            <Alert
              message="Embedding 模型配置"
              description="配置用于文本向量化的 Embedding 模型，支持 OpenAI、Claude、本地模型等"
              type="info"
              showIcon
              className="mb-6"
            />

            <Form form={form} layout="vertical">
              <Form.Item
                name="embedding_provider"
                label="模型提供商"
                rules={[{ required: true, message: '请选择模型提供商' }]}
                initialValue="openai"
              >
                <Select>
                  <Select.Option value="openai">OpenAI</Select.Option>
                  <Select.Option value="claude">Claude (Anthropic)</Select.Option>
                  <Select.Option value="azure">Azure OpenAI</Select.Option>
                  <Select.Option value="local">本地模型</Select.Option>
                  <Select.Option value="custom">自定义 API</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="embedding_model"
                label="模型名称"
                rules={[{ required: true, message: '请输入模型名称' }]}
                initialValue="text-embedding-3-small"
              >
                <Input placeholder="例如: text-embedding-3-small" />
              </Form.Item>

              <Form.Item
                name="embedding_api_key"
                label="API Key"
                rules={[{ required: true, message: '请输入 API Key' }]}
              >
                <Input.Password placeholder="请输入 API Key" />
              </Form.Item>

              <Form.Item name="embedding_api_base" label="API Base URL（可选）">
                <Input placeholder="例如: https://api.openai.com/v1" />
              </Form.Item>

              <Form.Item
                name="embedding_dimension"
                label="向量维度"
                initialValue={1536}
              >
                <InputNumber min={128} max={4096} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item>
                <Space>
                  <Button
                    onClick={testEmbeddingModel}
                    loading={testingConnection}
                    icon={
                      connectionStatus.embedding === 'success' ? (
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      ) : connectionStatus.embedding === 'error' ? (
                        <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                      ) : undefined
                    }
                  >
                    测试模型
                  </Button>
                  {connectionStatus.embedding === 'success' && (
                    <span className="text-green-600">模型可用</span>
                  )}
                  {connectionStatus.embedding === 'error' && (
                    <span className="text-red-600">模型不可用</span>
                  )}
                </Space>
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">向量化配置</h3>

              <Form.Item
                name="chunk_size"
                label="分段大小（字符数）"
                initialValue={500}
                tooltip="长文档会被分成多个段落进行向量化"
              >
                <InputNumber min={100} max={2000} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="chunk_overlap"
                label="分段重叠（字符数）"
                initialValue={50}
                tooltip="相邻段落之间的重叠部分，避免语义被截断"
              >
                <InputNumber min={0} max={500} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="auto_sync"
                label="自动同步"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Form>
          </Card>
        </TabPane>

        {/* Dify 集成配置 */}
        <TabPane tab="Dify 集成" key="dify">
          <Card>
            <Alert
              message="Dify 外部知识库配置"
              description="配置 Dify 外部知识库 API，让 Dify Agent 可以调用本系统的测试知识"
              type="info"
              showIcon
              className="mb-6"
            />

            <Form form={form} layout="vertical">
              <Form.Item
                name="dify_enabled"
                label="启用 Dify 集成"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="dify_api_endpoint"
                label="API 端点"
                tooltip="Dify 将调用这个地址来检索测试知识"
              >
                <Input
                  disabled
                  value="http://localhost:8080/api/v1/dify/retrieval"
                  addonAfter={
                    <Button
                      type="link"
                      size="small"
                      onClick={() => {
                        navigator.clipboard.writeText(
                          'http://localhost:8080/api/v1/dify/retrieval'
                        );
                        message.success('已复制到剪贴板');
                      }}
                    >
                      复制
                    </Button>
                  }
                />
              </Form.Item>

              <Form.Item name="dify_api_key" label="API Key（可选）">
                <Input.Password placeholder="如果需要认证，请输入 API Key" />
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">检索配置</h3>

              <Form.Item
                name="dify_top_k"
                label="默认返回数量（top_k）"
                initialValue={5}
                tooltip="每次检索默认返回的结果数量"
              >
                <InputNumber min={1} max={20} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="dify_score_threshold"
                label="相似度阈值"
                initialValue={0.7}
                tooltip="只返回相似度大于此阈值的结果"
              >
                <InputNumber min={0} max={1} step={0.1} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="dify_include_metadata"
                label="包含元数据"
                valuePropName="checked"
                initialValue={true}
                tooltip="返回结果中包含测试用例的元数据（优先级、类型、模块等）"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">配置说明</h3>
              <Alert
                message="如何在 Dify 中配置"
                description={
                  <div className="mt-2">
                    <p className="mb-2">1. 在 Dify 中创建知识库</p>
                    <p className="mb-2">2. 选择"外部知识库"类型</p>
                    <p className="mb-2">
                      3. 填入 API 端点：http://localhost:8080/api/v1/dify/retrieval
                    </p>
                    <p className="mb-2">4. 如果设置了 API Key，填入认证信息</p>
                    <p>5. 保存配置，即可在 Agent 中使用</p>
                  </div>
                }
                type="success"
              />
            </Form>
          </Card>
        </TabPane>

        {/* 高级配置 */}
        <TabPane tab="高级配置" key="advanced">
          <Card>
            <Form form={form} layout="vertical">
              <h3 className="text-lg font-bold mb-4">性能配置</h3>

              <Form.Item
                name="batch_size"
                label="批量处理大小"
                initialValue={100}
                tooltip="批量向量化时，每批处理的文档数量"
              >
                <InputNumber min={10} max={1000} style={{ width: '100%' }} />
              </Form.Item>

              <Form.Item
                name="cache_enabled"
                label="启用缓存"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                name="cache_ttl"
                label="缓存过期时间（秒）"
                initialValue={3600}
              >
                <InputNumber min={60} max={86400} style={{ width: '100%' }} />
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">日志配置</h3>

              <Form.Item name="log_level" label="日志级别" initialValue="info">
                <Select>
                  <Select.Option value="debug">Debug</Select.Option>
                  <Select.Option value="info">Info</Select.Option>
                  <Select.Option value="warn">Warn</Select.Option>
                  <Select.Option value="error">Error</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="log_api_calls"
                label="记录 API 调用"
                valuePropName="checked"
                initialValue={false}
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>

              <Divider />

              <h3 className="text-lg font-bold mb-4">数据同步</h3>

              <Form.Item label="手动同步">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Button block>同步所有 PRD 到 Weaviate</Button>
                  <Button block>同步所有测试用例到 Weaviate</Button>
                  <Button block danger>
                    清空 Weaviate 数据
                  </Button>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
}
