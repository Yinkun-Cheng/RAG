import { useState } from 'react';
import { Card, Button, Modal, Form, Input, Space, Empty, Row, Col } from 'antd';
import {
  PlusOutlined,
  FolderOpenOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  prdCount: number;
  testCaseCount: number;
}

// Mock 项目数据
const mockProjects: Project[] = [
  {
    id: 'proj-1',
    name: '电商平台',
    description: '电商平台核心功能开发',
    createdAt: '2025-01-01',
    prdCount: 6,
    testCaseCount: 15,
  },
  {
    id: 'proj-2',
    name: '移动支付系统',
    description: '移动支付系统需求与测试管理',
    createdAt: '2025-01-10',
    prdCount: 3,
    testCaseCount: 8,
  },
];

export default function ProjectList() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>(mockProjects);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [form] = Form.useForm();

  const handleCreateOrUpdate = () => {
    form.validateFields().then(values => {
      if (editingProject) {
        // 更新项目
        setProjects(
          projects.map(p =>
            p.id === editingProject.id ? { ...p, ...values } : p
          )
        );
      } else {
        // 创建新项目
        const newProject: Project = {
          id: `proj-${Date.now()}`,
          ...values,
          createdAt: new Date().toISOString().split('T')[0],
          prdCount: 0,
          testCaseCount: 0,
        };
        setProjects([...projects, newProject]);
      }
      setModalVisible(false);
      setEditingProject(null);
      form.resetFields();
    });
  };

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    form.setFieldsValue(project);
    setModalVisible(true);
  };

  const handleDelete = (projectId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '删除项目将同时删除该项目下的所有 PRD 和测试用例，此操作不可恢复。确认删除吗？',
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: () => {
        setProjects(projects.filter(p => p.id !== projectId));
      },
    });
  };

  const handleOpenProject = (projectId: string) => {
    navigate(`/project/${projectId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">项目管理</h1>
            <p className="text-gray-500 mt-2">选择一个项目开始管理 PRD 和测试用例</p>
          </div>
          <Button
            type="primary"
            size="large"
            icon={<PlusOutlined />}
            onClick={() => {
              setEditingProject(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            新建项目
          </Button>
        </div>

        {projects.length === 0 ? (
          <Empty
            description="暂无项目，请创建一个项目开始使用"
            className="mt-20"
          />
        ) : (
          <Row gutter={[24, 24]}>
            {projects.map(project => (
              <Col key={project.id} xs={24} sm={12} lg={8}>
                <Card
                  hoverable
                  className="h-full"
                  actions={[
                    <Button
                      type="text"
                      icon={<FolderOpenOutlined />}
                      onClick={() => handleOpenProject(project.id)}
                    >
                      打开
                    </Button>,
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(project)}
                    >
                      编辑
                    </Button>,
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(project.id)}
                    >
                      删除
                    </Button>,
                  ]}
                >
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {project.name}
                    </h3>
                    <p className="text-gray-500 text-sm">{project.description}</p>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>PRD: {project.prdCount}</span>
                    <span>测试用例: {project.testCaseCount}</span>
                  </div>
                  <div className="mt-2 text-xs text-gray-400">
                    创建于: {project.createdAt}
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        )}

        <Modal
          title={editingProject ? '编辑项目' : '新建项目'}
          open={modalVisible}
          onOk={handleCreateOrUpdate}
          onCancel={() => {
            setModalVisible(false);
            setEditingProject(null);
            form.resetFields();
          }}
          okText="确定"
          cancelText="取消"
        >
          <Form form={form} layout="vertical">
            <Form.Item
              name="name"
              label="项目名称"
              rules={[{ required: true, message: '请输入项目名称' }]}
            >
              <Input placeholder="例如: 电商平台" />
            </Form.Item>
            <Form.Item
              name="description"
              label="项目描述"
              rules={[{ required: true, message: '请输入项目描述' }]}
            >
              <Input.TextArea
                placeholder="简要描述项目的主要内容"
                rows={3}
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
}
