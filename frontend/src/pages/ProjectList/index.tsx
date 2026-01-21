import { useState, useEffect } from 'react';
import { Card, Button, Modal, Form, Input, Empty, Row, Col, Statistic, Spin, message } from 'antd';
import {
  PlusOutlined,
  FolderOpenOutlined,
  EditOutlined,
  DeleteOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api, { Project as APIProject } from '../../api';

interface Project extends APIProject {
  prdCount?: number;
  testCaseCount?: number;
}

export default function ProjectList() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  // 获取项目列表
  const fetchProjects = async () => {
    setLoading(true);
    try {
      const response = await api.project.list();
      setProjects(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      message.error('获取项目列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateOrUpdate = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      if (editingProject) {
        // 更新项目
        await api.project.update(editingProject.id, {
          name: values.name,
          description: values.description,
        });
        message.success('项目更新成功');
      } else {
        // 创建新项目
        await api.project.create({
          name: values.name,
          description: values.description,
        });
        message.success('项目创建成功');
      }

      setModalVisible(false);
      setEditingProject(null);
      form.resetFields();
      fetchProjects(); // 重新获取项目列表
    } catch (error) {
      console.error('Failed to create/update project:', error);
      message.error(editingProject ? '项目更新失败' : '项目创建失败');
    } finally {
      setSubmitting(false);
    }
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
      onOk: async () => {
        try {
          await api.project.delete(projectId);
          message.success('项目删除成功');
          fetchProjects(); // 重新获取项目列表
        } catch (error) {
          console.error('Failed to delete project:', error);
          message.error('项目删除失败');
        }
      },
    });
  };

  const handleOpenProject = (projectId: string) => {
    navigate(`/project/${projectId}`);
  };

  // 计算统计数据
  const totalProjects = projects.length;
  const totalPRDs = projects.reduce((sum, p) => sum + (p.prdCount || 0), 0);
  const totalTestCases = projects.reduce((sum, p) => sum + (p.testCaseCount || 0), 0);

  if (loading) {
    return (
      <div className="p-8 bg-gray-50 min-h-screen flex items-center justify-center">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

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
                    <span>PRD: {project.prdCount || 0}</span>
                    <span>测试用例: {project.testCaseCount || 0}</span>
                  </div>
                  <div className="text-xs text-gray-400">
                    创建于 {new Date(project.created_at).toLocaleDateString('zh-CN')}
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
        confirmLoading={submitting}
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
