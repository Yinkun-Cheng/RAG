import { useState } from 'react';
import { Card, Button, Modal, Form, Input, Empty, Row, Col, Statistic } from 'antd';
import {
  PlusOutlined,
  FolderOpenOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
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

  // 计算统计数据
  const totalProjects = projects.length;
  const totalPRDs = projects.reduce((sum, p) => sum + p.prdCount, 0);
  const totalTestCases = projects.reduce((sum, p) => sum + p.testCaseCount, 0);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">项目列表</h1>
              <p className="text-gray-500">管理你的 PRD 文档和测试用例</p>
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

          {/* 统计数据 */}
          <Row gutter={16}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="总项目数"
                  value={totalProjects}
                  prefix={<FolderOpenOutlined />}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="PRD 文档"
                  value={totalPRDs}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="测试用例"
                  value={totalTestCases}
                  prefix={<CheckCircleOutlined />}
                />
              </Card>
            </Col>
          </Row>
        </div>

        {/* 项目列表 */}
        {projects.length === 0 ? (
          <Card>
            <Empty
              description="暂无项目，点击右上角按钮创建第一个项目"
              className="py-12"
            />
          </Card>
        ) : (
          <Row gutter={[16, 16]}>
            {projects.map(project => (
              <Col key={project.id} xs={24} sm={12} lg={8}>
                <Card
                  hoverable
                  className="border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                  style={{ background: 'linear-gradient(to bottom right, #fafafa, #f5f5f5)' }}
                  title={
                    <div className="flex items-center">
                      <FolderOpenOutlined className="mr-2" />
                      {project.name}
                    </div>
                  }
                  extra={
                    <Button
                      type="link"
                      size="small"
                      onClick={() => handleOpenProject(project.id)}
                    >
                      打开
                    </Button>
                  }
                  actions={[
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
                  <p className="text-gray-600 mb-4 min-h-[40px]">
                    {project.description}
                  </p>
                  <div className="flex justify-between text-sm text-gray-500 mb-2">
                    <span>PRD: {project.prdCount}</span>
                    <span>测试用例: {project.testCaseCount}</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    创建于 {project.createdAt}
                  </div>
                </Card>
              </Col>
            ))}
          </Row>
        )}
      </div>

      {/* 创建/编辑项目 Modal */}
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
        <Form form={form} layout="vertical" className="mt-4">
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
              placeholder="简要描述项目的主要内容和目标"
              rows={4}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
