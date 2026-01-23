"""
QualityReviewAgent 单元测试
"""

import pytest
from unittest.mock import AsyncMock
from app.agent.quality_review_agent import (
    QualityReviewAgent,
    ReviewResult,
)
from app.agent.requirement_analysis_agent import AnalysisResult
from app.agent.test_design_agent import TestCaseDesign
from app.integration.brconnector_client import BRConnectorError


@pytest.fixture
def mock_brconnector():
    """创建 mock BRConnector 客户端"""
    client = AsyncMock()
    return client


@pytest.fixture
def agent(mock_brconnector):
    """创建 QualityReviewAgent 实例"""
    return QualityReviewAgent(mock_brconnector)


@pytest.fixture
def sample_analysis():
    """创建示例需求分析结果"""
    return AnalysisResult(
        functional_points=["用户登录", "密码验证"],
        business_rules=["密码长度至少 8 位"],
        input_specs={"username": {"type": "string"}, "password": {"type": "string"}},
        output_specs={"token": {"type": "string"}},
        exception_conditions=["用户名不存在", "密码错误"],
        constraints=["响应时间 < 2 秒"]
    )


@pytest.fixture
def sample_test_cases():
    """创建示例测试用例"""
    return [
        TestCaseDesign(
            title="测试有效用户登录",
            preconditions="用户已注册",
            steps=["输入用户名", "输入密码", "点击登录"],
            expected_result="登录成功",
            priority="high",
            type="functional",
            rationale="验证主流程"
        ),
        TestCaseDesign(
            title="测试密码错误",
            preconditions="用户已注册",
            steps=["输入用户名", "输入错误密码", "点击登录"],
            expected_result="显示错误提示",
            priority="high",
            type="exception",
            rationale="验证异常处理"
        ),
        TestCaseDesign(
            title="测试边界值",
            preconditions="系统正常",
            steps=["输入最小长度密码"],
            expected_result="接受输入",
            priority="medium",
            type="boundary",
            rationale="验证边界条件"
        )
    ]


@pytest.mark.asyncio
async def test_review_basic(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试基本质量审查"""
    # 准备 mock 响应
    mock_response = """```json
{
  "coverage_score": 85,
  "issues": ["缺少性能测试", "边界值测试不够全面"],
  "suggestions": ["添加并发登录测试", "增加密码长度边界测试"],
  "approved_cases": [0, 1, 2],
  "rejected_cases": [],
  "overall_quality": "good"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(
        sample_test_cases,
        "用户应该能够使用用户名和密码登录",
        sample_analysis
    )
    
    # 验证结果
    assert isinstance(result, ReviewResult)
    assert result.coverage_score == 85
    assert len(result.issues) == 2
    assert len(result.suggestions) == 2
    assert len(result.approved_cases) == 3
    assert len(result.rejected_cases) == 0
    assert result.overall_quality == "good"
    
    # 验证 LLM 被调用
    mock_brconnector.chat_simple.assert_called_once()


@pytest.mark.asyncio
async def test_review_with_rejected_cases(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试包含拒绝用例的审查"""
    mock_response = """```json
{
  "coverage_score": 70,
  "issues": ["测试用例 2 步骤不够详细"],
  "suggestions": ["细化测试步骤"],
  "approved_cases": [0, 1],
  "rejected_cases": [[2, "步骤描述不清晰"]],
  "overall_quality": "good"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 验证结果
    assert isinstance(result, ReviewResult)
    assert result.coverage_score == 70
    assert len(result.approved_cases) == 2
    assert len(result.rejected_cases) == 1
    assert result.rejected_cases[0] == (2, "步骤描述不清晰")


@pytest.mark.asyncio
async def test_review_excellent_quality(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试优秀质量的审查"""
    mock_response = """```json
{
  "coverage_score": 95,
  "issues": [],
  "suggestions": ["可以考虑添加更多边缘情况"],
  "approved_cases": [0, 1, 2],
  "rejected_cases": [],
  "overall_quality": "excellent"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 验证结果
    assert result.coverage_score == 95
    assert result.overall_quality == "excellent"
    assert len(result.issues) == 0


@pytest.mark.asyncio
async def test_review_needs_improvement(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试需要改进的审查"""
    mock_response = """```json
{
  "coverage_score": 50,
  "issues": ["覆盖率不足", "缺少异常测试", "缺少边界测试"],
  "suggestions": ["增加异常场景", "增加边界值测试", "增加性能测试"],
  "approved_cases": [0],
  "rejected_cases": [[1, "步骤不完整"], [2, "预期结果不明确"]],
  "overall_quality": "needs_improvement"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 验证结果
    assert result.coverage_score == 50
    assert result.overall_quality == "needs_improvement"
    assert len(result.issues) == 3
    assert len(result.suggestions) == 3
    assert len(result.approved_cases) == 1
    assert len(result.rejected_cases) == 2


@pytest.mark.asyncio
async def test_review_without_markdown_code_block(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试解析不带 markdown 代码块的 JSON 响应"""
    # 直接返回 JSON（不带代码块）
    mock_response = """{
  "coverage_score": 80,
  "issues": ["问题1"],
  "suggestions": ["建议1"],
  "approved_cases": [0, 1, 2],
  "rejected_cases": [],
  "overall_quality": "good"
}"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 验证结果
    assert isinstance(result, ReviewResult)
    assert result.coverage_score == 80


@pytest.mark.asyncio
async def test_review_with_missing_fields(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试处理缺少字段的响应"""
    # 返回不完整的 JSON（缺少某些字段）
    mock_response = """```json
{
  "coverage_score": 75,
  "approved_cases": [0, 1]
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 验证结果 - 缺少的字段应该有默认值
    assert isinstance(result, ReviewResult)
    assert result.coverage_score == 75
    assert result.issues == []  # 默认空列表
    assert result.suggestions == []  # 默认空列表
    assert result.rejected_cases == []  # 默认空列表
    assert result.overall_quality == "good"  # 根据评分推断


@pytest.mark.asyncio
async def test_review_quality_inference_from_score(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试根据评分推断质量等级"""
    # 测试高分（应该推断为 excellent）
    mock_response = """```json
{
  "coverage_score": 92,
  "issues": [],
  "suggestions": [],
  "approved_cases": [0, 1, 2],
  "rejected_cases": []
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    assert result.overall_quality == "excellent"
    
    # 测试中等分数（应该推断为 good）
    mock_response = """```json
{
  "coverage_score": 75,
  "issues": [],
  "suggestions": [],
  "approved_cases": [0, 1],
  "rejected_cases": []
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    assert result.overall_quality == "good"
    
    # 测试低分（应该推断为 needs_improvement）
    mock_response = """```json
{
  "coverage_score": 60,
  "issues": ["问题"],
  "suggestions": ["建议"],
  "approved_cases": [0],
  "rejected_cases": []
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    assert result.overall_quality == "needs_improvement"


@pytest.mark.asyncio
async def test_review_coverage_score_bounds(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试覆盖率评分边界处理"""
    # 测试超过 100 的评分
    mock_response = """```json
{
  "coverage_score": 150,
  "issues": [],
  "suggestions": [],
  "approved_cases": [0, 1, 2],
  "rejected_cases": [],
  "overall_quality": "excellent"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    assert result.coverage_score == 100  # 应该被限制在 100
    
    # 测试负数评分
    mock_response = """```json
{
  "coverage_score": -10,
  "issues": [],
  "suggestions": [],
  "approved_cases": [],
  "rejected_cases": [],
  "overall_quality": "needs_improvement"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    assert result.coverage_score == 0  # 应该被限制在 0


@pytest.mark.asyncio
async def test_review_quality_normalization(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试质量等级的标准化"""
    mock_response = """```json
{
  "coverage_score": 85,
  "issues": [],
  "suggestions": [],
  "approved_cases": [0, 1, 2],
  "rejected_cases": [],
  "overall_quality": "GOOD"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 验证结果 - 质量等级应该被标准化为小写
    assert result.overall_quality == "good"


@pytest.mark.asyncio
async def test_review_llm_error(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试 LLM 调用失败的情况"""
    # Mock LLM 抛出错误
    mock_brconnector.chat_simple.side_effect = BRConnectorError("API 调用失败")
    
    # 执行审查应该抛出异常
    with pytest.raises(BRConnectorError):
        await agent.review(sample_test_cases, "测试需求", sample_analysis)


@pytest.mark.asyncio
async def test_review_invalid_json_response(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试无效 JSON 响应的处理"""
    # 返回无效的 JSON
    mock_response = "这不是有效的 JSON 响应"
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查应该抛出 ValueError
    with pytest.raises(ValueError, match="无法解析 LLM 响应为 JSON"):
        await agent.review(sample_test_cases, "测试需求", sample_analysis)


@pytest.mark.asyncio
async def test_review_result_to_dict(agent, mock_brconnector, sample_test_cases, sample_analysis):
    """测试 ReviewResult 转换为字典"""
    mock_response = """```json
{
  "coverage_score": 85,
  "issues": ["问题1"],
  "suggestions": ["建议1"],
  "approved_cases": [0, 1],
  "rejected_cases": [[2, "原因"]],
  "overall_quality": "good"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行审查
    result = await agent.review(sample_test_cases, "测试需求", sample_analysis)
    
    # 转换为字典
    result_dict = result.to_dict()
    
    # 验证字典结构
    assert isinstance(result_dict, dict)
    assert 'coverage_score' in result_dict
    assert 'issues' in result_dict
    assert 'suggestions' in result_dict
    assert result_dict['coverage_score'] == 85
    assert result_dict['overall_quality'] == "good"


def test_review_result_from_dict():
    """测试从字典创建 ReviewResult"""
    data = {
        'coverage_score': 90,
        'issues': ["问题1", "问题2"],
        'suggestions': ["建议1"],
        'approved_cases': [0, 1, 2],
        'rejected_cases': [[3, "拒绝原因"]],
        'overall_quality': 'excellent'
    }
    
    # 从字典创建
    result = ReviewResult.from_dict(data)
    
    # 验证结果
    assert isinstance(result, ReviewResult)
    assert result.coverage_score == 90
    assert len(result.issues) == 2
    assert len(result.approved_cases) == 3
    assert len(result.rejected_cases) == 1
    assert result.rejected_cases[0] == (3, "拒绝原因")
    assert result.overall_quality == 'excellent'
