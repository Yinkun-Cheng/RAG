import { useState, useEffect } from 'react';
import { Card, Row, Col, Spin, message, Empty } from 'antd';
import { useParams } from 'react-router-dom';
import ModuleTree from '../../components/ModuleTree';
import api, { Module } from '../../api';

export default function ModuleManagement() {
  const { projectId } = useParams<{ projectId: string }>();
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取模块树
  const fetchModules = async () => {
    if (!projectId) {
      message.error('项目 ID 不存在');
      return;
    }

    setLoading(true);
    try {
      const response = await api.module.getTree(projectId);
      setModules(response.data || []);
    } catch (error) {
      console.error('Failed to fetch modules:', error);
      message.error('获取模块列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModules();
  }, [projectId]);

  const handleModuleChange = () => {
    // 重新加载模块数据
    fetchModules();
  };

  if (!projectId) {
    return (
      <div className="p-6">
        <Card>
          <Empty description="项目 ID 不存在，请从项目列表进入" />
        </Card>
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
      <h1 className="text-2xl font-bold mb-6">模块管理</h1>
      
      <Row gutter={16}>
        <Col span={24}>
          <Card 
            title="模块树结构" 
            extra={<span className="text-gray-500">右键点击模块可进行操作</span>}
          >
            {modules.length === 0 ? (
              <Empty 
                description="暂无模块，点击下方按钮创建第一个模块"
                className="py-12"
              />
            ) : (
              <ModuleTree 
                projectId={projectId} 
                modules={modules} 
                onModuleChange={handleModuleChange} 
              />
            )}
          </Card>
        </Col>
      </Row>

      <div className="mt-6 p-4 bg-blue-50 rounded">
        <h3 className="font-bold mb-2">使用说明：</h3>
        <ul className="list-disc list-inside space-y-1 text-gray-700">
          <li>点击"新建根模块"可以创建顶层模块</li>
          <li>右键点击任意模块，可以新建子模块、编辑或删除</li>
          <li>模块结构会自动应用到 PRD 文档和测试用例的分类中</li>
          <li>删除模块前请确保该模块下没有关联的文档或用例</li>
        </ul>
      </div>
    </div>
  );
}
