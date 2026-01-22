import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Form, Input, Select, Button, Card, Space, message, Spin } from 'antd';
import { ArrowLeftOutlined, SaveOutlined, SendOutlined } from '@ant-design/icons';
import MarkdownEditor from '../../components/MarkdownEditor';
import api, { Module, Tag as TagType, AppVersion } from '../../api';

export default function PRDForm() {
  const { id, projectId } = useParams<{ id?: string; projectId: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [modules, setModules] = useState<Module[]>([]);
  const [tags, setTags] = useState<TagType[]>([]);
  const [appVersions, setAppVersions] = useState<AppVersion[]>([]);

  const isEdit = !!id;
  const versionFromUrl = searchParams.get('version'); // 从 URL 获取版本参数

  // 调试：打印 URL 参数
  useEffect(() => {
    console.log('PRDForm - versionFromUrl:', versionFromUrl);
    console.log('PRDForm - searchParams:', Object.fromEntries(searchParams.entries()));
  }, [versionFromUrl, searchParams]);

  useEffect(() => {
    if (projectId) {
      fetchData();
    }
  }, [projectId, id]);

  // 当版本数据加载完成且有 URL 参数时，设置默认值
  useEffect(() => {
    console.log('PRDForm - Setting version:', {
      isEdit,
      versionFromUrl,
      appVersionsLength: appVersions.length,
      appVersions: appVersions.map(v => ({ id: v.id, version: v.version }))
    });
    
    if (!isEdit && versionFromUrl && appVersions.length > 0) {
      console.log('PRDForm - Setting form value to:', versionFromUrl);
      form.setFieldsValue({
        app_version_id: versionFromUrl,
      });
    }
  }, [appVersions, versionFromUrl, isEdit, form]);

  const fetchData = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      // 并行获取模块、标签和版本
      const [modulesRes, tagsRes, versionsRes] = await Promise.all([
        api.module.getTree(projectId),
        api.tag.list(projectId),
        api.appVersion.list(projectId),
      ]);

      setModules(modulesRes.data || []);
      setTags(tagsRes.data || []);
      setAppVersions(versionsRes.data || []);

      // 如果是编辑模式，获取 PRD 详情
      if (isEdit && id) {
        const prdRes = await api.prd.get(projectId, id);
        const prd = prdRes.data;
        
        form.setFieldsValue({
          title: prd.title,
          app_version_id: prd.app_version_id,
          module_id: prd.module_id,
          tag_ids: prd.tags?.map(t => t.id) || [],
        });
        setContent(prd.content);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
      message.error('获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取所有模块（扁平化）
  const getAllModules = () => {
    const modulesList: { id: string; name: string }[] = [];
    const flatten = (items: Module[]) => {
      items.forEach(item => {
        modulesList.push({ id: item.id, name: item.name });
        if (item.children) {
          flatten(item.children);
        }
      });
    };
    flatten(modules);
    return modulesList;
  };

  const allModules = getAllModules();

  const handleSave = async (shouldPublish: boolean) => {
    if (!projectId) return;
    
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      const prdData = {
        code: values.code || `PRD-${Date.now()}`,
        title: values.title,
        version: '1',
        app_version_id: values.app_version_id,
        module_id: values.module_id,
        content: content,
        author: 'Current User', // TODO: 从用户上下文获取
      };

      if (isEdit && id) {
        // 更新 PRD
        await api.prd.update(projectId, id, {
          title: values.title,
          version: '1',
          app_version_id: values.app_version_id,
          module_id: values.module_id,
          content: content,
        });

        // 更新标签
        // TODO: 实现标签的增删逻辑

        if (shouldPublish) {
          await api.prd.publish(projectId, id);
        }

        message.success(shouldPublish ? '更新并发布成功' : '更新成功');
      } else {
        // 创建 PRD
        const createRes = await api.prd.create(projectId, prdData);
        const newPrdId = createRes.data.id;

        // 添加标签
        if (values.tag_ids && values.tag_ids.length > 0) {
          await Promise.all(
            values.tag_ids.map((tagId: string) =>
              api.prd.addTag(projectId, newPrdId, tagId)
            )
          );
        }

        if (shouldPublish) {
          await api.prd.publish(projectId, newPrdId);
        }

        message.success(shouldPublish ? '创建并发布成功' : '创建成功');
      }

      navigate(`/project/${projectId}/prd`);
    } catch (error) {
      console.error('Failed to save PRD:', error);
      message.error('保存失败');
    } finally {
      setSubmitting(false);
    }
  };

  if (!projectId) {
    return (
      <div className="p-6">
        <div className="text-center py-20">
          <p className="text-xl text-gray-500">项目 ID 不存在</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

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
        title={isEdit ? '编辑 PRD' : '新建 PRD'}
        extra={
          <Space>
            <Button
              icon={<SaveOutlined />}
              onClick={() => handleSave(false)}
              loading={submitting}
            >
              保存草稿
            </Button>
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={() => handleSave(true)}
              loading={submitting}
            >
              {isEdit ? '保存并发布' : '创建并发布'}
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
            name="app_version_id"
            label="App 版本"
            rules={[{ required: true, message: '请选择 App 版本' }]}
            tooltip={versionFromUrl ? '版本已自动选择，如需更改请从 PRD 列表页面进入' : undefined}
          >
            <Select
              placeholder="请选择 App 版本"
              size="large"
              disabled={!!versionFromUrl}
              options={appVersions.map(v => ({
                label: `${v.version} - ${v.description}`,
                value: v.id,
              }))}
            />
          </Form.Item>

          <Form.Item
            name="module_id"
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

          <Form.Item name="tag_ids" label="标签">
            <Select
              mode="multiple"
              placeholder="选择标签"
              size="large"
              options={tags.map(t => ({ label: t.name, value: t.id }))}
            />
          </Form.Item>

          <Form.Item label="文档内容" required>
            <MarkdownEditor value={content} onChange={setContent} height="600px" />
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
