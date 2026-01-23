"""
ImpactAnalysisWorkflow 单元测试
"""

import pytest
from unittest.mock import AsyncMock
from app.workflow.impact_analysis_workflow import ImpactAnalysisWorkflow
from app.workflow.base import WorkflowResult
from app.agent.impact_analysis_agent import ImpactAnalysisAgent, ImpactReport
from app.tool.retrieval_tools import SearchPRDTool, SearchTestCaseTool, GetRelatedCasesTool


@pytest.fixture
def mock_impact_agent():
    """创建模拟的 ImpactAnalysisAgent"""
    agent = AsyncMock(spec=ImpactAnalysisAgent)
    return agent


@pytest.fixture
def mock_search_prd_tool():
    """创建模拟的 SearchPRDTool"""
    tool = AsyncMock(spec=SearchPRDTool)
    tool.backend_url = "http://localhost:8080"
    return tool


@pytest.fixture
def mock_search_testcase_tool():
    """创建模拟的 SearchTestCaseTool"""
    tool = AsyncMock(spec=SearchTestCaseTool)
    return tool


@pytest.fixture
def mock_get_related_cases_tool():
    """创建模拟的 GetRelatedCasesTool"""
    tool = AsyncMock(spec=GetRelatedCasesTool)
    return tool


@pytest.fixture
def workflow(mock_impact_agent, mock_search_prd_tool, mock_search_testcase_tool, mock_get_related_cases_tool):
    """创建 ImpactAnalysisWorkflow 实例"""
    return ImpactAnalysisWorkflow(
        impact_agent=mock_impact_agent,
        search_prd_tool=mock_search_prd_tool,
        search_testcase_tool=mock_search_testcase_tool,
        get_related_cases_tool=mock_get_related_cases_tool
    )


def test_workflow_properties(workflow):
    """测试工作流属性"""
    assert workflow.name == "impact_analysis"
    assert workflow.description == "分析需求变更对现有测试用例和模块的影响"


@pytest.mark.asyncio
async def test_execute_success(
    workflow,
    mock_impact_agent,
    mock_search_prd_tool,
    mock_search_testcase_tool
):
    """测试成功的工作流执行"""
    # 准备测试数据
    change_description = "新增用户权限管理功能"
    context = {
        'project_id': 'test-project-123',
        'prd_limit': 3,
        'case_limit': 5
    }
    
    # 模拟 PRD 搜索结果
    related_prds = [
        {"id": "prd1", "title": "用户管理 PRD", "content": "内容1"},
        {"id": "prd2", "title": "权限系统 PRD", "content": "内容2"}
    ]
    mock_search_prd_tool.execute.return_value = related_prds
    
    # 模拟测试用例搜索结果
    existing_cases = [
        {"id": "case1", "title": "用户登录测试", "module": "用户管理"},
        {"id": "case2", "title": "权限验证测试", "module": "权限系统"}
    ]
    mock_search_testcase_tool.execute.return_value = existing_cases
    
    # 模拟影响分析结果
    impact_report = ImpactReport(
        summary="新增权限管理功能将影响用户管理和权限系统模块",
        affected_modules=["用户管理", "权限系统"],
        affected_test_cases=[
            {"title": "用户登录测试", "reason": "需要验证权限", "action": "update"}
        ],
        risk_level="medium",
        recommendations=["更新用户登录测试用例"],
        change_type="feature_add"
    )
    mock_impact_agent.analyze_impact.return_value = impact_report
    
    # 执行工作流
    result = await workflow.execute(change_description, context)
    
    # 验证结果
    assert isinstance(result, WorkflowResult)
    assert result.success is True
    assert result.error is None
    
    # 验证返回的数据
    assert 'impact_report' in result.data
    assert 'related_prds' in result.data
    assert 'existing_test_cases' in result.data
    
    impact_data = result.data['impact_report']
    assert impact_data['summary'] == "新增权限管理功能将影响用户管理和权限系统模块"
    assert len(impact_data['affected_modules']) == 2
    assert impact_data['risk_level'] == "medium"
    assert impact_data['change_type'] == "feature_add"
    
    # 验证元数据
    assert result.metadata['risk_level'] == "medium"
    assert result.metadata['change_type'] == "feature_add"
    assert result.metadata['affected_modules_count'] == 2
    assert result.metadata['affected_cases_count'] == 1
    assert result.metadata['related_prds_count'] == 2
    assert result.metadata['existing_cases_count'] == 2
    
    # 验证工具调用
    mock_search_prd_tool.execute.assert_called_once_with(
        query=change_description,
        project_id='test-project-123',
        limit=3
    )
    
    mock_search_testcase_tool.execute.assert_called_once_with(
        query=change_description,
        project_id='test-project-123',
        limit=5
    )
    
    mock_impact_agent.analyze_impact.assert_called_once_with(
        change_description=change_description,
        related_prds=related_prds,
        existing_test_cases=existing_cases
    )


@pytest.mark.asyncio
async def test_execute_missing_project_id(workflow):
    """测试缺少 project_id 参数"""
    change_description = "新增功能"
    context = {}  # 缺少 project_id
    
    # 执行工作流
    result = await workflow.execute(change_description, context)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 project_id 参数" in result.error


@pytest.mark.asyncio
async def test_execute_no_context(workflow):
    """测试没有上下文"""
    change_description = "新增功能"
    
    # 执行工作流
    result = await workflow.execute(change_description, None)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 project_id 参数" in result.error


@pytest.mark.asyncio
async def test_execute_prd_search_failure(
    workflow,
    mock_impact_agent,
    mock_search_prd_tool,
    mock_search_testcase_tool
):
    """测试 PRD 搜索失败"""
    change_description = "新增功能"
    context = {'project_id': 'test-project-123'}
    
    # 模拟 PRD 搜索失败
    mock_search_prd_tool.execute.side_effect = Exception("搜索失败")
    
    # 模拟测试用例搜索成功
    mock_search_testcase_tool.execute.return_value = []
    
    # 模拟影响分析成功
    impact_report = ImpactReport(
        summary="影响分析",
        affected_modules=[],
        affected_test_cases=[],
        risk_level="low",
        recommendations=[],
        change_type="feature_add"
    )
    mock_impact_agent.analyze_impact.return_value = impact_report
    
    # 执行工作流（应该继续执行）
    result = await workflow.execute(change_description, context)
    
    # 验证结果（应该成功，但有警告）
    assert result.success is True
    assert "无法检索历史 PRD，将继续执行" in result.metadata['warnings']
    
    # 验证影响分析仍然被调用
    mock_impact_agent.analyze_impact.assert_called_once()


@pytest.mark.asyncio
async def test_execute_testcase_search_failure(
    workflow,
    mock_impact_agent,
    mock_search_prd_tool,
    mock_search_testcase_tool
):
    """测试测试用例搜索失败"""
    change_description = "新增功能"
    context = {'project_id': 'test-project-123'}
    
    # 模拟 PRD 搜索成功
    mock_search_prd_tool.execute.return_value = []
    
    # 模拟测试用例搜索失败
    mock_search_testcase_tool.execute.side_effect = Exception("搜索失败")
    
    # 模拟影响分析成功
    impact_report = ImpactReport(
        summary="影响分析",
        affected_modules=[],
        affected_test_cases=[],
        risk_level="low",
        recommendations=[],
        change_type="feature_add"
    )
    mock_impact_agent.analyze_impact.return_value = impact_report
    
    # 执行工作流（应该继续执行）
    result = await workflow.execute(change_description, context)
    
    # 验证结果（应该成功，但有警告）
    assert result.success is True
    assert "无法检索测试用例，将继续执行" in result.metadata['warnings']


@pytest.mark.asyncio
async def test_execute_impact_analysis_failure(
    workflow,
    mock_impact_agent,
    mock_search_prd_tool,
    mock_search_testcase_tool
):
    """测试影响分析失败"""
    change_description = "新增功能"
    context = {'project_id': 'test-project-123'}
    
    # 模拟 PRD 搜索成功
    mock_search_prd_tool.execute.return_value = []
    
    # 模拟测试用例搜索成功
    mock_search_testcase_tool.execute.return_value = []
    
    # 模拟影响分析失败
    mock_impact_agent.analyze_impact.side_effect = Exception("分析失败")
    
    # 执行工作流
    result = await workflow.execute(change_description, context)
    
    # 验证结果（应该失败）
    assert result.success is False
    assert "影响分析失败" in result.error
    assert result.metadata['step'] == 'impact_analysis'


@pytest.mark.asyncio
async def test_execute_with_default_limits(
    workflow,
    mock_impact_agent,
    mock_search_prd_tool,
    mock_search_testcase_tool
):
    """测试使用默认的限制参数"""
    change_description = "新增功能"
    context = {'project_id': 'test-project-123'}  # 不指定 prd_limit 和 case_limit
    
    # 模拟返回值
    mock_search_prd_tool.execute.return_value = []
    mock_search_testcase_tool.execute.return_value = []
    impact_report = ImpactReport(
        summary="影响分析",
        affected_modules=[],
        affected_test_cases=[],
        risk_level="low",
        recommendations=[],
        change_type="feature_add"
    )
    mock_impact_agent.analyze_impact.return_value = impact_report
    
    # 执行工作流
    result = await workflow.execute(change_description, context)
    
    # 验证使用了默认值
    mock_search_prd_tool.execute.assert_called_once_with(
        query=change_description,
        project_id='test-project-123',
        limit=5  # 默认值
    )
    
    mock_search_testcase_tool.execute.assert_called_once_with(
        query=change_description,
        project_id='test-project-123',
        limit=10  # 默认值
    )


@pytest.mark.asyncio
async def test_execute_unexpected_error(
    workflow,
    mock_search_prd_tool,
    mock_search_testcase_tool,
    mock_impact_agent
):
    """测试意外错误"""
    change_description = "新增功能"
    context = {'project_id': 'test-project-123'}
    
    # 模拟 PRD 搜索失败
    mock_search_prd_tool.execute.side_effect = RuntimeError("意外错误")
    
    # 模拟测试用例搜索成功
    mock_search_testcase_tool.execute.return_value = []
    
    # 模拟影响分析也失败
    mock_impact_agent.analyze_impact.side_effect = RuntimeError("分析失败")
    
    # 执行工作流
    result = await workflow.execute(change_description, context)
    
    # 验证结果（应该失败，因为影响分析失败）
    assert result.success is False
    assert "影响分析失败" in result.error
    # 验证有警告信息（PRD 搜索失败）
    assert len(result.metadata.get('warnings', [])) > 0
