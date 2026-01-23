"""
ImpactAnalysisAgent 单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agent.impact_analysis_agent import ImpactAnalysisAgent, ImpactReport
from app.integration.brconnector_client import BRConnectorError


@pytest.fixture
def mock_brconnector():
    """创建模拟的 BRConnector 客户端"""
    client = AsyncMock()
    return client


@pytest.fixture
def impact_agent(mock_brconnector):
    """创建 ImpactAnalysisAgent 实例"""
    return ImpactAnalysisAgent(mock_brconnector)


@pytest.mark.asyncio
async def test_analyze_impact_success(impact_agent, mock_brconnector):
    """测试成功的影响分析"""
    # 准备测试数据
    change_description = "新增用户权限管理功能"
    related_prds = [
        {"title": "用户管理 PRD", "content": "用户管理系统的需求文档..."},
        {"title": "权限系统 PRD", "content": "权限系统的需求文档..."}
    ]
    existing_test_cases = [
        {"title": "用户登录测试", "module": "用户管理", "priority": "P0"},
        {"title": "权限验证测试", "module": "权限系统", "priority": "P1"}
    ]
    
    # 模拟 LLM 响应
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": """```json
{
    "summary": "新增权限管理功能将影响用户管理和权限系统模块",
    "affected_modules": ["用户管理", "权限系统"],
    "affected_test_cases": [
        {
            "title": "用户登录测试",
            "reason": "需要验证新的权限检查逻辑",
            "action": "update"
        },
        {
            "title": "权限验证测试",
            "reason": "需要增加新权限类型的测试",
            "action": "update"
        }
    ],
    "risk_level": "medium",
    "recommendations": [
        "更新用户登录测试用例，增加权限检查",
        "为新权限类型添加测试用例"
    ],
    "change_type": "feature_add"
}
```"""
        }]
    }
    
    # 执行分析
    report = await impact_agent.analyze_impact(
        change_description=change_description,
        related_prds=related_prds,
        existing_test_cases=existing_test_cases
    )
    
    # 验证结果
    assert isinstance(report, ImpactReport)
    assert report.summary == "新增权限管理功能将影响用户管理和权限系统模块"
    assert len(report.affected_modules) == 2
    assert "用户管理" in report.affected_modules
    assert "权限系统" in report.affected_modules
    assert len(report.affected_test_cases) == 2
    assert report.risk_level == "medium"
    assert len(report.recommendations) == 2
    assert report.change_type == "feature_add"
    
    # 验证 LLM 调用
    mock_brconnector.chat.assert_called_once()
    call_args = mock_brconnector.chat.call_args
    assert call_args[1]['temperature'] == 0.3
    assert call_args[1]['max_tokens'] == 2000


@pytest.mark.asyncio
async def test_analyze_impact_without_context(impact_agent, mock_brconnector):
    """测试没有历史上下文的影响分析"""
    change_description = "修复用户登录 bug"
    
    # 模拟 LLM 响应
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": """```json
{
    "summary": "修复登录 bug，影响较小",
    "affected_modules": ["用户管理"],
    "affected_test_cases": [
        {
            "title": "用户登录测试",
            "reason": "需要验证 bug 修复",
            "action": "retest"
        }
    ],
    "risk_level": "low",
    "recommendations": ["重新测试用户登录功能"],
    "change_type": "bug_fix"
}
```"""
        }]
    }
    
    # 执行分析（不提供历史上下文）
    report = await impact_agent.analyze_impact(
        change_description=change_description
    )
    
    # 验证结果
    assert isinstance(report, ImpactReport)
    assert report.risk_level == "low"
    assert report.change_type == "bug_fix"
    assert len(report.affected_modules) == 1


@pytest.mark.asyncio
async def test_analyze_impact_llm_error(impact_agent, mock_brconnector):
    """测试 LLM 调用失败"""
    change_description = "新增功能"
    
    # 模拟 LLM 错误
    mock_brconnector.chat.side_effect = BRConnectorError("API 调用失败")
    
    # 执行分析应该抛出异常
    with pytest.raises(BRConnectorError):
        await impact_agent.analyze_impact(change_description=change_description)


@pytest.mark.asyncio
async def test_analyze_impact_invalid_json(impact_agent, mock_brconnector):
    """测试无效的 JSON 响应"""
    change_description = "新增功能"
    
    # 模拟无效的 JSON 响应
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": "这不是有效的 JSON"
        }]
    }
    
    # 执行分析应该抛出 ValueError
    with pytest.raises(ValueError, match="无法解析 LLM 响应"):
        await impact_agent.analyze_impact(change_description=change_description)


@pytest.mark.asyncio
async def test_analyze_impact_missing_fields(impact_agent, mock_brconnector):
    """测试缺少必需字段的响应"""
    change_description = "新增功能"
    
    # 模拟缺少字段的响应
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": """```json
{
    "summary": "影响分析",
    "affected_modules": ["模块A"]
}
```"""
        }]
    }
    
    # 执行分析，应该使用默认值
    report = await impact_agent.analyze_impact(change_description=change_description)
    
    # 验证使用了默认值
    assert report.summary == "影响分析"
    assert report.affected_modules == ["模块A"]
    assert report.affected_test_cases == []  # 默认值
    assert report.risk_level == "medium"  # 默认值
    assert report.recommendations == []  # 默认值
    assert report.change_type == "feature_modify"  # 默认值


@pytest.mark.asyncio
async def test_analyze_impact_invalid_risk_level(impact_agent, mock_brconnector):
    """测试无效的风险等级"""
    change_description = "新增功能"
    
    # 模拟无效的风险等级
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": """```json
{
    "summary": "影响分析",
    "affected_modules": [],
    "affected_test_cases": [],
    "risk_level": "invalid",
    "recommendations": [],
    "change_type": "feature_add"
}
```"""
        }]
    }
    
    # 执行分析，应该标准化为 medium
    report = await impact_agent.analyze_impact(change_description=change_description)
    
    # 验证风险等级被标准化
    assert report.risk_level == "medium"


@pytest.mark.asyncio
async def test_analyze_impact_invalid_change_type(impact_agent, mock_brconnector):
    """测试无效的变更类型"""
    change_description = "新增功能"
    
    # 模拟无效的变更类型
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": """```json
{
    "summary": "影响分析",
    "affected_modules": [],
    "affected_test_cases": [],
    "risk_level": "low",
    "recommendations": [],
    "change_type": "invalid_type"
}
```"""
        }]
    }
    
    # 执行分析，应该标准化为 feature_modify
    report = await impact_agent.analyze_impact(change_description=change_description)
    
    # 验证变更类型被标准化
    assert report.change_type == "feature_modify"


@pytest.mark.asyncio
async def test_analyze_impact_with_markdown_code_block(impact_agent, mock_brconnector):
    """测试带 markdown 代码块的响应"""
    change_description = "新增功能"
    
    # 模拟带 markdown 代码块的响应
    mock_brconnector.chat.return_value = {
        "content": [{
            "text": """这是一些说明文字

```json
{
    "summary": "影响分析完成",
    "affected_modules": ["模块A", "模块B"],
    "affected_test_cases": [],
    "risk_level": "high",
    "recommendations": ["建议1", "建议2"],
    "change_type": "feature_modify"
}
```

这是一些后续说明"""
        }]
    }
    
    # 执行分析
    report = await impact_agent.analyze_impact(change_description=change_description)
    
    # 验证能够正确解析
    assert report.summary == "影响分析完成"
    assert len(report.affected_modules) == 2
    assert report.risk_level == "high"
    assert len(report.recommendations) == 2


def test_impact_report_to_dict():
    """测试 ImpactReport 转换为字典"""
    report = ImpactReport(
        summary="测试摘要",
        affected_modules=["模块A"],
        affected_test_cases=[{"title": "测试1", "reason": "原因", "action": "update"}],
        risk_level="medium",
        recommendations=["建议1"],
        change_type="feature_add"
    )
    
    result = report.to_dict()
    
    assert result['summary'] == "测试摘要"
    assert result['affected_modules'] == ["模块A"]
    assert len(result['affected_test_cases']) == 1
    assert result['risk_level'] == "medium"
    assert result['recommendations'] == ["建议1"]
    assert result['change_type'] == "feature_add"


def test_impact_report_from_dict():
    """测试从字典创建 ImpactReport"""
    data = {
        'summary': "测试摘要",
        'affected_modules': ["模块A"],
        'affected_test_cases': [{"title": "测试1"}],
        'risk_level': "high",
        'recommendations': ["建议1"],
        'change_type': "bug_fix"
    }
    
    report = ImpactReport.from_dict(data)
    
    assert report.summary == "测试摘要"
    assert report.affected_modules == ["模块A"]
    assert len(report.affected_test_cases) == 1
    assert report.risk_level == "high"
    assert report.recommendations == ["建议1"]
    assert report.change_type == "bug_fix"


def test_impact_report_from_dict_with_defaults():
    """测试从不完整的字典创建 ImpactReport"""
    data = {
        'summary': "测试摘要"
    }
    
    report = ImpactReport.from_dict(data)
    
    # 验证使用了默认值
    assert report.summary == "测试摘要"
    assert report.affected_modules == []
    assert report.affected_test_cases == []
    assert report.risk_level == "medium"
    assert report.recommendations == []
    assert report.change_type == "feature_modify"
