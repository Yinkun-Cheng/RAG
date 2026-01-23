"""
TestDesignAgent 单元测试
"""

import pytest
from unittest.mock import AsyncMock
from app.agent.test_design_agent import (
    TestDesignAgent,
    TestCaseDesign,
)
from app.agent.requirement_analysis_agent import AnalysisResult
from app.integration.brconnector_client import BRConnectorError


@pytest.fixture
def mock_brconnector():
    """创建 mock BRConnector 客户端"""
    client = AsyncMock()
    return client


@pytest.fixture
def agent(mock_brconnector):
    """创建 TestDesignAgent 实例"""
    return TestDesignAgent(mock_brconnector)


@pytest.fixture
def sample_analysis():
    """创建示例需求分析结果"""
    return AnalysisResult(
        functional_points=["用户登录", "密码验证"],
        business_rules=["密码长度至少 8 位"],
        input_specs={
            "username": {"type": "string", "required": True},
            "password": {"type": "string", "required": True, "min_length": 8}
        },
        output_specs={"token": {"type": "string"}},
        exception_conditions=["用户名不存在", "密码错误"],
        constraints=["响应时间 < 2 秒"]
    )


@pytest.mark.asyncio
async def test_design_tests_basic(agent, mock_brconnector, sample_analysis):
    """测试基本测试用例设计"""
    # 准备 mock 响应
    mock_response = """```json
[
  {
    "title": "测试有效用户登录",
    "preconditions": "用户已注册且账户激活",
    "steps": ["输入有效用户名", "输入有效密码", "点击登录按钮"],
    "expected_result": "用户成功登录，返回 JWT 令牌",
    "priority": "high",
    "type": "functional",
    "rationale": "验证主流程"
  },
  {
    "title": "测试密码错误",
    "preconditions": "用户已注册",
    "steps": ["输入有效用户名", "输入错误密码", "点击登录按钮"],
    "expected_result": "显示密码错误提示",
    "priority": "high",
    "type": "exception",
    "rationale": "验证异常处理"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 验证结果
    assert isinstance(result, list)
    assert len(result) == 2
    
    # 验证第一个测试用例
    test_case_1 = result[0]
    assert isinstance(test_case_1, TestCaseDesign)
    assert test_case_1.title == "测试有效用户登录"
    assert len(test_case_1.steps) == 3
    assert test_case_1.priority == "high"
    assert test_case_1.type == "functional"
    
    # 验证第二个测试用例
    test_case_2 = result[1]
    assert test_case_2.title == "测试密码错误"
    assert test_case_2.type == "exception"
    
    # 验证 LLM 被调用
    mock_brconnector.chat_simple.assert_called_once()


@pytest.mark.asyncio
async def test_design_tests_with_historical_cases(agent, mock_brconnector, sample_analysis):
    """测试带历史测试用例的设计"""
    mock_response = """```json
[
  {
    "title": "测试登录功能",
    "preconditions": "用户存在",
    "steps": ["登录"],
    "expected_result": "成功",
    "priority": "high",
    "type": "functional",
    "rationale": "主流程"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 准备历史测试用例
    historical_cases = [
        {
            'title': '测试用户注册',
            'steps': ['输入用户名', '输入密码', '点击注册']
        },
        {
            'title': '测试密码重置',
            'steps': ['输入邮箱', '点击重置']
        }
    ]
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis, historical_cases)
    
    # 验证结果
    assert isinstance(result, list)
    assert len(result) == 1
    
    # 验证历史用例被包含在提示词中
    call_args = mock_brconnector.chat_simple.call_args
    assert "测试用户注册" in call_args.kwargs['prompt']
    assert "测试密码重置" in call_args.kwargs['prompt']


@pytest.mark.asyncio
async def test_design_tests_without_markdown_code_block(agent, mock_brconnector, sample_analysis):
    """测试解析不带 markdown 代码块的 JSON 响应"""
    # 直接返回 JSON（不带代码块）
    mock_response = """[
  {
    "title": "测试边界值",
    "preconditions": "系统正常",
    "steps": ["输入最小值"],
    "expected_result": "接受输入",
    "priority": "medium",
    "type": "boundary",
    "rationale": "边界测试"
  }
]"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 验证结果
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].type == "boundary"


@pytest.mark.asyncio
async def test_design_tests_with_missing_rationale(agent, mock_brconnector, sample_analysis):
    """测试处理缺少 rationale 字段的响应"""
    mock_response = """```json
[
  {
    "title": "测试性能",
    "preconditions": "系统空闲",
    "steps": ["发送 100 个请求"],
    "expected_result": "响应时间 < 2 秒",
    "priority": "low",
    "type": "performance"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 验证结果 - rationale 应该有默认值
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].rationale == ""  # 默认空字符串


@pytest.mark.asyncio
async def test_design_tests_with_invalid_test_case(agent, mock_brconnector, sample_analysis):
    """测试处理包含无效测试用例的响应"""
    # 返回包含有效和无效测试用例的混合数组
    mock_response = """```json
[
  {
    "title": "有效测试用例",
    "preconditions": "前置条件",
    "steps": ["步骤1"],
    "expected_result": "预期结果",
    "priority": "high",
    "type": "functional",
    "rationale": "理由"
  },
  {
    "title": "无效测试用例 - 缺少 steps"
  },
  {
    "title": "另一个有效测试用例",
    "preconditions": "前置条件2",
    "steps": ["步骤1", "步骤2"],
    "expected_result": "预期结果2",
    "priority": "medium",
    "type": "exception",
    "rationale": "理由2"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 验证结果 - 应该只包含有效的测试用例
    assert isinstance(result, list)
    assert len(result) == 2  # 跳过了无效的测试用例
    assert result[0].title == "有效测试用例"
    assert result[1].title == "另一个有效测试用例"


@pytest.mark.asyncio
async def test_design_tests_priority_and_type_normalization(agent, mock_brconnector, sample_analysis):
    """测试优先级和类型的标准化"""
    mock_response = """```json
[
  {
    "title": "测试用例",
    "preconditions": "前置条件",
    "steps": ["步骤1"],
    "expected_result": "预期结果",
    "priority": "HIGH",
    "type": "FUNCTIONAL",
    "rationale": "理由"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 验证结果 - 优先级和类型应该被标准化为小写
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].priority == "high"  # 标准化为小写
    assert result[0].type == "functional"  # 标准化为小写


@pytest.mark.asyncio
async def test_design_tests_steps_as_string(agent, mock_brconnector, sample_analysis):
    """测试处理 steps 为字符串的情况"""
    mock_response = """```json
[
  {
    "title": "测试用例",
    "preconditions": "前置条件",
    "steps": "单个步骤字符串",
    "expected_result": "预期结果",
    "priority": "medium",
    "type": "functional",
    "rationale": "理由"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 验证结果 - steps 应该被转换为列表
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0].steps, list)
    assert len(result[0].steps) == 1
    assert result[0].steps[0] == "单个步骤字符串"


@pytest.mark.asyncio
async def test_design_tests_llm_error(agent, mock_brconnector, sample_analysis):
    """测试 LLM 调用失败的情况"""
    # Mock LLM 抛出错误
    mock_brconnector.chat_simple.side_effect = BRConnectorError("API 调用失败")
    
    # 执行测试设计应该抛出异常
    with pytest.raises(BRConnectorError):
        await agent.design_tests(sample_analysis)


@pytest.mark.asyncio
async def test_design_tests_invalid_json_response(agent, mock_brconnector, sample_analysis):
    """测试无效 JSON 响应的处理"""
    # 返回无效的 JSON
    mock_response = "这不是有效的 JSON 响应"
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计应该抛出 ValueError
    with pytest.raises(ValueError, match="无法解析 LLM 响应为 JSON"):
        await agent.design_tests(sample_analysis)


@pytest.mark.asyncio
async def test_design_tests_non_array_response(agent, mock_brconnector, sample_analysis):
    """测试非数组响应的处理"""
    # 返回对象而不是数组
    mock_response = """```json
{
  "title": "这是一个对象，不是数组"
}
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计应该抛出 ValueError
    with pytest.raises(ValueError, match="响应应该是测试用例数组"):
        await agent.design_tests(sample_analysis)


@pytest.mark.asyncio
async def test_design_tests_empty_array(agent, mock_brconnector, sample_analysis):
    """测试空数组响应的处理"""
    mock_response = """```json
[]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计应该抛出 ValueError
    with pytest.raises(ValueError, match="没有有效的测试用例"):
        await agent.design_tests(sample_analysis)


@pytest.mark.asyncio
async def test_test_case_design_to_dict(agent, mock_brconnector, sample_analysis):
    """测试 TestCaseDesign 转换为字典"""
    mock_response = """```json
[
  {
    "title": "测试用例",
    "preconditions": "前置条件",
    "steps": ["步骤1", "步骤2"],
    "expected_result": "预期结果",
    "priority": "high",
    "type": "functional",
    "rationale": "理由"
  }
]
```"""
    
    mock_brconnector.chat_simple.return_value = mock_response
    
    # 执行测试设计
    result = await agent.design_tests(sample_analysis)
    
    # 转换为字典
    test_case_dict = result[0].to_dict()
    
    # 验证字典结构
    assert isinstance(test_case_dict, dict)
    assert 'title' in test_case_dict
    assert 'steps' in test_case_dict
    assert test_case_dict['title'] == "测试用例"
    assert test_case_dict['steps'] == ["步骤1", "步骤2"]


def test_test_case_design_from_dict():
    """测试从字典创建 TestCaseDesign"""
    data = {
        'title': '测试登录',
        'preconditions': '用户已注册',
        'steps': ['输入用户名', '输入密码', '点击登录'],
        'expected_result': '登录成功',
        'priority': 'high',
        'type': 'functional',
        'rationale': '验证主流程'
    }
    
    # 从字典创建
    test_case = TestCaseDesign.from_dict(data)
    
    # 验证结果
    assert isinstance(test_case, TestCaseDesign)
    assert test_case.title == '测试登录'
    assert len(test_case.steps) == 3
    assert test_case.priority == 'high'
    assert test_case.type == 'functional'
