import React from 'react'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h1>RAG 测试用例知识库管理系统</h1>
        <p>前端项目初始化成功</p>
      </div>
    </ConfigProvider>
  )
}

export default App
