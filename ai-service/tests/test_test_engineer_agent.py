"""
TestEngineerAgent 单元测试
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.agent.test_engineer_agent import TestEngineerAgent, AgentResponse, TaskType
from app.integration.brconnector_client import BRConnectorClient
from app.workflow.base import BaseWorkflow, WorkflowResult


class MockWorkflow(BaseWorkflow):
    """模拟工作流"""
    
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self.execute_mock = AsyncMock(return_value=WorkflowResult(
            success=True,
            data={'result': 'mock_result'},
            metadata={'mock': True}
        ))
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    async def execute(self, requirement: str, context: dict) -> WorkflowResult:
        """执行工作流（模拟）"""
        return await self.execute_mock(requirement, context)


@pytest.fixture
def mock_llm_client():
    """创建模拟的 LLM 客户端"""
    client = AsyncMock(spec=BRConnectorClient)
    return client


@pytest.fixture
def mock_workflows():
    """创建模拟的工作流字典"""
    return {
        'test_case_generation': MockWorkflow('test_case_generation', '测试用例生成'),
        'impact_analysis': MockWorkflow('impact_analysis', '影响分析'),
        'regression_recommendation': MockWorkflow('regression_recommendation', '回归测试推荐'),
        'test_case_optimization': MockWorkflow('test_case_optimization', '测试用例优化')
    }


@pytest.fixture
def agent(mock_llm_client, mock_workflows):
    """创建 TestEngineerAgent 实例"""
    return TestEngineerAgent(
        llm_client=mock_llm_client,
        workflows=mock_workflows
    )


def test_agent_initialization(mock_llm_client):
    """测试 Agent 初始化"""
    agent = TestEngineerAgent(llm_client=mock_llm_client)
    
    assert agent.llm_client == mock_llm_client
    assert agent.workflows == {}


def test_agent_initialization_with_workflows(mock_llm_client, mock_workflows):
    """测试带工作流的 Agent 初始化"""
    agent = TestEngineerAgent(
        llm_client=mock_llm_client,
        workflows=mock_workflows
    )
    
    assert len(agent.workflows) == 4
    assert 'test_case_generation' in agent.workflows


def test_register_workflow(agent):
    """测试注册工作流"""
    new_workflow = MockWorkflow('new_workflow', '新工作流')
    
    agent.register_workflow(new_workflow)
    
    assert 'new_workflow' in agent.workflows
    assert agent.workflows['new_workflow'] == new_workflow


def test_register_workflow_override(agent):
    """测试覆盖已存在的工作流"""
    original_workflow = agent.workflows['test_case_generation']
    new_workflow = MockWorkflow('test_case_generation', '新的测试用例生成')
    
    agent.register_workflow(new_workflow)
    
    assert agent.workflows['test_case_generation'] == new_workflow
    assert agent.workflows['test_case_generation'] != original_workflow


def test_discover_workflows(mock_llm_client):
    """测试自动发现工作流"""
    agent = TestEngineerAgent(llm_client=mock_llm_client)
    
    workflows = [
        MockWorkflow('workflow1', '工作流1'),
        MockWorkflow('workflow2', '工作流2'),
        MockWorkflow('workflow3', '工作流3')
    ]
    
    agent.discover_workflows(workflows)
    
    assert len(agent.workflows) == 3
    assert 'workflow1' in agent.workflows
    assert 'workflow2' in agent.workflows
    assert 'workflow3' in agent.workflows


def test_get_workflow(agent):
    """测试获取工作流"""
    workflow = agent.get_workflow('test_case_generation')
    
    assert workflow is not None
    assert workflow.name == 'test_case_generation'


def test_get_workflow_not_found(agent):
    """测试获取不存在的工作流"""
    workflow = agent.get_workflow('non_existent')
    
    assert workflow is None


def test_list_workflows(agent):
    """测试列出所有工作流"""
    workflows = agent.list_workflows()
    
    assert len(workflows) == 4
    assert all('name' in w and 'description' in w for w in workflows)
    
    workflow_names = [w['name'] for w in workflows]
    assert 'test_case_generation' in workflow_names
    assert 'impact_analysis' in workflow_names


@pytest.mark.asyncio
async def test_classify_task_generate(agent, mock_llm_client):
    """测试任务分类 - 生成测试用例（使用 LLM）"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 使用一个不包含明显关键词的消息，强制使用 LLM
    task_type = await agent.classify_task("帮我做一下登录功能的测试", {})
    
    assert task_type == TaskType.GENERATE_TEST_CASES
    mock_llm_client.chat.assert_called_once()


@pytest.mark.asyncio
async def test_classify_task_generate_by_keywords(agent, mock_llm_client):
    """测试任务分类 - 通过关键词快速分类生成测试用例"""
    # 不应该调用 LLM（通过关键词快速分类）
    task_type = await agent.classify_task("生成用户登录的测试用例", {})
    
    assert task_type == TaskType.GENERATE_TEST_CASES
    # 验证没有调用 LLM
    mock_llm_client.chat.assert_not_called()


@pytest.mark.asyncio
async def test_classify_task_impact_analysis(agent, mock_llm_client):
    """测试任务分类 - 影响分析"""
    mock_llm_client.chat.return_value = "impact_analysis"
    
    task_type = await agent.classify_task("分析这个需求变更的影响", {})
    
    assert task_type == TaskType.IMPACT_ANALYSIS


@pytest.mark.asyncio
async def test_classify_task_impact_analysis_by_keywords(agent, mock_llm_client):
    """测试任务分类 - 通过关键词快速分类影响分析"""
    task_type = await agent.classify_task("分析需求变更影响", {})
    
    assert task_type == TaskType.IMPACT_ANALYSIS
    mock_llm_client.chat.assert_not_called()


@pytest.mark.asyncio
async def test_classify_task_regression(agent, mock_llm_client):
    """测试任务分类 - 回归测试推荐"""
    mock_llm_client.chat.return_value = "regression_recommendation"
    
    task_type = await agent.classify_task("推荐回归测试用例", {})
    
    assert task_type == TaskType.REGRESSION_RECOMMENDATION


@pytest.mark.asyncio
async def test_classify_task_regression_by_keywords(agent, mock_llm_client):
    """测试任务分类 - 通过关键词快速分类回归测试"""
    task_type = await agent.classify_task("推荐回归测试", {})
    
    assert task_type == TaskType.REGRESSION_RECOMMENDATION
    mock_llm_client.chat.assert_not_called()


@pytest.mark.asyncio
async def test_classify_task_optimization(agent, mock_llm_client):
    """测试任务分类 - 测试用例优化"""
    mock_llm_client.chat.return_value = "test_case_optimization"
    
    task_type = await agent.classify_task("优化现有的测试用例", {})
    
    assert task_type == TaskType.TEST_CASE_OPTIMIZATION


@pytest.mark.asyncio
async def test_classify_task_optimization_by_keywords(agent, mock_llm_client):
    """测试任务分类 - 通过关键词快速分类优化"""
    task_type = await agent.classify_task("优化测试用例", {})
    
    assert task_type == TaskType.TEST_CASE_OPTIMIZATION
    mock_llm_client.chat.assert_not_called()


@pytest.mark.asyncio
async def test_classify_task_with_conversation_history(agent, mock_llm_client):
    """测试任务分类 - 带对话历史"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    context = {
        'conversation_history': [
            {'role': 'user', 'content': '我想测试登录功能'},
            {'role': 'assistant', 'content': '好的，我可以帮你生成测试用例'}
        ],
        'last_task_type': 'generate_test_cases'
    }
    
    task_type = await agent.classify_task("继续", context)
    
    assert task_type == TaskType.GENERATE_TEST_CASES
    # 验证 LLM 被调用（因为"继续"无法通过关键词分类）
    mock_llm_client.chat.assert_called_once()
    
    # 验证 prompt 包含上下文信息
    call_args = mock_llm_client.chat.call_args
    prompt = call_args[1]['messages'][0]['content']
    assert '对话历史' in prompt
    assert '上一次任务类型' in prompt


@pytest.mark.asyncio
async def test_classify_task_unknown(agent, mock_llm_client):
    """测试任务分类 - 未知任务"""
    mock_llm_client.chat.return_value = "unknown"
    
    task_type = await agent.classify_task("这是什么？", {})
    
    assert task_type == TaskType.UNKNOWN


@pytest.mark.asyncio
async def test_classify_task_error(agent, mock_llm_client):
    """测试任务分类失败"""
    mock_llm_client.chat.side_effect = Exception("LLM 调用失败")
    
    task_type = await agent.classify_task("生成测试用例", {})
    
    # 默认返回生成测试用例任务
    assert task_type == TaskType.GENERATE_TEST_CASES


def test_select_workflow_generate(agent):
    """测试选择工作流 - 生成测试用例"""
    workflow = agent.select_workflow(TaskType.GENERATE_TEST_CASES)
    
    assert workflow is not None
    assert workflow.name == 'test_case_generation'


def test_select_workflow_impact_analysis(agent):
    """测试选择工作流 - 影响分析"""
    workflow = agent.select_workflow(TaskType.IMPACT_ANALYSIS)
    
    assert workflow is not None
    assert workflow.name == 'impact_analysis'


def test_select_workflow_regression(agent):
    """测试选择工作流 - 回归测试推荐"""
    workflow = agent.select_workflow(TaskType.REGRESSION_RECOMMENDATION)
    
    assert workflow is not None
    assert workflow.name == 'regression_recommendation'


def test_select_workflow_optimization(agent):
    """测试选择工作流 - 测试用例优化"""
    workflow = agent.select_workflow(TaskType.TEST_CASE_OPTIMIZATION)
    
    assert workflow is not None
    assert workflow.name == 'test_case_optimization'


def test_select_workflow_unknown(agent):
    """测试选择工作流 - 未知任务"""
    workflow = agent.select_workflow(TaskType.UNKNOWN)
    
    assert workflow is None


@pytest.mark.asyncio
async def test_process_request_success(agent, mock_llm_client):
    """测试成功处理请求"""
    # 模拟任务分类
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 执行请求
    response = await agent.process_request(
        message="生成用户登录的测试用例",
        context={'project_id': 'test-project-123'}
    )
    
    # 验证响应
    assert isinstance(response, AgentResponse)
    assert response.success is True
    assert response.task_type == TaskType.GENERATE_TEST_CASES
    assert 'result' in response.data
    assert 'workflow_name' in response.metadata
    assert 'total_duration_seconds' in response.metadata
    assert response.metadata['total_duration_seconds'] >= 0


@pytest.mark.asyncio
async def test_process_request_with_custom_timeout(agent, mock_llm_client):
    """测试自定义超时时间"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 使用自定义超时时间
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-project-123'},
        timeout=60.0  # 60 秒超时
    )
    
    assert response.success is True
    assert 'total_duration_seconds' in response.metadata


@pytest.mark.asyncio
async def test_process_request_timeout(agent, mock_llm_client, mock_workflows):
    """测试请求超时"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 模拟工作流执行缓慢（超过超时时间）
    async def slow_execute(*args, **kwargs):
        await asyncio.sleep(2)  # 睡眠 2 秒
        return WorkflowResult(success=True, data={'result': 'slow'})
    
    mock_workflows['test_case_generation'].execute_mock.side_effect = slow_execute
    
    # 设置很短的超时时间
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-project-123'},
        timeout=0.5  # 0.5 秒超时
    )
    
    # 验证超时响应
    assert response.success is False
    assert "超时" in response.error
    assert 'timeout_error' in response.metadata
    assert response.metadata['timeout_error'] is True
    assert 'timeout_seconds' in response.metadata
    assert response.metadata['timeout_seconds'] == 0.5


@pytest.mark.asyncio
async def test_process_request_performance_monitoring(agent, mock_llm_client):
    """测试性能监控"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-project-123'}
    )
    
    # 验证性能监控元数据
    assert 'total_duration_seconds' in response.metadata
    assert 'duration_seconds' in response.metadata
    assert isinstance(response.metadata['total_duration_seconds'], float)
    assert response.metadata['total_duration_seconds'] >= 0


@pytest.mark.asyncio
async def test_process_request_missing_project_id(agent):
    """测试缺少 project_id"""
    response = await agent.process_request(
        message="生成测试用例",
        context={}
    )
    
    assert response.success is False
    assert "缺少必需的 project_id 参数" in response.error


@pytest.mark.asyncio
async def test_process_request_unknown_task(agent, mock_llm_client):
    """测试未知任务类型"""
    mock_llm_client.chat.return_value = "unknown"
    
    response = await agent.process_request(
        message="这是什么？",
        context={'project_id': 'test-project-123'}
    )
    
    assert response.success is False
    assert response.task_type == TaskType.UNKNOWN
    assert "无法确定任务类型" in response.error


@pytest.mark.asyncio
async def test_process_request_workflow_not_found(mock_llm_client):
    """测试工作流未找到"""
    # 创建没有工作流的 Agent
    agent = TestEngineerAgent(llm_client=mock_llm_client, workflows={})
    
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-project-123'}
    )
    
    assert response.success is False
    assert "未找到适合任务类型" in response.error


@pytest.mark.asyncio
async def test_process_request_workflow_failure(agent, mock_llm_client, mock_workflows):
    """测试工作流执行失败"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 模拟工作流执行失败
    mock_workflows['test_case_generation'].execute_mock.return_value = WorkflowResult(
        success=False,
        error="工作流执行失败"
    )
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-project-123'}
    )
    
    assert response.success is False
    assert "工作流执行失败" in response.error


@pytest.mark.asyncio
async def test_process_request_exception(agent, mock_llm_client, mock_workflows):
    """测试处理请求时发生异常"""
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 模拟工作流执行抛出异常
    mock_workflows['test_case_generation'].execute_mock.side_effect = Exception("意外错误")
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-project-123'}
    )
    
    assert response.success is False
    assert "处理请求时发生异常" in response.error


def test_agent_response_to_dict():
    """测试 AgentResponse 转换为字典"""
    response = AgentResponse(
        success=True,
        task_type=TaskType.GENERATE_TEST_CASES,
        data={'test': 'data'},
        metadata={'meta': 'data'}
    )
    
    result = response.to_dict()
    
    assert result['success'] is True
    assert result['task_type'] == 'generate_test_cases'
    assert result['data'] == {'test': 'data'}
    assert result['metadata'] == {'meta': 'data'}
    assert result['error'] is None
