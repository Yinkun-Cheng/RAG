import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Input, Select, Button, Card, Space, message } from 'antd';
import { ArrowLeftOutlined, SaveOutlined, SendOutlined } from '@ant-design/icons';
import MarkdownEditor from '../../components/MarkdownEditor';
import TagSelect from '../../components/TagSelect';
import { mockPRDs, mockModules, mockTags } from '../../mock/data';

export default function PRDForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const isEdit = !!id;

  useEffect(() => {
    if (isEdit) {
      const prd = mockPRDs.find(p => p.id === id);
      if (prd) {
        form.setFieldsValue({
          title: prd.title,
          moduleId: prd.moduleId,
          tags: prd.tags,
        });
        setContent(prd.content);
      }
    }
  }, [id, isEdit, form]);

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

  const handleSave = async (status: 'draft' | 'published') => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // 模拟保存
      setTimeout(() => {
        setLoading(false);
        message.success(
          status === 'draft' ? '保存草稿成功' : '发布成功'
        );
        navigate('/prd');
      }, 1000);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-4">
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/prd')}>
          返回列表
        </Button>
      </div>

      <Card
        title={isEdit ? '编辑 PRD' : '新建 PRD'}
        extra={
          <Space>
            <Button
              icon={<SaveOutlined />}
              onClick={() => handleSave('draft')}
              loading={loading}
            >
              保存草稿
            </Button>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={() => handleSave('published')}
              loading={loading}
            >
              发布
            </Button>
          </Space>
        }
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="PRD 标题"
            rules={[{ required: true, message: '请输入 PRD 标题' }]}
          >
            <Input placeholder="请输入 PRD 标题" size="large" />
          </Form.Item>

          <Form.Item
            name="moduleId"
            label="所属模块"
            rules={[{ required: true, message: '请选择所属模块' }]}
          >
            <Select
              placeholder="请选择所属模块"
              size="large"
              showSearch
              optionFilterProp="label"
              options={allModules.map(m => ({ label: m.name, value: m.id }))}
            />
          </Form.Item>

          <Form.Item name="tags" label="标签">
            <TagSelect availableTags={mockTags} />
          </Form.Item>

          <Form.Item label="文档内容" required>
            <MarkdownEditor value={content} onChange={setContent} height="600px" />
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
