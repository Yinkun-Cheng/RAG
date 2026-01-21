import { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Select, Tag, Space, message, Spin } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import api, { Tag as TagType } from '../../api';

export default function TagManagement() {
  const { projectId } = useParams<{ projectId: string }>();
  const [tags, setTags] = useState<TagType[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'add' | 'edit'>('add');
  const [currentTag, setCurrentTag] = useState<TagType | null>(null);
  const [form] = Form.useForm();

  // 获取标签列表
  useEffect(() => {
    if (projectId) {
      fetchTags();
    }
  }, [projectId]);

  const fetchTags = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const response = await api.tag.list(projectId);
      setTags(response.data || []);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
      message.error('获取标签列表失败');
    } finally {
      setLoading(false);
    }
  };

  const colorOptions = [
    { label: '红色', value: 'red' },
    { label: '橙色', value: 'orange' },
    { label: '蓝色', value: 'blue' },
    { label: '绿色', value: 'green' },
    { label: '紫色', value: 'purple' },
    { label: '火山色', value: 'volcano' },
    { label: '青色', value: 'cyan' },
    { label: '金色', value: 'gold' },
  ];

  const columns: ColumnsType<TagType> = [
    {
      title: '标签名称',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => <Tag color={record.color}>{name}</Tag>,
    },
    {
      title: '颜色',
      dataIndex: 'color',
      key: 'color',
      render: color => colorOptions.find(opt => opt.value === color)?.label || color,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => {
              setModalType('edit');
              setCurrentTag(record);
              form.setFieldsValue({
                name: record.name,
                color: record.color,
                description: record.description,
              });
              setModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleDelete = async (record: TagType) => {
    if (!projectId) return;
    
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除标签"${record.name}"吗？`,
      onOk: async () => {
        try {
          await api.tag.delete(projectId, record.id);
          message.success('删除成功');
          fetchTags();
        } catch (error) {
          console.error('Failed to delete tag:', error);
          message.error('删除失败');
        }
      },
    });
  };

  const handleOk = async () => {
    if (!projectId) return;
    
    try {
      const values = await form.validateFields();
      
      if (modalType === 'add') {
        await api.tag.create(projectId, values);
        message.success('新建标签成功');
      } else if (currentTag) {
        await api.tag.update(projectId, currentTag.id, values);
        message.success('编辑标签成功');
      }
      
      setModalVisible(false);
      form.resetFields();
      fetchTags();
    } catch (error) {
      console.error('Failed to save tag:', error);
      message.error('保存失败');
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">标签管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setModalType('add');
            setCurrentTag(null);
            form.resetFields();
            setModalVisible(true);
          }}
        >
          新建标签
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <Spin size="large" tip="加载中..." />
        </div>
      ) : (
        <Table columns={columns} dataSource={tags} rowKey="id" />
      )}

      <Modal
        title={modalType === 'add' ? '新建标签' : '编辑标签'}
        open={modalVisible}
        onOk={handleOk}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="标签名称"
            rules={[{ required: true, message: '请输入标签名称' }]}
          >
            <Input placeholder="请输入标签名称" />
          </Form.Item>
          <Form.Item
            name="color"
            label="标签颜色"
            rules={[{ required: true, message: '请选择标签颜色' }]}
          >
            <Select
              placeholder="请选择标签颜色"
              options={colorOptions}
              optionRender={option => (
                <Tag color={option.data.value}>{option.data.label}</Tag>
              )}
            />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea placeholder="请输入标签描述" rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
