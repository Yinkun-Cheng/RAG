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
import { Module } from '../../mock/data';

interface ModuleTreeProps {
  modules: Module[];
  onModuleChange?: () => void;
}

export default function ModuleTree({ modules, onModuleChange }: ModuleTreeProps) {
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>(['1', '2', '3']);
  const [selectedKeys, setSelectedKeys] = useState<React.Key[]>([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState<'add' | 'edit'>('add');
  const [currentModule, setCurrentModule] = useState<Module | null>(null);
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

  // 右键菜单
  const getContextMenuItems = (node: DataNode) => [
    {
      key: 'add',
      icon: <PlusOutlined />,
      label: '新建子模块',
      onClick: () => {
        setModalType('add');
        setCurrentModule({ id: node.key as string, name: node.title as string } as Module);
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
        setCurrentModule({ id: node.key as string, name: node.title as string } as Module);
        form.setFieldsValue({ name: node.title });
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
          content: `确定要删除模块"${node.title}"吗？`,
          onOk: () => {
            message.success('删除成功');
            onModuleChange?.();
          },
        });
      },
    },
  ];

  const handleOk = () => {
    form.validateFields().then(values => {
      if (modalType === 'add') {
        message.success(`新建子模块"${values.name}"成功`);
      } else {
        message.success(`编辑模块"${values.name}"成功`);
      }
      setModalVisible(false);
      onModuleChange?.();
    });
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
        onCancel={() => setModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="模块名称"
            rules={[{ required: true, message: '请输入模块名称' }]}
          >
            <Input placeholder="请输入模块名称" />
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
