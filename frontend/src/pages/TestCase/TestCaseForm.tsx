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
  Upload,
} from 'antd';
import {
  ArrowLeftOutlined,
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import TagSelect from '../../components/TagSelect';
import {
  mockTestCases,
  mockModules,
  mockTags,
  mockAppVersions,
} from '../../mock/data';

const { TextArea } = Input;

export default function TestCaseForm() {
  const { id, projectId } = useParams<{ id?: string; projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState<
    Array<{ order: number; description: string; screenshots: string[] }>
  >([{ order: 1, description: '', screenshots: [] }]);

  const isEdit = !!id;
  const versionFromUrl = searchParams.get('version');

  useEffect(() => {
    if (isEdit) {
      const testCase = mockTestCases.find(
        tc => tc.id === id && tc.projectId === projectId
      );
      if (testCase) {
        form.setFieldsValue({
          title: testCase.title,
          appVersionId: testCase.appVersionId,
          moduleId: testCase.moduleId,
          priority: testCase.priority,
          type: testCase.type,
          status: testCase.status,
          tags: testCase.tags,
          precondition: testCase.precondition,
          expectedResult: testCase.expectedResult,
        });
        setSteps(testCase.steps);
      }
    } else if (versionFromUrl) {
      form.setFieldValue('appVersionId', versionFromUrl);
    }
  }, [id, isEdit, projectId, versionFromUrl, form]);

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const modules: { id: string; name: string }[] = [];
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
  const projectVersions = mockAppVersions.filter(v => v.projectId === projectId);

  const handleAddStep = () => {
    setSteps([...steps, { order: steps.length + 1, description: '', screenshots: [] }]);
  };

  const handleRemoveStep = (index: number) => {
    const newSteps = steps.filter((_, i) => i !== index);
    // 重新排序
    newSteps.forEach((step, i) => {
      step.order = i + 1;
    });
    setSteps(newSteps);
  };

  const handleStepChange = (index: number, description: string) => {
    const newSteps = [...steps];
    newSteps[index].description = description;
    setSteps(newSteps);
  };

  const handleSave = async () => {
    try {
      await form.validateFields();
      
      // 验证步骤
      if (steps.length === 0 || steps.some(s => !s.description.trim())) {
        message.error('请填写完整的测试步骤');
        return;
      }

      setLoading(true);

      // 模拟保存
      setTimeout(() => {
        setLoading(false);
        message.success(isEdit ? '更新成功' : '创建成功');
        navigate(`/project/${projectId}/testcase`);
      }, 1000);
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
                options={projectVersions.map(v => ({
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
                <Select.Option value="high">高</Select.Option>
                <Select.Option value="medium">中</Select.Option>
                <Select.Option value="low">低</Select.Option>
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
              </Select>
            </Form.Item>
          </div>

          <Form.Item name="tags" label="标签">
            <TagSelect availableTags={mockTags} />
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
                  extra={
                    steps.length > 1 && (
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => handleRemoveStep(index)}
                      >
                        删除
                      </Button>
                    )
                  }
                >
                  <div className="flex-1">
                    <div className="font-medium mb-2">步骤 {step.order}</div>
                    <TextArea
                      value={step.description}
                      onChange={e => handleStepChange(index, e.target.value)}
                      placeholder="请描述测试步骤"
                      rows={2}
                    />
                    <div className="mt-2">
                      <Upload
                        listType="picture-card"
                        maxCount={5}
                        beforeUpload={() => false}
                      >
                        <div>
                          <UploadOutlined />
                          <div className="mt-2">上传截图</div>
                        </div>
                      </Upload>
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
    </div>
  );
}
