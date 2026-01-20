import { Layout as AntLayout, Menu, Button, Breadcrumb } from 'antd';
import { Outlet, useNavigate, useLocation, useParams } from 'react-router-dom';
import {
  DashboardOutlined,
  FileTextOutlined,
  CheckSquareOutlined,
  SearchOutlined,
  ImportOutlined,
  FolderOutlined,
  ArrowLeftOutlined,
  HomeOutlined,
} from '@ant-design/icons';
import { mockProjects } from '../../mock/data';

const { Header, Sider, Content } = AntLayout;

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = useParams<{ projectId: string }>();

  // 获取当前项目信息
  const currentProject = mockProjects.find(p => p.id === projectId);

  const menuItems = [
    {
      key: `/project/${projectId}`,
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: `/project/${projectId}/modules`,
      icon: <FolderOutlined />,
      label: '模块管理',
    },
    {
      key: `/project/${projectId}/prd`,
      icon: <FileTextOutlined />,
      label: 'PRD 文档',
    },
    {
      key: `/project/${projectId}/testcase`,
      icon: <CheckSquareOutlined />,
      label: '测试用例',
    },
    {
      key: `/project/${projectId}/search`,
      icon: <SearchOutlined />,
      label: '语义搜索',
    },
    {
      key: `/project/${projectId}/import`,
      icon: <ImportOutlined />,
      label: '导入',
    },
    {
      key: `/project/${projectId}/tags`,
      icon: <FileTextOutlined />,
      label: '标签管理',
    },
  ];

  // 获取当前路径对应的菜单项
  const getCurrentMenuItem = () => {
    const path = location.pathname;
    if (path === `/project/${projectId}`) return '仪表盘';
    if (path.includes('/modules')) return '模块管理';
    if (path.includes('/prd')) return 'PRD 文档';
    if (path.includes('/testcase')) return '测试用例';
    if (path.includes('/search')) return '语义搜索';
    if (path.includes('/import')) return '导入';
    if (path.includes('/tags')) return '标签管理';
    return '';
  };

  return (
    <AntLayout className="min-h-screen">
      <Header className="flex items-center justify-between bg-white border-b px-6">
        <div className="flex items-center gap-4">
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/')}
          >
            返回项目列表
          </Button>
          <div className="text-xl font-bold">{currentProject?.name || '项目'}</div>
        </div>
        <Breadcrumb
          items={[
            {
              title: <HomeOutlined />,
              onClick: () => navigate('/'),
            },
            {
              title: currentProject?.name,
            },
            ...(getCurrentMenuItem()
              ? [
                  {
                    title: getCurrentMenuItem(),
                  },
                ]
              : []),
          ]}
        />
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
