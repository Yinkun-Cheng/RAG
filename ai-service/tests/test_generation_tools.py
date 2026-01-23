"""
生成工具单元测试

测试 GenerateTestCaseTool 和 FormatTestCaseTool 的功能。
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from app.tool.generation_tools import (
    GenerateTestCaseTool,
    FormatTestCaseTool,
)
from app.tool.base import ToolError


@pytest.fixture
def mock_llm_client():
    """创建模拟的 LLM 客户端"""
    client = MagicMock()
    client.chat = AsyncMock()
    return client


@pytest.fixture
def generate_test_case_tool(mock_llm_client):
    """创建 GenerateTestCaseTool 实例"""
    return GenerateTestCaseTool(llm_client=mock_llm_client)


@pytest.fixture
def format_test_case_tool():
    """创建 FormatTestCaseTool 实例"""
    return FormatTestCaseTool()


# ============================================================================
# GenerateTestCaseTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_generate_test_case_tool_success(generate_test_case_tool, mock_llm_client):
    """测试测试用例生成成功"""
    # 模拟 LLM 响应
    mock_response = json.dumps({
        "title": "测试用户登录成功",
        "preconditions": "用户已注册且账户未被锁定",
        "steps": [
            {
                "step_number": 1,
                "action": "打开登录页面",
                "expected": "显示登录表单"
            },
            {
                "step_number": 2,
                "action": "输入正确的用户名和密码",
                "expected": "输入框显示输入内容"
            },
            {
                "step_number": 3,
                "action": "点击登录按钮",
                "expected": "跳转到首页"
            }
        ],
        "expected_result": "用户成功登录并跳转到首页"
    }, ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备测试点
    test_point = {
        "type": "functional",
        "description": "测试用户可以成功登录",
        "priority": "high",
        "rationale": "这是核心功能"
    }
    
    # 执行生成
    test_case = await generate_test_case_tool.execute(
        test_point=test_point,
        context={}
    )
    
    # 验证结果
    assert test_case["title"] == "测试用户登录成功"
    assert test_case["preconditions"] == "用户已注册且账户未被锁定"
    assert len(test_case["steps"]) == 3
    assert test_case["steps"][0]["step_number"] == 1
    assert test_case["steps"][0]["action"] == "打开登录页面"
    assert test_case["expected_result"] == "用户成功登录并跳转到首页"
    assert test_case["priority"] == "high"  # 继承自测试点
    assert test_case["type"] == "functional"  # 继承自测试点
    
    # 验证 LLM 调用
    mock_llm_client.chat.assert_called_once()


@pytest.mark.asyncio
async def test_generate_test_case_tool_with_context(generate_test_case_tool, mock_llm_client):
    """测试带上下文的测试用例生成"""
    # 模拟 LLM 响应
    mock_response = json.dumps({
        "title": "测试用例",
        "preconditions": "前置条件",
        "steps": [],
        "expected_result": "预期结果"
    }, ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备测试点和上下文
    test_point = {
        "type": "functional",
        "description": "测试功能",
        "priority": "medium",
        "rationale": "原因"
    }
    
    context = {
        "requirement_analysis": {
            "feature_name": "用户登录",
            "functional_points": ["登录验证"]
        },
        "historical_cases": [
            {
                "title": "历史用例1",
                "content": "历史用例内容"
            }
        ]
    }
    
    # 执行生成
    test_case = await generate_test_case_tool.execute(
        test_point=test_point,
        context=context
    )
    
    # 验证结果
    assert test_case["title"] == "测试用例"
    
    # 验证 LLM 调用包含上下文
    call_args = mock_llm_client.chat.call_args
    prompt = call_args[1]["messages"][0]["content"]
    assert "用户登录" in prompt  # 需求分析
    assert "历史用例1" in prompt  # 历史用例


@pytest.mark.asyncio
async def test_generate_test_case_tool_missing_fields(generate_test_case_tool, mock_llm_client):
    """测试缺少字段的响应"""
    # 模拟 LLM 响应（缺少某些字段）
    mock_response = json.dumps({
        "title": "测试用例"
        # 缺少 preconditions, steps, expected_result
    }, ensure_ascii=False)
    
    mock_llm_client.chat.return_value = mock_response
    
    # 准备测试点
    test_point = {
        "type": "functional",
        "description": "测试功能",
        "priority": "medium",
        "rationale": "原因"
    }
    
    # 执行生成
    test_case = await generate_test_case_tool.execute(
        test_point=test_point
    )
    
    # 验证结果：缺少的字段应该被填充默认值
    assert test_case["title"] == "测试用例"
    assert test_case["preconditions"] == ""  # 默认值
    assert test_case["steps"] == []  # 默认值
    assert test_case["expected_result"] == ""  # 默认值


# ============================================================================
# FormatTestCaseTool 测试
# ============================================================================

@pytest.mark.asyncio
async def test_format_test_case_tool_success(format_test_case_tool):
    """测试测试用例格式化成功"""
    # 准备原始测试用例
    test_cases = [
        {
            "title": "测试用户登录",
            "preconditions": "用户已注册",
            "steps": [
                {
                    "step_number": 1,
                    "action": "打开登录页面",
                    "expected": "显示登录表单"
                },
                {
                    "step_number": 2,
                    "action": "输入用户名密码",
                    "expected": "输入成功"
                }
            ],
            "expected_result": "登录成功",
            "priority": "high",
            "type": "functional"
        }
    ]
    
    # 执行格式化
    formatted_cases = await format_test_case_tool.execute(test_cases=test_cases)
    
    # 验证结果
    assert len(formatted_cases) == 1
    assert formatted_cases[0]["title"] == "测试用户登录"
    assert formatted_cases[0]["priority"] == "high"
    assert formatted_cases[0]["type"] == "functional"
    assert len(formatted_cases[0]["steps"]) == 2


@pytest.mark.asyncio
async def test_format_test_case_tool_normalize_priority(format_test_case_tool):
    """测试优先级标准化"""
    # 准备不同优先级格式的测试用例
    test_cases = [
        {"title": "用例1", "priority": "高", "type": "functional", "preconditions": "", "steps": [], "expected_result": ""},
        {"title": "用例2", "priority": "P0", "type": "functional", "preconditions": "", "steps": [], "expected_result": ""},
        {"title": "用例3", "priority": "medium", "type": "functional", "preconditions": "", "steps": [], "expected_result": ""},
        {"title": "用例4", "priority": "低", "type": "functional", "preconditions": "", "steps": [], "expected_result": ""},
    ]
    
    # 执行格式化
    formatted_cases = await format_test_case_tool.execute(test_cases=test_cases)
    
    # 验证结果：优先级应该被标准化
    assert formatted_cases[0]["priority"] == "high"
    assert formatted_cases[1]["priority"] == "high"
    assert formatted_cases[2]["priority"] == "medium"
    assert formatted_cases[3]["priority"] == "low"


@pytest.mark.asyncio
async def test_format_test_case_tool_normalize_type(format_test_case_tool):
    """测试测试类型标准化"""
    # 准备不同类型格式的测试用例
    test_cases = [
        {"title": "用例1", "type": "功能", "priority": "medium", "preconditions": "", "steps": [], "expected_result": ""},
        {"title": "用例2", "type": "边界值", "priority": "medium", "preconditions": "", "steps": [], "expected_result": ""},
        {"title": "用例3", "type": "异常", "priority": "medium", "preconditions": "", "steps": [], "expected_result": ""},
    ]
    
    # 执行格式化
    formatted_cases = await format_test_case_tool.execute(test_cases=test_cases)
    
    # 验证结果：类型应该被标准化
    assert formatted_cases[0]["type"] == "functional"
    assert formatted_cases[1]["type"] == "boundary"
    assert formatted_cases[2]["type"] == "exception"


@pytest.mark.asyncio
async def test_format_test_case_tool_format_steps(format_test_case_tool):
    """测试步骤格式化"""
    # 准备包含不规范步骤的测试用例
    test_cases = [
        {
            "title": "测试用例",
            "preconditions": "前置条件",
            "steps": [
                {
                    # 缺少 step_number
                    "action": "操作1",
                    "expected": "预期1"
                },
                {
                    "step_number": 5,  # 不连续的编号
                    "action": "操作2",
                    "expected": "预期2"
                },
                {
                    "step_number": 3,
                    "action": "",  # 空操作（应该被过滤）
                    "expected": "预期3"
                }
            ],
            "expected_result": "预期结果",
            "priority": "medium",
            "type": "functional"
        }
    ]
    
    # 执行格式化
    formatted_cases = await format_test_case_tool.execute(test_cases=test_cases)
    
    # 验证结果
    steps = formatted_cases[0]["steps"]
    assert len(steps) == 2  # 空操作被过滤
    assert steps[0]["step_number"] == 1  # 自动填充
    assert steps[0]["action"] == "操作1"
    assert steps[1]["step_number"] == 5  # 保留原编号
    assert steps[1]["action"] == "操作2"


@pytest.mark.asyncio
async def test_format_test_case_tool_empty_list(format_test_case_tool):
    """测试空列表"""
    # 执行格式化
    formatted_cases = await format_test_case_tool.execute(test_cases=[])
    
    # 验证结果
    assert len(formatted_cases) == 0


@pytest.mark.asyncio
async def test_format_test_case_tool_invalid_case(format_test_case_tool):
    """测试包含无效用例的列表"""
    # 准备包含无效用例的列表
    test_cases = [
        {
            "title": "有效用例",
            "preconditions": "前置条件",
            "steps": [],
            "expected_result": "预期结果",
            "priority": "medium",
            "type": "functional"
        },
        None,  # 无效用例
        {
            "title": "另一个有效用例",
            "preconditions": "前置条件",
            "steps": [],
            "expected_result": "预期结果",
            "priority": "high",
            "type": "functional"
        }
    ]
    
    # 执行格式化（应该跳过无效用例）
    formatted_cases = await format_test_case_tool.execute(test_cases=test_cases)
    
    # 验证结果：只有有效用例被格式化
    assert len(formatted_cases) == 2
    assert formatted_cases[0]["title"] == "有效用例"
    assert formatted_cases[1]["title"] == "另一个有效用例"
