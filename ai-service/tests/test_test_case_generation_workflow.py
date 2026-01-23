"""
测试用例生成工作流的单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.workflow.test_case_generation_workflow import TestCaseGenerationWorkflow
from app.agent.requirement_analysis_agent import AnalysisResult
from app.agent.test_design_agent import TestCaseDesign
from app.agent.quality_review_agent import ReviewResult


@pytest.fixture
def mock_requirement_agent():
    """模拟需求分析 Agent"""
    agent = AsyncMock()
    agent.analyze.return_value = AnalysisResult(
        functional_points=["用户登录", "密码验证"],
        business_rules=["密码长度至少 8 位"],
        input_specs={"username": {"type": "string"}, "password": {"type": "string"}},
        output_specs={"token": {"type": "string"}},
        exception_conditions=["用户名不存在", "密码错误"],
        constraints=["登录失败 3 次锁定账户"]
    )
    return agent


@pytest.fixture
def mock_test_design_agent():
    """模拟测试设计 Agent"""
    agent = AsyncMock()
    agent.design_tests.return_value = [
        TestCaseDesign(
            title="测试有效用户登录",
            preconditions="用户已注册",
            steps=["输入用户名", "输入密码", "点击登录"],
            expected_result="登录成功，返回 token",
            priority="high",
            type="functional",
            rationale="主流程测试"
        ),
        TestCaseDesign(
            title="测试密码错误",
            preconditions="用户已注册",
            steps=["输入用户名", "输入错误密码", "点击登录"],
            expected_result="提示密码错误",
            priority="high",
            type="exception",
            rationale="异常流程测试"
        )
    ]
    return agent


@pytest.fixture
def mock_quality_review_agent():
    """模拟质量审查 Agent"""
    agent = AsyncMock()
    agent.review.return_value = ReviewResult(
        coverage_score=90,
        issues=[],
        suggestions=["可以添加边界值测试"],
        approved_cases=[0, 1],
        rejected_cases=[],
        overall_quality="excellent"
    )
    return agent


@pytest.fixture
def mock_search_prd_tool():
    """模拟 PRD 搜索工具"""
    tool = AsyncMock()
    tool.execute.return_value = [
        {"id": "1", "title": "用户认证系统", "content": "用户登录功能..."}
    ]
    return tool


@pytest.fixture
def mock_search_testcase_tool():
    """模拟测试用例搜索工具"""
    tool = AsyncMock()
    tool.execute.return_value = [
        {"id": "1", "title": "测试用户登录", "steps": ["输入用户名", "输入密码"]}
    ]
    return tool


@pytest.fixture
def mock_format_tool():
    """模拟格式化工具"""
    tool = AsyncMock()
    tool.execute.return_value = [
        {
            "title": "测试有效用户登录",
            "preconditions": "用户已注册",
            "steps": [
                {"step_number": 1, "action": "输入用户名", "expected": ""},
                {"step_number": 2, "action": "输入密码", "expected": ""},
                {"step_number": 3, "action": "点击登录", "expected": ""}
            ],
            "expected_result": "登录成功，返回 token",
            "priority": "high",
            "type": "functional"
        },
        {
            "title": "测试密码错误",
            "preconditions": "用户已注册",
            "steps": [
                {"step_number": 1, "action": "输入用户名", "expected": ""},
                {"step_number": 2, "action": "输入错误密码", "expected": ""},
                {"step_number": 3, "action": "点击登录", "expected": ""}
            ],
            "expected_result": "提示密码错误",
            "priority": "high",
            "type": "exception"
        }
    ]
    return tool


@pytest.fixture
def workflow(
    mock_requirement_agent,
    mock_test_design_agent,
    mock_quality_review_agent,
    mock_search_prd_tool,
    mock_search_testcase_tool,
    mock_format_tool
):
    """创建工作流实例"""
    return TestCaseGenerationWorkflow(
        requirement_agent=mock_requirement_agent,
        test_design_agent=mock_test_design_agent,
        quality_review_agent=mock_quality_review_agent,
        search_prd_tool=mock_search_prd_tool,
        search_testcase_tool=mock_search_testcase_tool,
        format_tool=mock_format_tool
    )


@pytest.mark.asyncio
async def test_workflow_name_and_description(workflow):
    """测试工作流名称和描述"""
    assert workflow.name == "test_case_generation"
    assert "测试用例" in workflow.description


@pytest.mark.asyncio
async def test_workflow_success(workflow):
    """测试工作流成功执行"""
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    assert result.success is True
    assert result.error is None
    assert "test_cases" in result.data
    assert "analysis" in result.data
    assert "review" in result.data
    
    # 验证生成了 2 个测试用例
    assert len(result.data["test_cases"]) == 2
    
    # 验证元数据
    assert result.metadata["coverage_score"] == 90
    assert result.metadata["total_generated"] == 2
    assert result.metadata["approved_count"] == 2


@pytest.mark.asyncio
async def test_workflow_missing_project_id(workflow):
    """测试缺少 project_id 参数"""
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={}
    )
    
    assert result.success is False
    assert "project_id" in result.error


@pytest.mark.asyncio
async def test_workflow_retrieval_failure(
    workflow,
    mock_search_prd_tool,
    mock_search_testcase_tool
):
    """测试检索失败时的处理"""
    # 模拟检索失败
    mock_search_prd_tool.execute.side_effect = Exception("检索失败")
    mock_search_testcase_tool.execute.side_effect = Exception("检索失败")
    
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    # 工作流应该继续执行
    assert result.success is True
    assert len(result.metadata["warnings"]) == 2
    assert "无法检索历史 PRD" in result.metadata["warnings"][0]
    assert "无法检索历史测试用例" in result.metadata["warnings"][1]


@pytest.mark.asyncio
async def test_workflow_requirement_analysis_failure(
    workflow,
    mock_requirement_agent
):
    """测试需求分析失败"""
    mock_requirement_agent.analyze.side_effect = Exception("分析失败")
    
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    assert result.success is False
    assert "需求分析失败" in result.error
    assert result.metadata["step"] == "requirement_analysis"


@pytest.mark.asyncio
async def test_workflow_test_design_failure(
    workflow,
    mock_test_design_agent
):
    """测试测试设计失败"""
    mock_test_design_agent.design_tests.side_effect = Exception("设计失败")
    
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    assert result.success is False
    assert "测试设计失败" in result.error
    assert result.metadata["step"] == "test_design"


@pytest.mark.asyncio
async def test_workflow_quality_review_failure(
    workflow,
    mock_quality_review_agent
):
    """测试质量审查失败时的处理"""
    mock_quality_review_agent.review.side_effect = Exception("审查失败")
    
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    # 工作流应该继续执行，批准所有测试用例
    assert result.success is True
    assert len(result.metadata["warnings"]) > 0
    assert "质量审查失败" in result.metadata["warnings"][-1]
    assert result.metadata["coverage_score"] == 0


@pytest.mark.asyncio
async def test_workflow_formatting_failure(
    workflow,
    mock_format_tool
):
    """测试格式化失败"""
    mock_format_tool.execute.side_effect = Exception("格式化失败")
    
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    assert result.success is False
    assert "格式化失败" in result.error
    assert result.metadata["step"] == "formatting"


@pytest.mark.asyncio
async def test_workflow_with_custom_limits(workflow):
    """测试自定义检索数量限制"""
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={
            "project_id": 1,
            "historical_prd_limit": 10,
            "historical_case_limit": 15
        }
    )
    
    assert result.success is True
    
    # 验证调用了正确的参数
    workflow.search_prd_tool.execute.assert_called_once()
    call_kwargs = workflow.search_prd_tool.execute.call_args.kwargs
    assert call_kwargs["limit"] == 10
    
    workflow.search_testcase_tool.execute.assert_called_once()
    call_kwargs = workflow.search_testcase_tool.execute.call_args.kwargs
    assert call_kwargs["limit"] == 15


@pytest.mark.asyncio
async def test_workflow_partial_approval(
    workflow,
    mock_quality_review_agent,
    mock_format_tool
):
    """测试部分测试用例被批准"""
    # 只批准第一个测试用例
    mock_quality_review_agent.review.return_value = ReviewResult(
        coverage_score=60,
        issues=["第二个测试用例步骤不完整"],
        suggestions=[],
        approved_cases=[0],
        rejected_cases=[(1, "步骤不完整")],
        overall_quality="needs_improvement"
    )
    
    # 格式化工具只返回批准的测试用例
    mock_format_tool.execute.return_value = [
        {
            "title": "测试有效用户登录",
            "preconditions": "用户已注册",
            "steps": [
                {"step_number": 1, "action": "输入用户名", "expected": ""},
                {"step_number": 2, "action": "输入密码", "expected": ""},
                {"step_number": 3, "action": "点击登录", "expected": ""}
            ],
            "expected_result": "登录成功，返回 token",
            "priority": "high",
            "type": "functional"
        }
    ]
    
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    assert result.success is True
    assert len(result.data["test_cases"]) == 1
    assert result.metadata["approved_count"] == 1
    assert result.metadata["rejected_count"] == 1


@pytest.mark.asyncio
async def test_workflow_result_to_dict(workflow):
    """测试结果转换为字典"""
    result = await workflow.execute(
        requirement="实现用户登录功能",
        context={"project_id": 1}
    )
    
    result_dict = result.to_dict()
    
    assert isinstance(result_dict, dict)
    assert "success" in result_dict
    assert "data" in result_dict
    assert "error" in result_dict
    assert "metadata" in result_dict
