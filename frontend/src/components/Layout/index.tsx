import { Layout as AntLayout, Menu } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FileTextOutlined,
  CheckSquareOutlined,
  SearchOutlined,
  ImportOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = AntLayout;

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/prd',
      icon: <FileTextOutlined />,
      label: 'PRD 文档',
    },
    {
      key: '/testcase',
      icon: <CheckSquareOutlined />,
      label: '测试用例',
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '语义搜索',
    },
    {
      key: '/import',
      icon: <ImportOutlined />,
      label: '导入',
    },
  ];

  return (
    <AntLayout className="min-h-screen">
      <Header className="flex items-center bg-white border-b px-6">
        <div className="text-xl font-bold">RAG 测试用例管理系统</div>
      </Header>
      <AntLayout>
        <Sider width={200} className="bg-white">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            className="h-full border-r"
          />
        </Sider>
        <Content className="bg-gray-50">
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
}
