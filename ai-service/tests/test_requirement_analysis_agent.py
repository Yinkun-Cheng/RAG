"""
RequirementAnalysisAgent 单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agent.requirement_analysis_agent import (
    RequirementAnalysisAgent,
    AnalysisResult,
)
from app.integration.brconnector_client import BRConnectorError


@pytest.fixture
def mock_brconnector():
    """创建 mock BRConnector 客户端"""
    client = AsyncMock()
    return client


@pytest.fixture
def agent(mock_brconnector):
    """创建 RequirementAnalysisAgent 实例"""
    return RequirementAnalysisAgent(mock_brconnector)


@pytest.mark.asyncio
async def test_analyze_basic_requirement(agent, mock_brconnector):
    """测试基本需求分析"""
    # 准备 mock 响应
    mock_response = """```json
{
  "functional_points": ["用户登录", "密码验证"],
  "business_rules": ["密码长度至少 8 位", "用户名唯一"],
  "input_specs": {
    "username": {"type": "string", "required": true},
    "password": {"type": "string", "required": true, "min_length": 8}
  },
  "output_specs": {
    "token": {"type": "string", "description": "JWT 令牌"}
  },
  "exception_conditions": ["用户名不存在", "密码错误", "账户被锁定"],
  "constraints": ["响应时间 < 2 秒", "支持 HTTPS"]
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行分析
    result = await agent.analyze("用户应该能够使用用户名和密码登录")
    
    # 验证结果
    assert isinstance(result, AnalysisResult)
    assert len(result.functional_points) == 2
    assert "用户登录" in result.functional_points
    assert "密码验证" in result.functional_points
    
    assert len(result.business_rules) == 2
    assert len(result.exception_conditions) == 3
    assert len(result.constraints) == 2
    
    assert "username" in result.input_specs
    assert result.input_specs["username"]["type"] == "string"
    assert result.input_specs["username"]["required"] is True
    
    # 验证 LLM 被调用
    mock_brconnector.chat_simple.assert_called_once()
    call_args = mock_brconnector.chat_simple.call_args
    assert "用户应该能够使用用户名和密码登录" in call_args.kwargs['prompt']


@pytest.mark.asyncio
async def test_analyze_with_historical_context(agent, mock_brconnector):
    """测试带历史上下文的需求分析"""
    mock_response = """```json
{
  "functional_points": ["创建订单"],
  "business_rules": ["订单金额 > 0"],
  "input_specs": {"amount": {"type": "number"}},
  "output_specs": {"order_id": {"type": "string"}},
  "exception_conditions": ["金额无效"],
  "constraints": []
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 准备历史上下文
    context = {
        'historical_prds': [
            {'title': '订单管理系统', 'content': '用户可以创建、查看、取消订单...'},
            {'title': '支付系统', 'content': '支持多种支付方式...'}
        ]
    }
    
    # 执行分析
    result = await agent.analyze("实现订单创建功能", context)
    
    # 验证结果
    assert isinstance(result, AnalysisResult)
    assert len(result.functional_points) == 1
    assert "创建订单" in result.functional_points
    
    # 验证历史上下文被包含在提示词中
    call_args = mock_brconnector.chat_simple.call_args
    assert "订单管理系统" in call_args.kwargs['prompt']
    assert "支付系统" in call_args.kwargs['prompt']


@pytest.mark.asyncio
async def test_analyze_without_markdown_code_block(agent, mock_brconnector):
    """测试解析不带 markdown 代码块的 JSON 响应"""
    # 直接返回 JSON（不带代码块）
    mock_response = """{
  "functional_points": ["搜索功能"],
  "business_rules": [],
  "input_specs": {"query": {"type": "string"}},
  "output_specs": {"results": {"type": "array"}},
  "exception_conditions": ["查询为空"],
  "constraints": []
}"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行分析
    result = await agent.analyze("实现搜索功能")
    
    # 验证结果
    assert isinstance(result, AnalysisResult)
    assert len(result.functional_points) == 1
    assert "搜索功能" in result.functional_points


@pytest.mark.asyncio
async def test_analyze_with_missing_fields(agent, mock_brconnector):
    """测试处理缺少字段的响应"""
    # 返回不完整的 JSON（缺少某些字段）
    mock_response = """```json
{
  "functional_points": ["导出数据"],
  "business_rules": ["数据格式为 CSV"]
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行分析
    result = await agent.analyze("实现数据导出功能")
    
    # 验证结果 - 缺少的字段应该有默认值
    assert isinstance(result, AnalysisResult)
    assert len(result.functional_points) == 1
    assert len(result.business_rules) == 1
    assert result.input_specs == {}  # 默认空字典
    assert result.output_specs == {}  # 默认空字典
    assert result.exception_conditions == []  # 默认空列表
    assert result.constraints == []  # 默认空列表


@pytest.mark.asyncio
async def test_analyze_llm_error(agent, mock_brconnector):
    """测试 LLM 调用失败的情况"""
    # Mock LLM 抛出错误
    mock_brconnector.chat_simple.side_effect = BRConnectorError("API 调用失败")
    
    # 执行分析应该抛出异常
    with pytest.raises(BRConnectorError):
        await agent.analyze("测试需求")


@pytest.mark.asyncio
async def test_analyze_invalid_json_response(agent, mock_brconnector):
    """测试无效 JSON 响应的处理"""
    # 返回无效的 JSON
    mock_response = "这不是有效的 JSON 响应"
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行分析应该抛出 ValueError
    with pytest.raises(ValueError, match="无法解析 LLM 响应为 JSON"):
        await agent.analyze("测试需求")


@pytest.mark.asyncio
async def test_analyze_empty_requirement(agent, mock_brconnector):
    """测试空需求的处理"""
    mock_response = """```json
{
  "functional_points": [],
  "business_rules": [],
  "input_specs": {},
  "output_specs": {},
  "exception_conditions": [],
  "constraints": []
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行分析
    result = await agent.analyze("")
    
    # 验证结果 - 应该返回空的分析结果
    assert isinstance(result, AnalysisResult)
    assert len(result.functional_points) == 0
    assert len(result.business_rules) == 0


@pytest.mark.asyncio
async def test_analysis_result_to_dict(agent, mock_brconnector):
    """测试 AnalysisResult 转换为字典"""
    mock_response = """```json
{
  "functional_points": ["功能1"],
  "business_rules": ["规则1"],
  "input_specs": {"param1": {"type": "string"}},
  "output_specs": {"result": {"type": "object"}},
  "exception_conditions": ["异常1"],
  "constraints": ["约束1"]
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行分析
    result = await agent.analyze("测试需求")
    
    # 转换为字典
    result_dict = result.to_dict()
    
    # 验证字典结构
    assert isinstance(result_dict, dict)
    assert 'functional_points' in result_dict
    assert 'business_rules' in result_dict
    assert result_dict['functional_points'] == ["功能1"]
    assert result_dict['business_rules'] == ["规则1"]


def test_analysis_result_from_dict():
    """测试从字典创建 AnalysisResult"""
    data = {
        'functional_points': ["功能1", "功能2"],
        'business_rules': ["规则1"],
        'input_specs': {"param": {"type": "string"}},
        'output_specs': {"result": {"type": "object"}},
        'exception_conditions': ["异常1", "异常2"],
        'constraints': ["约束1"]
    }
    
    # 从字典创建
    result = AnalysisResult.from_dict(data)
    
    # 验证结果
    assert isinstance(result, AnalysisResult)
    assert result.functional_points == ["功能1", "功能2"]
    assert result.business_rules == ["规则1"]
    assert len(result.exception_conditions) == 2
