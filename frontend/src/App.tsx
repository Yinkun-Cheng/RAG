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
import TestCaseDetail from './pages/TestCase/TestCaseDetail';
import TestCaseForm from './pages/TestCase/TestCaseForm';
import Search from './pages/Search';
import ImpactAnalysis from './pages/ImpactAnalysis';
import TagManagement from './pages/TagManagement';
import Settings from './pages/Settings';

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
              <Route path="testcase">
                <Route index element={<TestCase />} />
                <Route path="new" element={<TestCaseForm />} />
                <Route path=":id" element={<TestCaseDetail />} />
                <Route path=":id/edit" element={<TestCaseForm />} />
              </Route>
              <Route path="search" element={<Search />} />
              <Route path="impact-analysis" element={<ImpactAnalysis />} />
              <Route path="tags" element={<TagManagement />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
    </ConfigProvider>
  );
}

export default App;
