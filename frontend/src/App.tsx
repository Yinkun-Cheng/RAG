import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Layout from './components/Layout';
import ProjectList from './pages/ProjectList';
import Dashboard from './pages/Dashboard';
import ModuleManagement from './pages/ModuleManagement';
import PRD from './pages/PRD';
import PRDDetail from './pages/PRD/PRDDetail';
import PRDForm from './pages/PRD/PRDForm';
import TestCase from './pages/TestCase';
import Search from './pages/Search';
import Import from './pages/Import';
import TagManagement from './pages/TagManagement';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* 项目选择页面 */}
            <Route path="/" element={<ProjectList />} />
            
            {/* 项目内页面 */}
            <Route path="/project/:projectId" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="modules" element={<ModuleManagement />} />
              <Route path="prd">
                <Route index element={<PRD />} />
                <Route path="new" element={<PRDForm />} />
                <Route path=":id" element={<PRDDetail />} />
                <Route path=":id/edit" element={<PRDForm />} />
              </Route>
              <Route path="testcase" element={<TestCase />} />
              <Route path="search" element={<Search />} />
              <Route path="import" element={<Import />} />
              <Route path="tags" element={<TagManagement />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ConfigProvider>
  );
}

export default App;
