"""
属性测试：测试用例生成

Feature: ai-test-assistant
Property 9: Test Case Generation

验证：对于任何需求描述，TestCaseGenerationWorkflow 应该生成至少一个包含所有必需字段的测试用例。

需求: 4.1
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock
from app.workflow.test_case_generation_workflow import TestCaseGenerationWorkflow
from app.agent.requirement_analysis_agent import RequirementAnalysisAgent, AnalysisResult
from app.agent.test_design_agent import TestDesignAgent, TestCaseDesign
from app.agent.quality_review_agent import QualityReviewAgent, ReviewResult


# 生成有效的需求描述策略
requirement_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),  # 大写、小写、数字、空格
        whitelist_characters='，。！？、：；（）【】《》""''',  # 中文标点
    ),
    min_size=10,
    max_size=500
).filter(lambda x: len(x.strip()) >= 10)  # 确保去除空格后至少10个字符


def create_mock_workflow():
    """创建模拟的 Workflow 及其依赖"""
    # 模拟 RequirementAnalysisAgent
    requirement_agent = AsyncMock(spec=RequirementAnalysisAgent)
    requirement_agent.analyze.return_value = AnalysisResult(
        functional_points=["功能点1", "功能点2"],
        business_rules=["业务规则1"],
        input_specs={"输入1": {"type": "string", "range": "1-100"}},
        output_specs={"输出1": {"type": "string"}},
        exception_conditions=["异常条件1"],
        constraints=["约束1"]
    )
    
    # 模拟 TestDesignAgent
    test_design_agent = AsyncMock(spec=TestDesignAgent)
    test_design_agent.design_tests.return_value = [
        TestCaseDesign(
            title="测试用例标题",
            preconditions="前置条件",
            steps=["步骤1", "步骤2", "步骤3"],
            expected_result="预期结果",
            priority="high",
            type="functional",
            rationale="测试理由"
        )
    ]
    
    # 模拟 QualityReviewAgent
    quality_review_agent = AsyncMock(spec=QualityReviewAgent)
    quality_review_agent.review.return_value = ReviewResult(
        coverage_score=85,
        issues=[],
        suggestions=[],
        approved_cases=[0],
        rejected_cases=[],
        overall_quality="good"
    )
    
    # 模拟 Tools
    search_prd_tool = AsyncMock()
    search_prd_tool.execute.return_value = []
    
    search_testcase_tool = AsyncMock()
    search_testcase_tool.execute.return_value = []
    
    format_tool = AsyncMock()
    format_tool.execute.return_value = [{
        "title": "测试用例标题",
        "preconditions": "前置条件",
        "steps": [
            {"step_number": 1, "action": "步骤1", "expected": ""},
            {"step_number": 2, "action": "步骤2", "expected": ""},
            {"step_number": 3, "action": "步骤3", "expected": ""}
        ],
        "expected_result": "预期结果",
        "priority": "high",
        "type": "functional"
    }]
    
    workflow = TestCaseGenerationWorkflow(
        requirement_agent=requirement_agent,
        test_design_agent=test_design_agent,
        quality_review_agent=quality_review_agent,
        search_prd_tool=search_prd_tool,
        search_testcase_tool=search_testcase_tool,
        format_tool=format_tool
    )
    
    return workflow


# Feature: ai-test-assistant, Property 9: Test Case Generation
@given(requirement_strategy)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_property_test_case_generation(requirement: str):
    """
    属性 9: 测试用例生成
    
    对于任何有效的需求描述，Workflow 应该：
    1. 成功执行
    2. 生成至少一个测试用例
    3. 测试用例包含所有必需字段
    """
    workflow = create_mock_workflow()
    
    # 执行工作流
    result = await workflow.execute(
        requirement=requirement,
        context={"project_id": 1}
    )
    
    # 验证结果不为空
    assert result is not None, "工作流结果不应为空"
    assert result.success is True, "工作流应该成功执行"
    assert result.data is not None, "工作流数据不应为空"
    assert "test_cases" in result.data, "数据中应包含 test_cases"
    
    # 验证至少生成一个测试用例
    test_cases = result.data["test_cases"]
    assert len(test_cases) >= 1, f"应该至少生成一个测试用例，实际生成了 {len(test_cases)} 个"
    
    # 验证第一个测试用例的结构
    test_case = test_cases[0]
    
    # 验证必需字段存在
    assert "title" in test_case, "测试用例必须包含 title 字段"
    assert "preconditions" in test_case, "测试用例必须包含 preconditions 字段"
    assert "steps" in test_case, "测试用例必须包含 steps 字段"
    assert "expected_result" in test_case, "测试用例必须包含 expected_result 字段"
    assert "priority" in test_case, "测试用例必须包含 priority 字段"
    assert "type" in test_case, "测试用例必须包含 type 字段"
    
    # 验证字段值非空
    assert len(test_case["title"]) > 0, "title 不应为空"
    assert len(test_case["preconditions"]) > 0, "preconditions 不应为空"
    assert len(test_case["steps"]) > 0, "steps 不应为空列表"
    assert len(test_case["expected_result"]) > 0, "expected_result 不应为空"
    
    # 验证 steps 结构
    for i, step in enumerate(test_case["steps"]):
        assert isinstance(step, dict), f"步骤 {i} 应该是字典类型"
        assert "step_number" in step, f"步骤 {i} 必须包含 step_number"
        assert "action" in step, f"步骤 {i} 必须包含 action"
        assert len(step["action"]) > 0, f"步骤 {i} 的 action 不应为空"


@pytest.mark.asyncio
async def test_property_test_case_generation_minimum_requirement():
    """测试最小有效需求"""
    workflow = create_mock_workflow()
    
    # 最小有效需求（10个字符）
    result = await workflow.execute(
        requirement="用户登录功能测试",
        context={"project_id": 1}
    )
    
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "test_cases" in result.data
    assert len(result.data["test_cases"]) >= 1


@pytest.mark.asyncio
async def test_property_test_case_generation_long_requirement():
    """测试长需求描述"""
    workflow = create_mock_workflow()
    
    # 长需求描述
    long_requirement = "用户登录功能需要支持多种登录方式，包括用户名密码登录、手机号验证码登录、第三方账号登录等。" * 10
    
    result = await workflow.execute(
        requirement=long_requirement,
        context={"project_id": 1}
    )
    
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "test_cases" in result.data
    assert len(result.data["test_cases"]) >= 1


@pytest.mark.asyncio
async def test_property_test_case_generation_chinese_requirement():
    """测试中文需求"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="实现用户注册功能，支持邮箱和手机号注册，需要验证码验证",
        context={"project_id": 1}
    )
    
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "test_cases" in result.data
    assert len(result.data["test_cases"]) >= 1
    
    test_case = result.data["test_cases"][0]
    assert "title" in test_case
    assert "steps" in test_case
    assert len(test_case["steps"]) > 0


@pytest.mark.asyncio
async def test_property_test_case_generation_english_requirement():
    """测试英文需求"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="Implement user authentication with username and password validation",
        context={"project_id": 1}
    )
    
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "test_cases" in result.data
    assert len(result.data["test_cases"]) >= 1


@pytest.mark.asyncio
async def test_property_test_case_generation_mixed_language():
    """测试中英文混合需求"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="实现 API 接口的 rate limiting 功能，限制每个用户每分钟最多调用 100 次",
        context={"project_id": 1}
    )
    
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "test_cases" in result.data
    assert len(result.data["test_cases"]) >= 1


@pytest.mark.asyncio
async def test_property_test_case_generation_with_special_characters():
    """测试包含特殊字符的需求"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="用户输入验证：支持 email@example.com 格式，密码长度 8-20 位，包含 !@#$% 等特殊字符",
        context={"project_id": 1}
    )
    
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "test_cases" in result.data
    assert len(result.data["test_cases"]) >= 1


@pytest.mark.asyncio
async def test_property_test_case_generation_metadata():
    """测试生成的元数据"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="测试用户权限管理功能",
        context={"project_id": 1}
    )
    
    # 验证元数据存在
    assert result is not None
    assert result.success is True
    assert result.metadata is not None
    assert "total_generated" in result.metadata
    assert "approved_count" in result.metadata
    assert result.metadata["total_generated"] >= 1
    assert result.metadata["approved_count"] >= 1


@pytest.mark.asyncio
async def test_property_test_case_generation_analysis_result():
    """测试需求分析结果"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="实现文件上传功能，支持图片和文档",
        context={"project_id": 1}
    )
    
    # 验证分析结果存在
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "analysis" in result.data
    
    analysis = result.data["analysis"]
    assert "functional_points" in analysis
    assert "business_rules" in analysis
    assert "input_specs" in analysis
    assert "output_specs" in analysis
    assert "exception_conditions" in analysis
    assert "constraints" in analysis


@pytest.mark.asyncio
async def test_property_test_case_generation_review_result():
    """测试质量审查结果"""
    workflow = create_mock_workflow()
    
    result = await workflow.execute(
        requirement="实现数据导出功能，支持 Excel 和 CSV 格式",
        context={"project_id": 1}
    )
    
    # 验证审查结果存在
    assert result is not None
    assert result.success is True
    assert result.data is not None
    assert "review" in result.data
    
    review = result.data["review"]
    assert "coverage_score" in review
    assert "issues" in review
    assert "suggestions" in review
    assert "approved_cases" in review
    assert "overall_quality" in review
    
    # 验证覆盖率分数在有效范围内
    assert 0 <= review["coverage_score"] <= 100
