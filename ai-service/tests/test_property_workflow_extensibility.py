"""
属性测试 - Workflow 可扩展性

Feature: ai-test-assistant, Property 4: Workflow Extensibility

属性 4: Workflow 可扩展性
对于任何实现了 Workflow 接口的新 Workflow 类，TestEngineerAgent 应该能够
在不修改核心 Agent 代码的情况下发现并注册它。

验证: 需求 2.6
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock

from app.agent.test_engineer_agent import TestEngineerAgent
from app.integration.brconnector_client import BRConnectorClient
from app.workflow.base import BaseWorkflow, WorkflowResult


# 策略：生成随机的 Workflow 类
@st.composite
def workflow_strategy(draw):
    """生成随机的 Workflow 实例"""
    name = draw(st.text(min_size=5, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), blacklist_characters=' ')))
    description = draw(st.text(min_size=10, max_size=100))
    
    class DynamicWorkflow(BaseWorkflow):
        """动态生成的 Workflow 类"""
        
        def __init__(self):
            self._name = name
            self._description = description
        
        @property
        def name(self) -> str:
            return self._name
        
        @property
        def description(self) -> str:
            return self._description
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            """执行工作流（模拟）"""
            return WorkflowResult(
                success=True,
                data={'workflow_name': self._name},
                metadata={'executed': True}
            )
    
    return DynamicWorkflow()


# Feature: ai-test-assistant, Property 4: Workflow Extensibility
@given(workflow_strategy())
@pytest.mark.asyncio
async def test_property_workflow_extensibility(workflow):
    """
    属性 4: Workflow 可扩展性
    
    对于任何实现了 Workflow 接口的新 Workflow 类，TestEngineerAgent 应该能够
    在不修改核心 Agent 代码的情况下发现并注册它。
    """
    # 创建 Agent（不带任何预注册的工作流）
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 验证初始状态：没有工作流
    assert len(agent.workflows) == 0
    
    # 注册新工作流（不修改 Agent 代码）
    agent.register_workflow(workflow)
    
    # 验证工作流已注册
    assert workflow.name in agent.workflows
    assert agent.workflows[workflow.name] == workflow
    
    # 验证可以获取工作流
    retrieved_workflow = agent.get_workflow(workflow.name)
    assert retrieved_workflow is not None
    assert retrieved_workflow.name == workflow.name
    assert retrieved_workflow.description == workflow.description
    
    # 验证工作流列表包含新工作流
    workflow_list = agent.list_workflows()
    assert any(w['name'] == workflow.name for w in workflow_list)
    
    # 验证工作流可以执行
    result = await workflow.execute("test requirement", {})
    assert result.success is True


@given(st.lists(workflow_strategy(), min_size=1, max_size=10, unique_by=lambda w: w.name))
@pytest.mark.asyncio
async def test_property_multiple_workflows_discovery(workflows):
    """
    属性 4 扩展: 多个 Workflow 自动发现
    
    对于任何数量的 Workflow 实例列表，TestEngineerAgent 应该能够
    自动发现并注册所有工作流。
    """
    # 创建 Agent
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 自动发现并注册所有工作流
    agent.discover_workflows(workflows)
    
    # 验证所有工作流都已注册
    assert len(agent.workflows) == len(workflows)
    
    for workflow in workflows:
        assert workflow.name in agent.workflows
        assert agent.workflows[workflow.name] == workflow
    
    # 验证工作流列表完整
    workflow_list = agent.list_workflows()
    assert len(workflow_list) == len(workflows)
    
    for workflow in workflows:
        assert any(w['name'] == workflow.name for w in workflow_list)


def test_workflow_registration_without_code_modification():
    """
    测试工作流注册不需要修改 Agent 代码
    
    这个测试验证了可以在运行时动态注册工作流，
    而不需要修改 TestEngineerAgent 的源代码。
    """
    # 创建 Agent
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 定义一个新的 Workflow 类（在运行时）
    class CustomWorkflow(BaseWorkflow):
        @property
        def name(self) -> str:
            return "custom_workflow"
        
        @property
        def description(self) -> str:
            return "自定义工作流"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(
                success=True,
                data={'custom': True}
            )
    
    # 注册新工作流（不修改 Agent 代码）
    custom_workflow = CustomWorkflow()
    agent.register_workflow(custom_workflow)
    
    # 验证注册成功
    assert "custom_workflow" in agent.workflows
    assert agent.get_workflow("custom_workflow") is not None


def test_workflow_override():
    """
    测试工作流覆盖
    
    验证可以用新的工作流实例覆盖已存在的工作流。
    """
    # 创建 Agent
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 定义第一个工作流
    class WorkflowV1(BaseWorkflow):
        @property
        def name(self) -> str:
            return "test_workflow"
        
        @property
        def description(self) -> str:
            return "版本 1"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True, data={'version': 1})
    
    # 定义第二个工作流（同名）
    class WorkflowV2(BaseWorkflow):
        @property
        def name(self) -> str:
            return "test_workflow"
        
        @property
        def description(self) -> str:
            return "版本 2"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True, data={'version': 2})
    
    # 注册第一个版本
    v1 = WorkflowV1()
    agent.register_workflow(v1)
    assert agent.get_workflow("test_workflow").description == "版本 1"
    
    # 注册第二个版本（覆盖）
    v2 = WorkflowV2()
    agent.register_workflow(v2)
    assert agent.get_workflow("test_workflow").description == "版本 2"


def test_workflow_interface_compliance():
    """
    测试 Workflow 接口合规性
    
    验证所有注册的工作流都实现了必需的接口方法。
    """
    # 创建 Agent
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 定义一个完整实现接口的工作流
    class CompliantWorkflow(BaseWorkflow):
        @property
        def name(self) -> str:
            return "compliant_workflow"
        
        @property
        def description(self) -> str:
            return "合规的工作流"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True)
    
    # 注册工作流
    workflow = CompliantWorkflow()
    agent.register_workflow(workflow)
    
    # 验证接口方法存在且可调用
    assert hasattr(workflow, 'name')
    assert hasattr(workflow, 'description')
    assert hasattr(workflow, 'execute')
    assert callable(workflow.execute)
    
    # 验证属性返回正确类型
    assert isinstance(workflow.name, str)
    assert isinstance(workflow.description, str)


@pytest.mark.asyncio
async def test_workflow_execution_isolation():
    """
    测试工作流执行隔离
    
    验证多个工作流可以独立执行，互不干扰。
    """
    # 创建 Agent
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 定义两个工作流
    class Workflow1(BaseWorkflow):
        @property
        def name(self) -> str:
            return "workflow1"
        
        @property
        def description(self) -> str:
            return "工作流 1"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True, data={'id': 1})
    
    class Workflow2(BaseWorkflow):
        @property
        def name(self) -> str:
            return "workflow2"
        
        @property
        def description(self) -> str:
            return "工作流 2"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True, data={'id': 2})
    
    # 注册两个工作流
    w1 = Workflow1()
    w2 = Workflow2()
    agent.register_workflow(w1)
    agent.register_workflow(w2)
    
    # 执行两个工作流
    result1 = await w1.execute("test", {})
    result2 = await w2.execute("test", {})
    
    # 验证结果独立
    assert result1.data['id'] == 1
    assert result2.data['id'] == 2
    assert result1.data != result2.data
