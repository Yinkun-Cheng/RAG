import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Form,
  Input,
  Select,
  Button,
  Card,
  message,
  Divider,
  List,
  Spin,
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import TagSelect from '../../components/TagSelect';
import api from '../../api';

const { TextArea } = Input;

export default function TestCaseForm() {
  const { id, projectId } = useParams<{ id?: string; projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(false);
  const [steps, setSteps] = useState<
    Array<{ order: number; description: string; testData?: string; expected?: string }>
  >([{ order: 1, description: '', testData: '', expected: '' }]);
  
  // 数据状态
  const [appVersions, setAppVersions] = useState<any[]>([]);
  const [modules, setModules] = useState<any[]>([]);
  const [tags, setTags] = useState<any[]>([]);

  const isEdit = !!id;
  const versionFromUrl = searchParams.get('version');
  const prdFromUrl = searchParams.get('prd');
  
  // 防止重复提示的标志
  const [prdFilled, setPrdFilled] = useState(false);

  // 加载基础数据
  useEffect(() => {
    if (!projectId) return;
    loadData();
  }, [projectId]);

  const loadData = async () => {
    if (!projectId) return;
    
    setDataLoading(true);
    try {
      const [versionRes, moduleRes, tagRes] = await Promise.all([
        api.appVersion.list(projectId),
        api.module.getTree(projectId),
        api.tag.list(projectId),
      ]);

      setAppVersions(versionRes.data || []);
      setModules(moduleRes.data || []);
      setTags(tagRes.data || []);
    } catch (error: any) {
      console.error('Failed to load data:', error);
      message.error(error.message || '加载数据失败');
    } finally {
      setDataLoading(false);
    }
  };

  // 如果有 PRD ID，获取 PRD 详情并自动填充
  useEffect(() => {
    if (prdFromUrl && projectId && !isEdit && !prdFilled) {
      loadPRDAndFillForm();
    }
  }, [prdFromUrl, projectId, isEdit, prdFilled]);

  const loadPRDAndFillForm = async () => {
    if (!prdFromUrl || !projectId || prdFilled) return;
    
    try {
      const prdRes = await api.prd.get(projectId, prdFromUrl);
      const prd = prdRes.data;
      
      // 自动填充 App 版本和所属模块
      form.setFieldsValue({
        appVersionId: prd.app_version_id,
        moduleId: prd.module_id,
      });
      
      setPrdFilled(true); // 标记已填充
      message.success('已自动填充 PRD 的版本和模块信息');
    } catch (error: any) {
      console.error('Failed to load PRD:', error);
      message.error('获取 PRD 信息失败');
    }
  };

  useEffect(() => {
    if (isEdit && id && projectId) {
      loadTestCase();
    } else if (versionFromUrl && !prdFromUrl) {
      // 如果只有版本参数（没有 PRD），则只填充版本
      form.setFieldValue('appVersionId', versionFromUrl);
    }
  }, [id, isEdit, projectId, versionFromUrl, prdFromUrl]);

  const loadTestCase = async () => {
    if (!id || !projectId) return;
    
    setDataLoading(true);
    try {
      const res = await api.testcase.get(projectId, id);
      const testCase = res.data;
      
      form.setFieldsValue({
        title: testCase.title,
        appVersionId: testCase.app_version_id,
        moduleId: testCase.module_id,
        priority: testCase.priority,
        type: testCase.type,
        status: testCase.status,
        tags: testCase.tags?.map((t: any) => t.id) || [],
        precondition: testCase.precondition,
        expectedResult: testCase.expected_result,
      });
      
      if (testCase.steps && testCase.steps.length > 0) {
        setSteps(testCase.steps.map((s: any) => ({
          order: s.step_order,
          description: s.description,
          testData: s.test_data,
          expected: s.expected,
        })));
      }
    } catch (error: any) {
      console.error('Failed to load test case:', error);
      message.error(error.message || '加载测试用例失败');
    } finally {
      setDataLoading(false);
    }
  };

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const result: { id: string; name: string }[] = [];
    const flatten = (items: any[]) => {
      items.forEach(item => {
        result.push({ id: item.id, name: item.name });
        if (item.children) {
          flatten(item.children);
        }
      });
    };
    flatten(modules);
    return result;
  };

  const allModules = getAllModules();

  const handleAddStep = () => {
    setSteps([...steps, { order: steps.length + 1, description: '', testData: '', expected: '' }]);
  };

  const handleRemoveStep = (index: number) => {
    const newSteps = steps.filter((_, i) => i !== index);
    // 重新排序
    newSteps.forEach((step, i) => {
      step.order = i + 1;
    });
    setSteps(newSteps);
  };

  const handleStepChange = (index: number, field: string, value: string) => {
    const newSteps = [...steps];
    (newSteps[index] as any)[field] = value;
    setSteps(newSteps);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      
      // 验证步骤
      if (steps.length === 0 || steps.some(s => !s.description.trim())) {
        message.error('请填写完整的测试步骤');
        return;
      }

      if (!projectId) return;

      setLoading(true);

      try {
        const testCaseData = {
          code: values.code || `TC-${Date.now()}`, // 临时生成编号
          title: values.title,
          prd_id: prdFromUrl || '', // 使用 URL 中的 PRD ID
          module_id: values.moduleId,
          app_version_id: values.appVersionId,
          precondition: values.precondition,
          expected_result: values.expectedResult,
          priority: values.priority,
          type: values.type,
          status: values.status,
          steps: steps.map(s => ({
            step_order: s.order,
            description: s.description,
            test_data: s.testData || '',
            expected: s.expected || '',
          })),
        };

        if (isEdit && id) {
          // 更新时不需要 code 字段
          const { code, ...updateData } = testCaseData;
          await api.testcase.update(projectId, id, {
            ...updateData,
            create_version: false,
          });
          message.success('更新成功');
        } else {
          await api.testcase.create(projectId, testCaseData);
          message.success('创建成功');
        }

        navigate(`/project/${projectId}/testcase`);
      } catch (error: any) {
        console.error('Failed to save test case:', error);
        message.error(error.message || '保存失败');
      } finally {
        setLoading(false);
      }
    } catch (error) {
      console.error('表单验证失败:', error);
    }
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

      {dataLoading ? (
        <div className="flex justify-center items-center py-20">
          <Spin size="large" spinning={dataLoading} tip="加载中...">
            <div style={{ minHeight: 200 }} />
          </Spin>
        </div>
      ) : (
        <Card
          title={isEdit ? '编辑测试用例' : '新建测试用例'}
          extra={
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={loading}
            >
              保存
            </Button>
          }
        >
          <Form form={form} layout="vertical">
            {/* 基本信息 */}
            <Form.Item
              name="title"
              label="用例标题"
              rules={[{ required: true, message: '请输入用例标题' }]}
            >
              <Input placeholder="请输入用例标题" size="large" />
            </Form.Item>

            <div className="grid grid-cols-2 gap-4">
              <Form.Item
                name="appVersionId"
                label="App 版本"
                rules={[{ required: true, message: '请选择 App 版本' }]}
              >
                <Select
                  placeholder="请选择 App 版本"
                  options={appVersions.map(v => ({
                    label: `${v.version} - ${v.description}`,
                    value: v.id,
                  }))}
                />
              </Form.Item>

              <Form.Item
                name="moduleId"
                label="所属模块"
                rules={[{ required: true, message: '请选择所属模块' }]}
              >
                <Select
                  placeholder="请选择所属模块"
                  showSearch
                  optionFilterProp="label"
                  options={allModules.map(m => ({ label: m.name, value: m.id }))}
                />
              </Form.Item>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Form.Item
                name="priority"
                label="优先级"
                rules={[{ required: true, message: '请选择优先级' }]}
              >
                <Select placeholder="请选择优先级">
                  <Select.Option value="P0">P0</Select.Option>
                  <Select.Option value="P1">P1</Select.Option>
                  <Select.Option value="P2">P2</Select.Option>
                  <Select.Option value="P3">P3</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="type"
                label="类型"
                rules={[{ required: true, message: '请选择类型' }]}
              >
                <Select placeholder="请选择类型">
                  <Select.Option value="functional">功能</Select.Option>
                  <Select.Option value="performance">性能</Select.Option>
                  <Select.Option value="security">安全</Select.Option>
                  <Select.Option value="ui">UI</Select.Option>
                </Select>
              </Form.Item>

              <Form.Item
                name="status"
                label="状态"
                rules={[{ required: true, message: '请选择状态' }]}
                initialValue="active"
              >
                <Select placeholder="请选择状态">
                  <Select.Option value="active">有效</Select.Option>
                  <Select.Option value="deprecated">已废弃</Select.Option>
                  <Select.Option value="draft">草稿</Select.Option>
                </Select>
              </Form.Item>
            </div>

            <Form.Item name="tags" label="标签">
              <TagSelect availableTags={tags} />
            </Form.Item>

            <Divider />

            {/* 前置条件 */}
            <Form.Item
              name="precondition"
              label="前置条件"
              rules={[{ required: true, message: '请输入前置条件' }]}
            >
              <TextArea
                placeholder="请描述执行此测试用例前需要满足的条件"
                rows={3}
              />
            </Form.Item>

            {/* 测试步骤 */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-3">
                <label className="font-medium">
                  测试步骤 <span className="text-red-500">*</span>
                </label>
                <Button type="dashed" icon={<PlusOutlined />} onClick={handleAddStep}>
                  添加步骤
                </Button>
              </div>

              <List
                dataSource={steps}
                renderItem={(step, index) => (
                  <List.Item
                    key={index}
                    className="border rounded p-4 mb-3"
                  >
                    <div className="flex-1">
                      <div className="flex justify-between items-center mb-2">
                        <div className="font-medium">步骤 {step.order}</div>
                        {steps.length > 1 && (
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => handleRemoveStep(index)}
                          >
                            删除
                          </Button>
                        )}
                      </div>
                      
                      <div className="mb-3">
                        <label className="text-sm text-gray-600 mb-1 block">操作描述 *</label>
                        <TextArea
                          value={step.description}
                          onChange={e => handleStepChange(index, 'description', e.target.value)}
                          placeholder="请描述测试步骤的操作"
                          rows={2}
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-sm text-gray-600 mb-1 block">测试数据</label>
                          <Input
                            value={step.testData}
                            onChange={e => handleStepChange(index, 'testData', e.target.value)}
                            placeholder="输入测试数据（可选）"
                          />
                        </div>
                        <div>
                          <label className="text-sm text-gray-600 mb-1 block">预期结果</label>
                          <Input
                            value={step.expected}
                            onChange={e => handleStepChange(index, 'expected', e.target.value)}
                            placeholder="该步骤的预期结果（可选）"
                          />
                        </div>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            </div>

            {/* 预期结果 */}
            <Form.Item
              name="expectedResult"
              label="预期结果"
              rules={[{ required: true, message: '请输入预期结果' }]}
            >
              <TextArea
                placeholder="请描述执行测试步骤后的预期结果"
                rows={3}
              />
            </Form.Item>
          </Form>
        </Card>
      )}
    </div>
  );
}
