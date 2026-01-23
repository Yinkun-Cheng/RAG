"""
理解工具单元测试

测试 ParseRequirementTool 和 ExtractTestPointsTool 的功能。
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.tool.understanding_tools import (
    ParseRequirementTool,
    ExtractTestPointsTool,
)
from app.tool.base import ToolError


@pytest.fixture
def mock_llm_client():
    """创建模拟的 LLM 客户端"""
    client = MagicMock()
    client.chat = AsyncMock()
    return client


@pytest.fixture
def parse_requirement_tool(mock_llm_client):
    """创建 ParseRequirementTool 实例"""
    return ParseRequirementTool(llm_client=mock_llm_client)


@pytest.fixture
def extract_test_points_tool(mock_llm_client):
    """创建 ExtractTestPointsTool 实例"""
    return ExtractTestPointsTool(llm_client=mock_llm_client)


# ============================================================================
# ParseRequirementTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_parse_requirement_tool_success(parse_requirement_tool, mock_llm_client):
    """测试需求解析成功"""
    # 模拟 LLM 响应
    mock_response = json.dumps({
        "feature_name": "用户登录功能",
        "description": "实现用户通过用户名和密码登录系统的功能",
        "functional_points": [
            "用户可以输入用户名和密码",
            "系统验证用户名和密码是否正确",
            "登录成功后跳转到首页"
        ],
        "constraints": [
            "密码必须加密存储",
            "登录失败3次后锁定账户30分钟"
        ],
        "acceptance_criteria": [
            "用户可以成功登录",
            "错误的密码会显示错误提示",
            "登录成功后显示用户信息"
        ]
    }, ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 执行解析
    result = await parse_requirement_tool.execute(
        requirement="实现用户登录功能，用户可以通过用户名和密码登录系统"
    )
    
    # 验证结果
    assert result["feature_name"] == "用户登录功能"
    assert result["description"] == "实现用户通过用户名和密码登录系统的功能"
    assert len(result["functional_points"]) == 3
    assert len(result["constraints"]) == 2
    assert len(result["acceptance_criteria"]) == 3
    
    # 验证 LLM 调用
    mock_llm_client.chat.assert_called_once()
    call_args = mock_llm_client.chat.call_args
    assert "实现用户登录功能" in call_args[1]["messages"][0]["content"]


@pytest.mark.asyncio
async def test_parse_requirement_tool_with_json_code_block(parse_requirement_tool, mock_llm_client):
    """测试解析包含 JSON 代码块的响应"""
    # 模拟 LLM 响应（包含 markdown 代码块）
    mock_response = """这是需求分析结果：

```json
{
  "feature_name": "用户注册功能",
  "description": "实现新用户注册功能",
  "functional_points": ["填写注册信息", "验证邮箱"],
  "constraints": ["邮箱必须唯一"],
  "acceptance_criteria": ["注册成功"]
}
```

以上是分析结果。"""
    
    mock_llm_client.chat.return_value = mock_response
    
    # 执行解析
    result = await parse_requirement_tool.execute(
        requirement="实现用户注册功能"
    )
    
    # 验证结果
    assert result["feature_name"] == "用户注册功能"
    assert len(result["functional_points"]) == 2


@pytest.mark.asyncio
async def test_parse_requirement_tool_llm_error(parse_requirement_tool, mock_llm_client):
    """测试 LLM 调用失败"""
    # 模拟 LLM 错误
    mock_llm_client.chat.side_effect = Exception("API Error")
    
    # 执行解析应该抛出异常
    with pytest.raises(ToolError) as exc_info:
        await parse_requirement_tool.execute(
            requirement="测试需求"
        )
    
    assert "解析需求失败" in str(exc_info.value)


@pytest.mark.asyncio
async def test_parse_requirement_tool_invalid_json(parse_requirement_tool, mock_llm_client):
    """测试无效的 JSON 响应"""
    # 模拟无效的 JSON 响应
    mock_llm_client.chat.return_value = "这不是有效的 JSON"
    
    # 执行解析应该抛出异常
    with pytest.raises(ToolError) as exc_info:
        await parse_requirement_tool.execute(
            requirement="测试需求"
        )
    
    assert "无法解析 LLM 响应为 JSON" in str(exc_info.value)


# ============================================================================
# ExtractTestPointsTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_extract_test_points_tool_success(extract_test_points_tool, mock_llm_client):
    """测试测试点提取成功"""
    # 模拟 LLM 响应
    mock_response = json.dumps([
        {
            "type": "functional",
            "description": "测试用户可以成功登录",
            "priority": "high",
            "rationale": "这是核心功能"
        },
        {
            "type": "exception",
            "description": "测试错误密码的处理",
            "priority": "high",
            "rationale": "需要验证错误处理"
        },
        {
            "type": "boundary",
            "description": "测试密码长度边界值",
            "priority": "medium",
            "rationale": "验证输入验证"
        }
    ], ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备需求分析结果
    requirement_analysis = {
        "feature_name": "用户登录功能",
        "description": "实现用户登录",
        "functional_points": ["输入用户名密码", "验证登录"],
        "constraints": [],
        "acceptance_criteria": []
    }
    
    # 执行提取
    test_points = await extract_test_points_tool.execute(
        requirement_analysis=requirement_analysis
    )
    
    # 验证结果
    assert len(test_points) == 3
    assert test_points[0]["type"] == "functional"
    assert test_points[0]["priority"] == "high"
    assert test_points[1]["type"] == "exception"
    assert test_points[2]["type"] == "boundary"
    
    # 验证 LLM 调用
    mock_llm_client.chat.assert_called_once()


@pytest.mark.asyncio
async def test_extract_test_points_tool_with_json_code_block(extract_test_points_tool, mock_llm_client):
    """测试解析包含 JSON 代码块的响应"""
    # 模拟 LLM 响应（包含 markdown 代码块）
    mock_response = """以下是提取的测试点：

```json
[
  {
    "type": "functional",
    "description": "测试功能1",
    "priority": "high",
    "rationale": "重要功能"
  }
]
```"""
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备需求分析结果
    requirement_analysis = {
        "feature_name": "测试功能",
        "description": "测试",
        "functional_points": [],
        "constraints": [],
        "acceptance_criteria": []
    }
    
    # 执行提取
    test_points = await extract_test_points_tool.execute(
        requirement_analysis=requirement_analysis
    )
    
    # 验证结果
    assert len(test_points) == 1
    assert test_points[0]["type"] == "functional"


@pytest.mark.asyncio
async def test_extract_test_points_tool_missing_fields(extract_test_points_tool, mock_llm_client):
    """测试缺少字段的测试点"""
    # 模拟 LLM 响应（缺少某些字段）
    mock_response = json.dumps([
        {
            "description": "测试功能1"
            # 缺少 type, priority, rationale
        }
    ], ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备需求分析结果
    requirement_analysis = {
        "feature_name": "测试功能",
        "description": "测试",
        "functional_points": [],
        "constraints": [],
        "acceptance_criteria": []
    }
    
    # 执行提取
    test_points = await extract_test_points_tool.execute(
        requirement_analysis=requirement_analysis
    )
    
    # 验证结果：缺少的字段应该被填充默认值
    assert len(test_points) == 1
    assert test_points[0]["type"] == "functional"  # 默认值
    assert test_points[0]["priority"] == "medium"  # 默认值
    assert test_points[0]["rationale"] == ""  # 默认值


@pytest.mark.asyncio
async def test_extract_test_points_tool_invalid_response(extract_test_points_tool, mock_llm_client):
    """测试无效的响应（不是数组）"""
    # 模拟无效的响应（对象而不是数组）
    mock_response = json.dumps({
        "test_points": []
    }, ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备需求分析结果
    requirement_analysis = {
        "feature_name": "测试功能",
        "description": "测试",
        "functional_points": [],
        "constraints": [],
        "acceptance_criteria": []
    }
    
    # 执行提取应该抛出异常
    with pytest.raises(ToolError) as exc_info:
        await extract_test_points_tool.execute(
            requirement_analysis=requirement_analysis
        )
    
    assert "不是 JSON 数组" in str(exc_info.value)
