import { Card, Row, Col, Statistic } from 'antd';
import {
  FileTextOutlined,
  CheckSquareOutlined,
  TagOutlined,
  FolderOutlined,
} from '@ant-design/icons';
import ModuleTree from '../../components/ModuleTree';
import { mockModules, mockPRDs, mockTestCases, mockTags } from '../../mock/data';

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">仪表盘</h1>

      <Row gutter={16} className="mb-6">
        <Col span={6}>
          <Card>
            <Statistic
              title="PRD 文档"
              value={mockPRDs.length}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="测试用例"
              value={mockTestCases.length}
              prefix={<CheckSquareOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="标签"
              value={mockTags.length}
              prefix={<TagOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="模块"
              value={mockModules.length}
              prefix={<FolderOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="模块结构" className="mb-6">
        <ModuleTree modules={mockModules} />
      </Card>
    </div>
  );
}
