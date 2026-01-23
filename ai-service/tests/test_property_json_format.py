"""
属性测试：JSON 输出格式

属性 11: JSON 输出格式
验证需求 4.4: 所有测试用例生成结果必须是有效的 JSON 格式
"""

import json
import pytest
import asyncio
from hypothesis import given, strategies as st, settings
from app.tool.generation_tools import FormatTestCaseTool


# ============================================================================
# 辅助函数
# ============================================================================

def run_async(coro):
    """同步运行异步函数"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


# ============================================================================
# 测试数据生成策略
# ============================================================================

# 生成有效的测试步骤
test_step_strategy = st.builds(
    dict,
    step_number=st.integers(min_value=1, max_value=20),
    action=st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    expected=st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',)))
)

# 生成有效的测试用例
valid_test_case_strategy = st.builds(
    dict,
    title=st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
    preconditions=st.text(min_size=0, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))),
    steps=st.lists(test_step_strategy, min_size=1, max_size=10),
    expected_result=st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))),
    priority=st.sampled_from(['high', 'medium', 'low']),
    type=st.sampled_from(['functional', 'boundary', 'exception'])
)


# ============================================================================
# 属性 11: JSON 输出格式
# ============================================================================

@given(test_cases=st.lists(valid_test_case_strategy, min_size=1, max_size=5))
@settings(max_examples=100, deadline=None)
def test_property_json_output_format(test_cases):
    """
    属性 11: JSON 输出格式
    
    对于任何测试用例生成结果：
    1. 结果必须可以序列化为 JSON
    2. 序列化后的 JSON 必须可以解析
    3. 解析后的对象必须包含 test_cases 数组
    4. 数组中的每个对象必须是正确结构的测试用例
    """
    tool = FormatTestCaseTool()
    
    # 格式化测试用例（同步运行异步方法）
    formatted = run_async(tool.execute(test_cases))
    
    # 构建响应对象（模拟 API 响应）
    response = {
        'test_cases': formatted,
        'count': len(formatted),
        'status': 'success'
    }
    
    # 1. 验证可以序列化为 JSON
    try:
        json_str = json.dumps(response, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        pytest.fail(f"无法序列化为 JSON: {e}")
    
    # 2. 验证 JSON 字符串不为空
    assert len(json_str) > 0, "JSON 字符串不应为空"
    
    # 3. 验证可以解析 JSON
    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        pytest.fail(f"无法解析 JSON: {e}")
    
    # 4. 验证解析后的对象结构
    assert isinstance(parsed, dict), "解析后的对象必须是字典"
    assert 'test_cases' in parsed, "解析后的对象必须包含 test_cases 字段"
    assert isinstance(parsed['test_cases'], list), "test_cases 必须是数组"
    assert len(parsed['test_cases']) > 0, "test_cases 数组不应为空"
    
    # 5. 验证每个测试用例的结构
    for i, case in enumerate(parsed['test_cases']):
        assert isinstance(case, dict), f"测试用例 {i} 必须是对象"
        
        # 必需字段
        required_fields = ['title', 'preconditions', 'steps', 'expected_result', 'priority', 'type']
        for field in required_fields:
            assert field in case, f"测试用例 {i} 必须包含 {field} 字段"
        
        # 字段类型
        assert isinstance(case['title'], str), f"测试用例 {i} 的 title 必须是字符串"
        assert isinstance(case['preconditions'], str), f"测试用例 {i} 的 preconditions 必须是字符串"
        assert isinstance(case['steps'], list), f"测试用例 {i} 的 steps 必须是数组"
        assert isinstance(case['expected_result'], str), f"测试用例 {i} 的 expected_result 必须是字符串"
        assert isinstance(case['priority'], str), f"测试用例 {i} 的 priority 必须是字符串"
        assert isinstance(case['type'], str), f"测试用例 {i} 的 type 必须是字符串"
        
        # 步骤结构
        for j, step in enumerate(case['steps']):
            assert isinstance(step, dict), f"测试用例 {i} 的步骤 {j} 必须是对象"
            assert 'step_number' in step, f"测试用例 {i} 的步骤 {j} 必须包含 step_number"
            assert 'action' in step, f"测试用例 {i} 的步骤 {j} 必须包含 action"
            assert 'expected' in step, f"测试用例 {i} 的步骤 {j} 必须包含 expected"


# ============================================================================
# JSON 序列化和反序列化往返测试
# ============================================================================

@given(test_case=valid_test_case_strategy)
@settings(max_examples=100, deadline=None)
def test_property_json_round_trip(test_case):
    """
    JSON 往返测试：序列化后再反序列化应该得到等价的数据
    """
    tool = FormatTestCaseTool()
    
    # 格式化测试用例（同步运行异步方法）
    formatted = run_async(tool.execute([test_case]))
    original = formatted[0]
    
    # 序列化
    json_str = json.dumps(original, ensure_ascii=False)
    
    # 反序列化
    restored = json.loads(json_str)
    
    # 验证数据等价性
    assert restored['title'] == original['title']
    assert restored['preconditions'] == original['preconditions']
    assert restored['expected_result'] == original['expected_result']
    assert restored['priority'] == original['priority']
    assert restored['type'] == original['type']
    assert len(restored['steps']) == len(original['steps'])
    
    for i, (restored_step, original_step) in enumerate(zip(restored['steps'], original['steps'])):
        assert restored_step['step_number'] == original_step['step_number'], \
            f"步骤 {i} 的 step_number 不匹配"
        assert restored_step['action'] == original_step['action'], \
            f"步骤 {i} 的 action 不匹配"
        assert restored_step['expected'] == original_step['expected'], \
            f"步骤 {i} 的 expected 不匹配"


# ============================================================================
# 特殊字符处理测试
# ============================================================================

def test_property_json_special_characters():
    """测试 JSON 输出正确处理特殊字符"""
    tool = FormatTestCaseTool()
    
    # 包含特殊字符的测试用例
    test_case = {
        'title': 'Test "quotes" and \\backslashes\\',
        'preconditions': 'Line 1\nLine 2\tTabbed',
        'steps': [
            {
                'step_number': 1,
                'action': 'Enter {"key": "value"}',
                'expected': 'Response: {"status": "ok"}'
            }
        ],
        'expected_result': 'Success with special chars: <>&"\'\n\t',
        'priority': 'high',
        'type': 'functional'
    }
    
    formatted = run_async(tool.execute([test_case]))
    
    # 序列化为 JSON
    json_str = json.dumps({'test_cases': formatted}, ensure_ascii=False)
    
    # 验证可以解析
    parsed = json.loads(json_str)
    
    # 验证特殊字符被正确保留
    case = parsed['test_cases'][0]
    assert '"quotes"' in case['title']
    assert '\\backslashes\\' in case['title']
    assert '\n' in case['preconditions']
    assert '\t' in case['preconditions']


def test_property_json_unicode_characters():
    """测试 JSON 输出正确处理 Unicode 字符"""
    tool = FormatTestCaseTool()
    
    # 包含 Unicode 字符的测试用例
    test_case = {
        'title': '测试用户登录功能 🔐',
        'preconditions': '用户已注册，密码为：P@ssw0rd！',
        'steps': [
            {
                'step_number': 1,
                'action': '输入用户名：张三',
                'expected': '显示欢迎信息：欢迎，张三！'
            }
        ],
        'expected_result': '登录成功 ✓',
        'priority': 'high',
        'type': 'functional'
    }
    
    formatted = run_async(tool.execute([test_case]))
    
    # 序列化为 JSON（不转义 Unicode）
    json_str = json.dumps({'test_cases': formatted}, ensure_ascii=False)
    
    # 验证可以解析
    parsed = json.loads(json_str)
    
    # 验证 Unicode 字符被正确保留
    case = parsed['test_cases'][0]
    assert '测试用户登录功能' in case['title']
    assert '🔐' in case['title']
    assert '张三' in case['steps'][0]['action']
    assert '✓' in case['expected_result']


def test_property_json_empty_values():
    """测试 JSON 输出正确处理空值"""
    tool = FormatTestCaseTool()
    
    test_case = {
        'title': 'Test',
        'preconditions': '',  # 空字符串
        'steps': [
            {'step_number': 1, 'action': 'Action', 'expected': ''}  # 空预期结果
        ],
        'expected_result': 'Result',
        'priority': 'medium',
        'type': 'functional'
    }
    
    formatted = run_async(tool.execute([test_case]))
    
    # 序列化为 JSON
    json_str = json.dumps({'test_cases': formatted}, ensure_ascii=False)
    
    # 验证可以解析
    parsed = json.loads(json_str)
    
    # 验证空值被正确处理
    case = parsed['test_cases'][0]
    assert case['preconditions'] == ''
    assert case['steps'][0]['expected'] == ''


def test_property_json_large_dataset():
    """测试 JSON 输出处理大量测试用例"""
    tool = FormatTestCaseTool()
    
    # 生成 100 个测试用例
    test_cases = [
        {
            'title': f'Test Case {i}',
            'preconditions': f'Precondition {i}' * 10,  # 较长的前置条件
            'steps': [
                {
                    'step_number': j,
                    'action': f'Action {i}-{j}' * 5,
                    'expected': f'Expected {i}-{j}' * 5
                }
                for j in range(1, 6)  # 每个用例 5 个步骤
            ],
            'expected_result': f'Result {i}' * 10,
            'priority': 'medium',
            'type': 'functional'
        }
        for i in range(100)
    ]
    
    formatted = run_async(tool.execute(test_cases))
    
    # 序列化为 JSON
    json_str = json.dumps({'test_cases': formatted}, ensure_ascii=False)
    
    # 验证可以解析
    parsed = json.loads(json_str)
    
    # 验证数据完整性
    assert len(parsed['test_cases']) == 100
    assert all('title' in case for case in parsed['test_cases'])
    assert all(len(case['steps']) == 5 for case in parsed['test_cases'])


def test_property_json_nested_structure():
    """测试 JSON 输出正确处理嵌套结构"""
    tool = FormatTestCaseTool()
    
    test_case = {
        'title': 'Nested Structure Test',
        'preconditions': 'Setup complete',
        'steps': [
            {
                'step_number': 1,
                'action': 'Step with nested data: {"user": {"name": "John", "age": 30}}',
                'expected': 'Response: {"status": "success", "data": {"id": 123}}'
            }
        ],
        'expected_result': 'All nested structures handled correctly',
        'priority': 'high',
        'type': 'functional'
    }
    
    formatted = run_async(tool.execute([test_case]))
    
    # 序列化为 JSON
    json_str = json.dumps({'test_cases': formatted}, ensure_ascii=False)
    
    # 验证可以解析
    parsed = json.loads(json_str)
    
    # 验证嵌套的 JSON 字符串被正确转义
    case = parsed['test_cases'][0]
    assert '{"user":' in case['steps'][0]['action'] or '"user"' in case['steps'][0]['action']
