"""
属性测试 - 结构化错误响应

属性 18: 结构化错误响应
验证: 需求 9.2

验证对于任何错误情况，TestEngineerAgent 应该返回结构化的错误响应，
包含 success=False、task_type、error 消息和 metadata。
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock
from app.agent.test_engineer_agent import TestEngineerAgent, AgentResponse, TaskType
from app.workflow.base import WorkflowResult


# 生成随机错误消息的策略
error_messages = st.text(min_size=1, max_size=200)

# 生成随机任务类型的策略
task_types = st.sampled_from([
    TaskType.GENERATE_TEST_CASES,
    TaskType.IMPACT_ANALYSIS,
    TaskType.REGRESSION_RECOMMENDATION,
    TaskType.TEST_CASE_OPTIMIZATION,
    TaskType.UNKNOWN
])


@pytest.mark.asyncio
@given(error_message=error_messages)
@settings(max_examples=100, deadline=None)
async def test_property_error_response_structure(error_message):
    """
    属性 18: 结构化错误响应
    
    验证对于任何错误消息，AgentResponse 应该包含所有必需的错误字段。
    """
    # 创建错误响应
    response = AgentResponse(
        success=False,
        task_type=TaskType.UNKNOWN,
        error=error_message,
        metadata={'test': 'metadata'}
    )
    
    # 验证响应结构
    assert response.success is False, "错误响应的 success 应该为 False"
    assert isinstance(response.task_type, TaskType), "task_type 应该是 TaskType 枚举"
    assert response.error is not None, "错误响应应该包含 error 消息"
    assert isinstance(response.error, str), "error 应该是字符串类型"
    assert len(response.error) > 0, "error 消息不应该为空"
    assert isinstance(response.metadata, dict), "metadata 应该是字典类型"
    
    # 验证转换为字典后的结构
    response_dict = response.to_dict()
    assert 'success' in response_dict, "响应字典应该包含 success 字段"
    assert 'task_type' in response_dict, "响应字典应该包含 task_type 字段"
    assert 'error' in response_dict, "响应字典应该包含 error 字段"
    assert 'metadata' in response_dict, "响应字典应该包含 metadata 字段"
    assert response_dict['success'] is False, "字典中的 success 应该为 False"
    assert response_dict['error'] == error_message, "字典中的 error 应该与原始消息一致"


@pytest.mark.asyncio
@given(task_type=task_types, error_message=error_messages)
@settings(max_examples=100, deadline=None)
async def test_property_error_response_with_task_type(task_type, error_message):
    """
    属性 18: 结构化错误响应（带任务类型）
    
    验证对于任何任务类型和错误消息，错误响应应该正确包含任务类型信息。
    """
    response = AgentResponse(
        success=False,
        task_type=task_type,
        error=error_message
    )
    
    # 验证任务类型正确保存
    assert response.task_type == task_type, "任务类型应该正确保存"
    
    # 验证转换为字典后任务类型正确
    response_dict = response.to_dict()
    assert response_dict['task_type'] == task_type.value, "字典中的任务类型应该是字符串值"


@pytest.mark.asyncio
async def test_missing_project_id_error_structure():
    """测试缺少 project_id 时的错误响应结构"""
    # 创建模拟的 LLM 客户端
    mock_llm_client = AsyncMock()
    
    # 创建 Agent（不需要工作流）
    agent = TestEngineerAgent(llm_client=mock_llm_client)
    
    # 调用 process_request，缺少 project_id
    response = await agent.process_request(
        message="生成测试用例",
        context={}  # 缺少 project_id
    )
    
    # 验证错误响应结构
    assert response.success is False, "缺少 project_id 应该返回失败响应"
    assert response.task_type == TaskType.UNKNOWN, "缺少 project_id 时任务类型应该是 UNKNOWN"
    assert response.error is not None, "应该包含错误消息"
    assert "project_id" in response.error, "错误消息应该提到 project_id"
    assert isinstance(response.metadata, dict), "应该包含 metadata"
    assert 'duration_seconds' in response.metadata, "metadata 应该包含执行时间"
    
    # 验证转换为字典
    response_dict = response.to_dict()
    assert response_dict['success'] is False
    assert response_dict['error'] is not None


@pytest.mark.asyncio
async def test_unknown_task_error_structure():
    """测试未知任务类型时的错误响应结构"""
    mock_llm_client = AsyncMock()
    mock_llm_client.chat.return_value = "unknown"
    
    agent = TestEngineerAgent(llm_client=mock_llm_client)
    
    response = await agent.process_request(
        message="这是什么？",
        context={'project_id': 'test-123'}
    )
    
    # 验证错误响应结构
    assert response.success is False
    assert response.task_type == TaskType.UNKNOWN
    assert response.error is not None
    assert "无法确定任务类型" in response.error
    assert isinstance(response.metadata, dict)
    assert 'duration_seconds' in response.metadata
    assert 'classification_duration' in response.metadata


@pytest.mark.asyncio
async def test_workflow_not_found_error_structure():
    """测试工作流未找到时的错误响应结构"""
    mock_llm_client = AsyncMock()
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 创建没有工作流的 Agent
    agent = TestEngineerAgent(llm_client=mock_llm_client, workflows={})
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-123'}
    )
    
    # 验证错误响应结构
    assert response.success is False
    assert response.task_type == TaskType.GENERATE_TEST_CASES
    assert response.error is not None
    assert "未找到适合任务类型" in response.error
    assert isinstance(response.metadata, dict)
    assert 'duration_seconds' in response.metadata
    assert 'workflow_selection_duration' in response.metadata


@pytest.mark.asyncio
async def test_workflow_execution_failure_error_structure():
    """测试工作流执行失败时的错误响应结构"""
    from app.workflow.base import BaseWorkflow
    
    # 创建模拟工作流
    class MockFailingWorkflow(BaseWorkflow):
        @property
        def name(self) -> str:
            return "test_workflow"
        
        @property
        def description(self) -> str:
            return "测试工作流"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(
                success=False,
                error="工作流执行失败：数据库连接超时",
                metadata={'error_code': 'DB_TIMEOUT'}
            )
    
    mock_llm_client = AsyncMock()
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    # 创建 Agent 并注册失败的工作流
    agent = TestEngineerAgent(llm_client=mock_llm_client)
    agent.register_workflow(MockFailingWorkflow())
    
    # 手动设置工作流映射
    agent.workflows['test_case_generation'] = agent.workflows['test_workflow']
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-123'}
    )
    
    # 验证错误响应结构
    assert response.success is False
    assert response.task_type == TaskType.GENERATE_TEST_CASES
    assert response.error is not None
    assert "工作流执行失败" in response.error
    assert isinstance(response.metadata, dict)
    assert 'error_code' in response.metadata
    assert response.metadata['error_code'] == 'DB_TIMEOUT'
    assert 'duration_seconds' in response.metadata
    assert 'workflow_execution_duration' in response.metadata


@pytest.mark.asyncio
async def test_exception_error_structure():
    """测试异常时的错误响应结构"""
    from app.workflow.base import BaseWorkflow
    
    # 创建抛出异常的工作流
    class MockExceptionWorkflow(BaseWorkflow):
        @property
        def name(self) -> str:
            return "test_workflow"
        
        @property
        def description(self) -> str:
            return "测试工作流"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            raise ValueError("意外的值错误")
    
    mock_llm_client = AsyncMock()
    mock_llm_client.chat.return_value = "generate_test_cases"
    
    agent = TestEngineerAgent(llm_client=mock_llm_client)
    agent.register_workflow(MockExceptionWorkflow())
    agent.workflows['test_case_generation'] = agent.workflows['test_workflow']
    
    response = await agent.process_request(
        message="生成测试用例",
        context={'project_id': 'test-123'}
    )
    
    # 验证错误响应结构
    assert response.success is False
    assert response.task_type == TaskType.UNKNOWN
    assert response.error is not None
    assert "处理请求时发生异常" in response.error
    assert isinstance(response.metadata, dict)
    assert 'duration_seconds' in response.metadata
    assert 'exception_type' in response.metadata
    assert response.metadata['exception_type'] == 'ValueError'


def test_error_response_to_dict_completeness():
    """测试错误响应转换为字典的完整性"""
    response = AgentResponse(
        success=False,
        task_type=TaskType.GENERATE_TEST_CASES,
        error="测试错误消息",
        metadata={
            'error_code': 'TEST_ERROR',
            'duration_seconds': 1.23,
            'additional_info': '额外信息'
        }
    )
    
    response_dict = response.to_dict()
    
    # 验证所有字段都存在
    assert 'success' in response_dict
    assert 'task_type' in response_dict
    assert 'data' in response_dict
    assert 'error' in response_dict
    assert 'metadata' in response_dict
    
    # 验证字段值正确
    assert response_dict['success'] is False
    assert response_dict['task_type'] == 'generate_test_cases'
    assert response_dict['data'] == {}
    assert response_dict['error'] == "测试错误消息"
    assert response_dict['metadata']['error_code'] == 'TEST_ERROR'
    assert response_dict['metadata']['duration_seconds'] == 1.23
    assert response_dict['metadata']['additional_info'] == '额外信息'


@pytest.mark.asyncio
@given(
    error_message=st.text(min_size=1, max_size=100),
    error_code=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd'), whitelist_characters='_'))
)
@settings(max_examples=50, deadline=None)
async def test_property_error_metadata_preservation(error_message, error_code):
    """
    属性 18: 错误元数据保留
    
    验证错误响应中的 metadata 应该正确保留所有错误相关信息。
    """
    metadata = {
        'error_code': error_code,
        'timestamp': '2024-01-01T00:00:00Z',
        'component': 'TestEngineerAgent'
    }
    
    response = AgentResponse(
        success=False,
        task_type=TaskType.UNKNOWN,
        error=error_message,
        metadata=metadata
    )
    
    # 验证 metadata 完整保留
    assert response.metadata == metadata
    assert response.metadata['error_code'] == error_code
    
    # 验证转换为字典后 metadata 仍然完整
    response_dict = response.to_dict()
    assert response_dict['metadata'] == metadata
    assert response_dict['metadata']['error_code'] == error_code
