"""
TestCaseOptimizationWorkflow 单元测试
"""

import pytest
from unittest.mock import AsyncMock
from app.workflow.test_case_optimization_workflow import TestCaseOptimizationWorkflow
from app.workflow.base import WorkflowResult
from app.tool.retrieval_tools import SearchTestCaseTool, SearchPRDTool
from app.tool.validation_tools import ValidateCoverageTool, CheckQualityTool
from app.tool.generation_tools import FormatTestCaseTool
from app.agent.requirement_analysis_agent import RequirementAnalysisAgent, AnalysisResult
from app.agent.test_design_agent import TestDesignAgent, TestCaseDesign


@pytest.fixture
def mock_search_testcase_tool():
    """创建模拟的 SearchTestCaseTool"""
    tool = AsyncMock(spec=SearchTestCaseTool)
    return tool


@pytest.fixture
def mock_search_prd_tool():
    """创建模拟的 SearchPRDTool"""
    tool = AsyncMock(spec=SearchPRDTool)
    return tool


@pytest.fixture
def mock_validate_coverage_tool():
    """创建模拟的 ValidateCoverageTool"""
    tool = AsyncMock(spec=ValidateCoverageTool)
    return tool


@pytest.fixture
def mock_check_quality_tool():
    """创建模拟的 CheckQualityTool"""
    tool = AsyncMock(spec=CheckQualityTool)
    return tool


@pytest.fixture
def mock_requirement_analysis_agent():
    """创建模拟的 RequirementAnalysisAgent"""
    agent = AsyncMock(spec=RequirementAnalysisAgent)
    return agent


@pytest.fixture
def mock_test_design_agent():
    """创建模拟的 TestDesignAgent"""
    agent = AsyncMock(spec=TestDesignAgent)
    return agent


@pytest.fixture
def mock_format_testcase_tool():
    """创建模拟的 FormatTestCaseTool"""
    tool = AsyncMock(spec=FormatTestCaseTool)
    return tool


@pytest.fixture
def workflow(
    mock_search_testcase_tool,
    mock_search_prd_tool,
    mock_validate_coverage_tool,
    mock_check_quality_tool,
    mock_requirement_analysis_agent,
    mock_test_design_agent,
    mock_format_testcase_tool
):
    """创建 TestCaseOptimizationWorkflow 实例"""
    return TestCaseOptimizationWorkflow(
        search_testcase_tool=mock_search_testcase_tool,
        search_prd_tool=mock_search_prd_tool,
        validate_coverage_tool=mock_validate_coverage_tool,
        check_quality_tool=mock_check_quality_tool,
        requirement_analysis_agent=mock_requirement_analysis_agent,
        test_design_agent=mock_test_design_agent,
        format_testcase_tool=mock_format_testcase_tool
    )


def test_workflow_properties(workflow):
    """测试工作流属性"""
    assert workflow.name == "test_case_optimization"
    assert workflow.description == "优化和补全现有测试用例"


@pytest.mark.asyncio
async def test_execute_success(
    workflow,
    mock_search_testcase_tool,
    mock_search_prd_tool,
    mock_validate_coverage_tool,
    mock_check_quality_tool,
    mock_requirement_analysis_agent,
    mock_test_design_agent,
    mock_format_testcase_tool
):
    """测试成功的工作流执行"""
    # 准备测试数据
    requirement = "用户登录功能"
    context = {
        'project_id': 'test-project-123',
        'existing_cases': [
            {
                'id': 'case1',
                'title': '用户登录测试',
                'preconditions': '用户已注册',
                'steps': [{'step': '输入用户名密码', 'expected': '登录成功'}],
                'expected_result': '登录成功',
                'priority': 'P0',
                'type': 'functional'
            }
        ]
    }
    
    # 模拟质量检查结果
    mock_check_quality_tool.execute.return_value = ['标题过于简单']
    
    # 模拟 PRD 搜索结果
    mock_search_prd_tool.execute.return_value = [
        {'id': 'prd1', 'title': '用户认证系统', 'content': '...'}
    ]
    
    # 模拟需求分析结果
    analysis_result = AnalysisResult(
        functional_points=['用户登录', '密码验证'],
        business_rules=['密码必须加密'],
        input_specs={'username': 'string', 'password': 'string'},
        output_specs={'token': 'string'},
        exception_conditions=['用户名不存在', '密码错误'],
        constraints=['登录失败3次锁定账户']
    )
    mock_requirement_analysis_agent.analyze.return_value = analysis_result
    
    # 模拟覆盖率检查结果
    mock_validate_coverage_tool.execute.return_value = {
        'missing_coverage': ['异常：用户名不存在', '边界：密码长度']
    }
    
    # 模拟测试设计结果
    test_design = TestCaseDesign(
        title='用户名不存在测试',
        preconditions='系统正常运行',
        steps=['输入不存在的用户名', '点击登录'],
        expected_result='提示用户名不存在',
        priority='P1',
        type='exception',
        rationale='验证异常处理'
    )
    mock_test_design_agent.design_tests.return_value = [test_design]
    
    # 模拟格式化结果
    mock_format_testcase_tool.execute.return_value = [test_design.to_dict()]
    
    # 执行工作流
    result = await workflow.execute(requirement, context)
    
    # 验证结果
    assert isinstance(result, WorkflowResult)
    assert result.success is True
    assert result.error is None
    
    # 验证返回的数据
    assert 'quality_issues' in result.data
    assert 'missing_points' in result.data
    assert 'supplementary_cases' in result.data
    assert 'optimization_suggestions' in result.data
    
    # 验证质量问题
    quality_issues = result.data['quality_issues']
    assert len(quality_issues) == 1
    assert quality_issues[0]['case_id'] == 'case1'
    
    # 验证缺失测试点
    missing_points = result.data['missing_points']
    assert len(missing_points) == 2
    
    # 验证补充用例
    supplementary_cases = result.data['supplementary_cases']
    assert len(supplementary_cases) == 1
    
    # 验证优化建议
    suggestions = result.data['optimization_suggestions']
    assert len(suggestions) > 0
    
    # 验证元数据
    assert result.metadata['existing_cases_count'] == 1
    assert result.metadata['quality_issues_count'] == 1
    assert result.metadata['missing_points_count'] == 2
    assert result.metadata['supplementary_cases_count'] == 1


@pytest.mark.asyncio
async def test_execute_missing_project_id(workflow):
    """测试缺少 project_id 参数"""
    requirement = "用户登录功能"
    context = {}  # 缺少 project_id
    
    # 执行工作流
    result = await workflow.execute(requirement, context)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 project_id 参数" in result.error


@pytest.mark.asyncio
async def test_execute_no_context(workflow):
    """测试没有上下文"""
    requirement = "用户登录功能"
    
    # 执行工作流
    result = await workflow.execute(requirement, None)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 project_id 参数" in result.error


@pytest.mark.asyncio
async def test_execute_missing_requirement(workflow):
    """测试缺少 requirement 参数"""
    context = {'project_id': 'test-project-123'}
    
    # 执行工作流
    result = await workflow.execute("", context)
    
    # 验证结果
    assert result.success is False
    assert "缺少必需的 requirement 参数" in result.error


@pytest.mark.asyncio
async def test_execute_no_existing_cases_provided(
    workflow,
    mock_search_testcase_tool,
    mock_search_prd_tool,
    mock_requirement_analysis_agent,
    mock_validate_coverage_tool,
    mock_test_design_agent,
    mock_format_testcase_tool
):
    """测试没有提供现有用例（通过搜索获取）"""
    requirement = "用户登录功能"
    context = {'project_id': 'test-project-123'}
    
    # 模拟搜索测试用例结果
    mock_search_testcase_tool.execute.return_value = [
        {
            'id': 'case1',
            'title': '用户登录测试',
            'preconditions': '用户已注册',
            'steps': [{'step': '输入用户名密码', 'expected': '登录成功'}],
            'expected_result': '登录成功',
            'priority': 'P0',
            'type': 'functional'
        }
    ]
    
    # 模拟其他工具
    mock_search_prd_tool.execute.return_value = []
    mock_requirement_analysis_agent.analyze.return_value = AnalysisResult(
        functional_points=['用户登录'],
        business_rules=[],
        input_specs={},
        output_specs={},
        exception_conditions=[],
        constraints=[]
    )
    mock_validate_coverage_tool.execute.return_value = {'missing_coverage': []}
    mock_test_design_agent.design_tests.return_value = []
    mock_format_testcase_tool.execute.return_value = []
    
    # 执行工作流
    result = await workflow.execute(requirement, context)
    
    # 验证结果
    assert result.success is True
    assert result.metadata['existing_cases_count'] == 1
    
    # 验证搜索工具被调用
    mock_search_testcase_tool.execute.assert_called_once()


@pytest.mark.asyncio
async def test_execute_no_existing_cases_found(
    workflow,
    mock_search_testcase_tool
):
    """测试没有找到现有用例"""
    requirement = "用户登录功能"
    context = {'project_id': 'test-project-123'}
    
    # 模拟搜索返回空列表
    mock_search_testcase_tool.execute.return_value = []
    
    # 执行工作流
    result = await workflow.execute(requirement, context)
    
    # 验证结果（应该成功，但返回建议）
    assert result.success is True
    assert result.metadata['existing_cases_count'] == 0
    assert len(result.data['optimization_suggestions']) > 0
    assert "没有找到现有测试用例" in result.data['optimization_suggestions'][0]


@pytest.mark.asyncio
async def test_execute_quality_check_failure(
    workflow,
    mock_search_prd_tool,
    mock_check_quality_tool,
    mock_requirement_analysis_agent,
    mock_validate_coverage_tool,
    mock_test_design_agent,
    mock_format_testcase_tool
):
    """测试质量检查失败"""
    requirement = "用户登录功能"
    context = {
        'project_id': 'test-project-123',
        'existing_cases': [
            {'id': 'case1', 'title': '测试1', 'steps': [], 'expected_result': ''}
        ]
    }
    
    # 模拟质量检查抛出异常
    mock_check_quality_tool.execute.side_effect = Exception("质量检查失败")
    
    # 模拟其他工具
    mock_search_prd_tool.execute.return_value = []
    mock_requirement_analysis_agent.analyze.return_value = AnalysisResult(
        functional_points=[],
        business_rules=[],
        input_specs={},
        output_specs={},
        exception_conditions=[],
        constraints=[]
    )
    mock_validate_coverage_tool.execute.return_value = {'missing_coverage': []}
    mock_test_design_agent.design_tests.return_value = []
    mock_format_testcase_tool.execute.return_value = []
    
    # 执行工作流（应该继续执行）
    result = await workflow.execute(requirement, context)
    
    # 验证结果（应该成功，但有警告）
    assert result.success is True
    assert "质量检查失败" in result.metadata['warnings'][0]


@pytest.mark.asyncio
async def test_execute_requirement_analysis_failure(
    workflow,
    mock_search_prd_tool,
    mock_check_quality_tool,
    mock_requirement_analysis_agent
):
    """测试需求分析失败"""
    requirement = "用户登录功能"
    context = {
        'project_id': 'test-project-123',
        'existing_cases': [
            {'id': 'case1', 'title': '测试1', 'steps': [], 'expected_result': ''}
        ]
    }
    
    # 模拟工具
    mock_check_quality_tool.execute.return_value = []
    mock_search_prd_tool.execute.return_value = []
    
    # 模拟需求分析失败
    mock_requirement_analysis_agent.analyze.side_effect = Exception("需求分析失败")
    
    # 执行工作流
    result = await workflow.execute(requirement, context)
    
    # 验证结果（应该失败）
    assert result.success is False
    assert "需求分析失败" in result.error


@pytest.mark.asyncio
async def test_execute_no_missing_points(
    workflow,
    mock_search_prd_tool,
    mock_check_quality_tool,
    mock_requirement_analysis_agent,
    mock_validate_coverage_tool,
    mock_test_design_agent,
    mock_format_testcase_tool
):
    """测试没有缺失的测试点"""
    requirement = "用户登录功能"
    context = {
        'project_id': 'test-project-123',
        'existing_cases': [
            {'id': 'case1', 'title': '测试1', 'steps': [], 'expected_result': ''}
        ]
    }
    
    # 模拟工具
    mock_check_quality_tool.execute.return_value = []
    mock_search_prd_tool.execute.return_value = []
    mock_requirement_analysis_agent.analyze.return_value = AnalysisResult(
        functional_points=[],
        business_rules=[],
        input_specs={},
        output_specs={},
        exception_conditions=[],
        constraints=[]
    )
    
    # 模拟没有缺失的测试点
    mock_validate_coverage_tool.execute.return_value = {'missing_coverage': []}
    
    # 执行工作流
    result = await workflow.execute(requirement, context)
    
    # 验证结果
    assert result.success is True
    assert len(result.data['missing_points']) == 0
    assert len(result.data['supplementary_cases']) == 0
    
    # 验证测试设计 Agent 没有被调用
    mock_test_design_agent.design_tests.assert_not_called()


@pytest.mark.asyncio
async def test_execute_generate_supplements_failure(
    workflow,
    mock_search_prd_tool,
    mock_check_quality_tool,
    mock_requirement_analysis_agent,
    mock_validate_coverage_tool,
    mock_test_design_agent,
    mock_format_testcase_tool
):
    """测试生成补充用例失败"""
    requirement = "用户登录功能"
    context = {
        'project_id': 'test-project-123',
        'existing_cases': [
            {'id': 'case1', 'title': '测试1', 'steps': [], 'expected_result': ''}
        ]
    }
    
    # 模拟工具
    mock_check_quality_tool.execute.return_value = []
    mock_search_prd_tool.execute.return_value = []
    mock_requirement_analysis_agent.analyze.return_value = AnalysisResult(
        functional_points=[],
        business_rules=[],
        input_specs={},
        output_specs={},
        exception_conditions=[],
        constraints=[]
    )
    mock_validate_coverage_tool.execute.return_value = {
        'missing_coverage': ['缺失点1', '缺失点2']
    }
    
    # 模拟生成补充用例失败
    mock_test_design_agent.design_tests.side_effect = Exception("生成失败")
    
    # 执行工作流（应该继续执行）
    result = await workflow.execute(requirement, context)
    
    # 验证结果（应该成功，但有警告）
    assert result.success is True
    assert len(result.data['supplementary_cases']) == 0
    assert "生成补充测试用例失败" in result.metadata['warnings'][0]


def test_generate_optimization_suggestions_with_quality_issues(workflow):
    """测试生成优化建议（有质量问题）"""
    quality_issues = [
        {'case_id': 'case1', 'issues': ['标题: 标题过于简单', '步骤: 步骤不清晰']},
        {'case_id': 'case2', 'issues': ['标题: 标题过于简单']}
    ]
    missing_points = []
    
    suggestions = workflow._generate_optimization_suggestions(
        quality_issues=quality_issues,
        missing_points=missing_points,
        existing_cases_count=2,
        supplementary_cases_count=0
    )
    
    assert len(suggestions) > 0
    assert any('质量问题' in s for s in suggestions)
    assert any('标题' in s for s in suggestions)


def test_generate_optimization_suggestions_with_missing_points(workflow):
    """测试生成优化建议（有缺失测试点）"""
    quality_issues = []
    missing_points = ['功能：用户注册', '异常：密码错误', '边界：用户名长度']
    
    suggestions = workflow._generate_optimization_suggestions(
        quality_issues=quality_issues,
        missing_points=missing_points,
        existing_cases_count=5,
        supplementary_cases_count=3
    )
    
    assert len(suggestions) > 0
    assert any('缺失的测试点' in s for s in suggestions)
    assert any('功能测试点' in s for s in suggestions)
    assert any('异常测试点' in s for s in suggestions)
    assert any('边界值测试点' in s for s in suggestions)


def test_generate_optimization_suggestions_perfect_cases(workflow):
    """测试生成优化建议（完美的测试用例）"""
    quality_issues = []
    missing_points = []
    
    suggestions = workflow._generate_optimization_suggestions(
        quality_issues=quality_issues,
        missing_points=missing_points,
        existing_cases_count=10,
        supplementary_cases_count=0
    )
    
    assert len(suggestions) > 0
    assert any('质量良好' in s for s in suggestions)


def test_generate_optimization_suggestions_few_cases(workflow):
    """测试生成优化建议（测试用例数量少）"""
    quality_issues = []
    missing_points = []
    
    suggestions = workflow._generate_optimization_suggestions(
        quality_issues=quality_issues,
        missing_points=missing_points,
        existing_cases_count=3,
        supplementary_cases_count=0
    )
    
    assert len(suggestions) > 0
    assert any('数量较少' in s for s in suggestions)
