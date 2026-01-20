import { useState } from 'react';
import { Table, Button, Modal, Form, Input, Select, Tag, Space, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { mockTags, Tag as TagType } from '../../mock/data';

export default function TagManagement() {
  const [tags, setTags] = useState<TagType[]>(mockTags);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'add' | 'edit'>('add');
  const [currentTag, setCurrentTag] = useState<TagType | null>(null);
  const [form] = Form.useForm();

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
      title: '使用次数',
      dataIndex: 'usageCount',
      key: 'usageCount',
      sorter: (a, b) => a.usageCount - b.usageCount,
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
              form.setFieldsValue(record);
              setModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => {
              Modal.confirm({
                title: '确认删除',
                content: `确定要删除标签"${record.name}"吗？`,
                onOk: () => {
                  setTags(tags.filter(t => t.id !== record.id));
                  message.success('删除成功');
                },
              });
            }}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleOk = () => {
    form.validateFields().then(values => {
      if (modalType === 'add') {
        const newTag: TagType = {
          id: String(Date.now()),
          ...values,
          usageCount: 0,
        };
        setTags([...tags, newTag]);
        message.success('新建标签成功');
      } else if (currentTag) {
        setTags(tags.map(t => (t.id === currentTag.id ? { ...t, ...values } : t)));
        message.success('编辑标签成功');
      }
      setModalVisible(false);
      form.resetFields();
    });
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

      <Table columns={columns} dataSource={tags} rowKey="id" />

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
        </Form>
      </Modal>
    </div>
  );
}
