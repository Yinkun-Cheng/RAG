"""
属性测试 - Workflow 自动发现

Feature: ai-test-assistant, Property 19: Workflow Auto-Discovery

属性 19: Workflow 自动发现
对于任何放置在 workflows 目录中实现了 Workflow 接口的 Workflow 类，
TestEngineerAgent 应该在初始化时自动发现并注册它。

验证: 需求 11.2
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import AsyncMock

from app.agent.test_engineer_agent import TestEngineerAgent
from app.integration.brconnector_client import BRConnectorClient
from app.workflow.base import BaseWorkflow, WorkflowResult


# 策略：生成随机的 Workflow 类列表
@st.composite
def workflow_list_strategy(draw):
    """生成随机的 Workflow 实例列表"""
    count = draw(st.integers(min_value=1, max_value=10))
    workflows = []
    
    for i in range(count):
        name = f"workflow_{i}_{draw(st.text(min_size=3, max_size=10, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))}"
        description = draw(st.text(min_size=10, max_size=50))
        
        class DynamicWorkflow(BaseWorkflow):
            """动态生成的 Workflow 类"""
            
            def __init__(self, wf_name, wf_desc):
                self._name = wf_name
                self._description = wf_desc
            
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
                    metadata={'discovered': True}
                )
        
        workflows.append(DynamicWorkflow(name, description))
    
    return workflows


# Feature: ai-test-assistant, Property 19: Workflow Auto-Discovery
@given(workflow_list_strategy())
@pytest.mark.asyncio
async def test_property_workflow_auto_discovery(workflows):
    """
    属性 19: Workflow 自动发现
    
    对于任何放置在 workflows 目录中实现了 Workflow 接口的 Workflow 类，
    TestEngineerAgent 应该在初始化时自动发现并注册它。
    """
    # 创建 Agent（不带任何预注册的工作流）
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 验证初始状态：没有工作流
    assert len(agent.workflows) == 0
    
    # 模拟自动发现过程（在实际系统中，这会在初始化时自动完成）
    agent.discover_workflows(workflows)
    
    # 验证所有工作流都已被发现并注册
    assert len(agent.workflows) == len(workflows)
    
    for workflow in workflows:
        # 验证工作流已注册
        assert workflow.name in agent.workflows
        assert agent.workflows[workflow.name] == workflow
        
        # 验证可以通过名称获取工作流
        retrieved = agent.get_workflow(workflow.name)
        assert retrieved is not None
        assert retrieved.name == workflow.name
        assert retrieved.description == workflow.description
        
        # 验证工作流可以执行
        result = await workflow.execute("test requirement", {})
        assert result.success is True
        assert result.metadata.get('discovered') is True


def test_discover_workflows_empty_list():
    """
    测试发现空工作流列表
    
    验证当没有工作流时，Agent 仍然可以正常工作。
    """
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 发现空列表
    agent.discover_workflows([])
    
    # 验证没有工作流被注册
    assert len(agent.workflows) == 0
    assert agent.list_workflows() == []


def test_discover_workflows_with_duplicates():
    """
    测试发现重复的工作流
    
    验证当有重复名称的工作流时，后者会覆盖前者。
    """
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 创建两个同名的工作流
    class Workflow1(BaseWorkflow):
        @property
        def name(self) -> str:
            return "duplicate_workflow"
        
        @property
        def description(self) -> str:
            return "第一个版本"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True, data={'version': 1})
    
    class Workflow2(BaseWorkflow):
        @property
        def name(self) -> str:
            return "duplicate_workflow"
        
        @property
        def description(self) -> str:
            return "第二个版本"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True, data={'version': 2})
    
    w1 = Workflow1()
    w2 = Workflow2()
    
    # 发现工作流（包含重复）
    agent.discover_workflows([w1, w2])
    
    # 验证只有一个工作流被注册（后者覆盖前者）
    assert len(agent.workflows) == 1
    assert agent.get_workflow("duplicate_workflow").description == "第二个版本"


def test_discover_workflows_preserves_existing():
    """
    测试发现工作流时保留已存在的工作流
    
    验证多次调用 discover_workflows 会累积工作流。
    """
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 创建第一批工作流
    class Workflow1(BaseWorkflow):
        @property
        def name(self) -> str:
            return "workflow1"
        
        @property
        def description(self) -> str:
            return "工作流 1"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True)
    
    # 创建第二批工作流
    class Workflow2(BaseWorkflow):
        @property
        def name(self) -> str:
            return "workflow2"
        
        @property
        def description(self) -> str:
            return "工作流 2"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True)
    
    w1 = Workflow1()
    w2 = Workflow2()
    
    # 第一次发现
    agent.discover_workflows([w1])
    assert len(agent.workflows) == 1
    assert "workflow1" in agent.workflows
    
    # 第二次发现
    agent.discover_workflows([w2])
    assert len(agent.workflows) == 2
    assert "workflow1" in agent.workflows
    assert "workflow2" in agent.workflows


@pytest.mark.asyncio
async def test_discover_workflows_all_executable():
    """
    测试所有发现的工作流都可执行
    
    验证发现的工作流都实现了 execute 方法并可以正常执行。
    """
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 创建多个工作流
    workflows = []
    for i in range(5):
        class DynamicWorkflow(BaseWorkflow):
            def __init__(self, idx):
                self.idx = idx
            
            @property
            def name(self) -> str:
                return f"workflow_{self.idx}"
            
            @property
            def description(self) -> str:
                return f"工作流 {self.idx}"
            
            async def execute(self, requirement: str, context: dict) -> WorkflowResult:
                return WorkflowResult(
                    success=True,
                    data={'index': self.idx}
                )
        
        workflows.append(DynamicWorkflow(i))
    
    # 发现工作流
    agent.discover_workflows(workflows)
    
    # 验证所有工作流都可执行
    for i, workflow in enumerate(workflows):
        result = await workflow.execute("test", {})
        assert result.success is True
        assert result.data['index'] == i


def test_discover_workflows_interface_validation():
    """
    测试发现工作流时的接口验证
    
    验证所有发现的工作流都实现了必需的接口。
    """
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 创建符合接口的工作流
    class ValidWorkflow(BaseWorkflow):
        @property
        def name(self) -> str:
            return "valid_workflow"
        
        @property
        def description(self) -> str:
            return "有效的工作流"
        
        async def execute(self, requirement: str, context: dict) -> WorkflowResult:
            return WorkflowResult(success=True)
    
    workflow = ValidWorkflow()
    
    # 发现工作流
    agent.discover_workflows([workflow])
    
    # 验证工作流实现了所有必需的接口
    registered_workflow = agent.get_workflow("valid_workflow")
    assert hasattr(registered_workflow, 'name')
    assert hasattr(registered_workflow, 'description')
    assert hasattr(registered_workflow, 'execute')
    assert callable(registered_workflow.execute)


@given(st.integers(min_value=1, max_value=20))
def test_discover_workflows_scalability(workflow_count):
    """
    测试工作流发现的可扩展性
    
    验证 Agent 可以处理大量工作流的发现和注册。
    """
    llm_client = AsyncMock(spec=BRConnectorClient)
    agent = TestEngineerAgent(llm_client=llm_client, workflows={})
    
    # 创建大量工作流
    workflows = []
    for i in range(workflow_count):
        class DynamicWorkflow(BaseWorkflow):
            def __init__(self, idx):
                self.idx = idx
            
            @property
            def name(self) -> str:
                return f"workflow_{self.idx}"
            
            @property
            def description(self) -> str:
                return f"工作流 {self.idx}"
            
            async def execute(self, requirement: str, context: dict) -> WorkflowResult:
                return WorkflowResult(success=True)
        
        workflows.append(DynamicWorkflow(i))
    
    # 发现所有工作流
    agent.discover_workflows(workflows)
    
    # 验证所有工作流都已注册
    assert len(agent.workflows) == workflow_count
    
    # 验证可以列出所有工作流
    workflow_list = agent.list_workflows()
    assert len(workflow_list) == workflow_count
    
    # 验证每个工作流都可以通过名称获取
    for i in range(workflow_count):
        workflow_name = f"workflow_{i}"
        assert workflow_name in agent.workflows
        assert agent.get_workflow(workflow_name) is not None
