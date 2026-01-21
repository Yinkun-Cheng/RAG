import { useState } from 'react';
import { Tree, Dropdown, Modal, Form, Input, Button, message } from 'antd';
import type { DataNode, TreeProps } from 'antd/es/tree';
import {
  FolderOutlined,
  FolderOpenOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import api, { Module } from '../../api';

interface ModuleTreeProps {
  projectId: string;
  modules: Module[];
  onModuleChange?: () => void;
}

export default function ModuleTree({ projectId, modules, onModuleChange }: ModuleTreeProps) {
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'add' | 'edit'>('add');
  const [currentModule, setCurrentModule] = useState<Module | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  // 转换模块数据为 Tree 组件需要的格式
  const convertToTreeData = (modules: Module[]): DataNode[] => {
    return modules.map(module => ({
      key: module.id,
      title: module.name,
      icon: expandedKeys.includes(module.id) ? (
        <FolderOpenOutlined />
      ) : (
        <FolderOutlined />
      ),
      children: module.children ? convertToTreeData(module.children) : undefined,
    }));
  };

  const treeData = convertToTreeData(modules);

  const onExpand: TreeProps['onExpand'] = expandedKeys => {
    setExpandedKeys(expandedKeys);
  };

  const onSelect: TreeProps['onSelect'] = selectedKeys => {
    setSelectedKeys(selectedKeys);
  };

  // 查找模块信息
  const findModule = (modules: Module[], id: string): Module | null => {
    for (const module of modules) {
      if (module.id === id) return module;
      if (module.children) {
        const found = findModule(module.children, id);
        if (found) return found;
      }
    }
    return null;
  };

  // 右键菜单
  const getContextMenuItems = (node: DataNode) => {
    const module = findModule(modules, node.key as string);
    
    return [
      {
        key: 'add',
        icon: <PlusOutlined />,
        label: '新建子模块',
        onClick: () => {
          setModalType('add');
          setCurrentModule(module);
          form.resetFields();
          setModalVisible(true);
        },
      },
      {
        key: 'edit',
        icon: <EditOutlined />,
        label: '编辑',
        onClick: () => {
          setModalType('edit');
          setCurrentModule(module);
          form.setFieldsValue({ 
            name: module?.name,
            description: module?.description 
          });
          setModalVisible(true);
        },
      },
      {
        key: 'delete',
        icon: <DeleteOutlined />,
        label: '删除',
        danger: true,
        onClick: () => {
          Modal.confirm({
            title: '确认删除',
            content: `确定要删除模块"${node.title}"吗？此操作不可恢复。`,
            okText: '确认',
            cancelText: '取消',
            okButtonProps: { danger: true },
            onOk: async () => {
              try {
                await api.module.delete(projectId, node.key as string);
                message.success('删除成功');
                onModuleChange?.();
              } catch (error) {
                console.error('Failed to delete module:', error);
                message.error('删除失败');
              }
            },
          });
        },
      },
    ];
  };

  const handleOk = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      if (modalType === 'add') {
        // 创建模块
        await api.module.create(projectId, {
          name: values.name,
          description: values.description || '',
          parent_id: currentModule?.id,
        });
        message.success('创建模块成功');
      } else {
        // 更新模块
        if (currentModule) {
          await api.module.update(projectId, currentModule.id, {
            name: values.name,
            description: values.description || '',
          });
          message.success('更新模块成功');
        }
      }

      setModalVisible(false);
      form.resetFields();
      onModuleChange?.();
    } catch (error) {
      console.error('Failed to save module:', error);
      message.error(modalType === 'add' ? '创建模块失败' : '更新模块失败');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <div className="mb-4">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setModalType('add');
            setCurrentModule(null);
            form.resetFields();
            setModalVisible(true);
          }}
        >
          新建根模块
        </Button>
      </div>

      <Tree
        showIcon
        expandedKeys={expandedKeys}
        selectedKeys={selectedKeys}
        onExpand={onExpand}
        onSelect={onSelect}
        treeData={treeData}
        titleRender={node => (
          <Dropdown menu={{ items: getContextMenuItems(node) }} trigger={['contextMenu']}>
            <span>{node.title as string}</span>
          </Dropdown>
        )}
      />

      <Modal
        title={modalType === 'add' ? '新建模块' : '编辑模块'}
        open={modalVisible}
        onOk={handleOk}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        okText="确定"
        cancelText="取消"
        confirmLoading={submitting}
      >
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item
            name="name"
            label="模块名称"
            rules={[{ required: true, message: '请输入模块名称' }]}
          >
            <Input placeholder="例如: 用户管理" />
          </Form.Item>
          <Form.Item
            name="description"
            label="模块描述"
          >
            <Input.TextArea
              placeholder="简要描述模块的功能"
              rows={3}
            />
          </Form.Item>
          {modalType === 'add' && currentModule && (
            <Form.Item label="父模块">
              <Input value={currentModule.name} disabled />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </>
  );
}
