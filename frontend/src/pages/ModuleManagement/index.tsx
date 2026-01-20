import { useState } from 'react';
import { Card, Row, Col } from 'antd';
import ModuleTree from '../../components/ModuleTree';
import { mockModules } from '../../mock/data';

export default function ModuleManagement() {
  const [modules, setModules] = useState(mockModules);

  const handleModuleChange = () => {
    // 这里可以重新加载模块数据
    console.log('模块数据已更新');
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">模块管理</h1>
      
      <Row gutter={16}>
        <Col span={24}>
          <Card title="模块树结构" extra={<span className="text-gray-500">右键点击模块可进行操作</span>}>
            <ModuleTree modules={modules} onModuleChange={handleModuleChange} />
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
