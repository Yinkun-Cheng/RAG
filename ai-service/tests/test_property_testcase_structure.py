"""
属性测试：测试用例结构完整性

属性 10: 测试用例结构完整性
验证需求 4.2: 所有生成的测试用例必须包含完整的必需字段
"""

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
    action=st.text(min_size=5, max_size=200),
    expected=st.text(min_size=5, max_size=200)
)

# 生成有效的测试用例
valid_test_case_strategy = st.builds(
    dict,
    title=st.text(min_size=5, max_size=200),
    preconditions=st.text(min_size=0, max_size=500),
    steps=st.lists(test_step_strategy, min_size=1, max_size=10),
    expected_result=st.text(min_size=5, max_size=500),
    priority=st.sampled_from(['high', 'medium', 'low', 'High', 'Medium', 'Low']),
    type=st.sampled_from(['functional', 'boundary', 'exception', 'Functional', 'Boundary', 'Exception'])
)


# ============================================================================
# 属性 10: 测试用例结构完整性
# ============================================================================

@given(test_case=valid_test_case_strategy)
@settings(max_examples=100, deadline=None)
def test_property_test_case_structure_completeness(test_case):
    """
    属性 10: 测试用例结构完整性
    
    对于任何生成的测试用例，它必须包含所有必需字段：
    - title: 标题（非空字符串）
    - preconditions: 前置条件（字符串，可为空）
    - steps: 测试步骤（至少一个步骤）
    - expected_result: 预期结果（非空字符串）
    - priority: 优先级（high/medium/low）
    - type: 类型（functional/boundary/exception）
    """
    tool = FormatTestCaseTool()
    
    # 格式化测试用例（同步运行异步方法）
    formatted = run_async(tool.execute([test_case]))
    
    # 验证返回结果是列表
    assert isinstance(formatted, list), "格式化结果应该是列表"
    assert len(formatted) > 0, "格式化结果不应为空"
    
    # 验证第一个测试用例的结构
    case = formatted[0]
    
    # 必需字段存在性检查
    assert 'title' in case, "测试用例必须包含 title 字段"
    assert 'preconditions' in case, "测试用例必须包含 preconditions 字段"
    assert 'steps' in case, "测试用例必须包含 steps 字段"
    assert 'expected_result' in case, "测试用例必须包含 expected_result 字段"
    assert 'priority' in case, "测试用例必须包含 priority 字段"
    assert 'type' in case, "测试用例必须包含 type 字段"
    
    # 字段类型检查
    assert isinstance(case['title'], str), "title 必须是字符串"
    assert isinstance(case['preconditions'], str), "preconditions 必须是字符串"
    assert isinstance(case['steps'], list), "steps 必须是列表"
    assert isinstance(case['expected_result'], str), "expected_result 必须是字符串"
    assert isinstance(case['priority'], str), "priority 必须是字符串"
    assert isinstance(case['type'], str), "type 必须是字符串"
    
    # 字段值有效性检查
    assert len(case['title']) > 0, "title 不能为空"
    assert len(case['steps']) > 0, "至少需要一个测试步骤"
    assert len(case['expected_result']) > 0, "expected_result 不能为空"
    
    # 优先级值检查
    assert case['priority'] in ['high', 'medium', 'low'], \
        f"priority 必须是 high/medium/low 之一，实际值: {case['priority']}"
    
    # 类型值检查
    assert case['type'] in ['functional', 'boundary', 'exception'], \
        f"type 必须是 functional/boundary/exception 之一，实际值: {case['type']}"
    
    # 测试步骤结构检查
    for i, step in enumerate(case['steps']):
        assert isinstance(step, dict), f"步骤 {i} 必须是字典"
        assert 'step_number' in step, f"步骤 {i} 必须包含 step_number"
        assert 'action' in step, f"步骤 {i} 必须包含 action"
        assert 'expected' in step, f"步骤 {i} 必须包含 expected"
        
        assert isinstance(step['step_number'], int), f"步骤 {i} 的 step_number 必须是整数"
        assert isinstance(step['action'], str), f"步骤 {i} 的 action 必须是字符串"
        assert isinstance(step['expected'], str), f"步骤 {i} 的 expected 必须是字符串"
        
        assert step['step_number'] > 0, f"步骤 {i} 的 step_number 必须大于 0"
        assert len(step['action']) > 0, f"步骤 {i} 的 action 不能为空"


# ============================================================================
# 边界情况测试
# ============================================================================

def test_property_minimum_valid_test_case():
    """测试最小有效测试用例"""
    tool = FormatTestCaseTool()
    
    minimal_case = {
        'title': 'Test',
        'preconditions': '',
        'steps': [
            {'step_number': 1, 'action': 'Do something', 'expected': 'Result'}
        ],
        'expected_result': 'Success',
        'priority': 'medium',
        'type': 'functional'
    }
    
    formatted = run_async(tool.execute([minimal_case]))
    
    assert len(formatted) == 1
    case = formatted[0]
    
    # 验证所有必需字段存在
    assert 'title' in case
    assert 'preconditions' in case
    assert 'steps' in case
    assert 'expected_result' in case
    assert 'priority' in case
    assert 'type' in case
    
    # 验证值
    assert case['title'] == 'Test'
    assert case['preconditions'] == ''
    assert len(case['steps']) == 1
    assert case['expected_result'] == 'Success'


def test_property_multiple_test_cases():
    """测试多个测试用例的结构完整性"""
    tool = FormatTestCaseTool()
    
    test_cases = [
        {
            'title': f'Test Case {i}',
            'preconditions': f'Precondition {i}',
            'steps': [
                {'step_number': 1, 'action': f'Action {i}', 'expected': f'Expected {i}'}
            ],
            'expected_result': f'Result {i}',
            'priority': 'high',
            'type': 'functional'
        }
        for i in range(5)
    ]
    
    formatted = run_async(tool.execute(test_cases))
    
    assert len(formatted) == 5, "应该返回 5 个格式化的测试用例"
    
    # 验证每个测试用例的结构
    for i, case in enumerate(formatted):
        assert 'title' in case
        assert 'preconditions' in case
        assert 'steps' in case
        assert 'expected_result' in case
        assert 'priority' in case
        assert 'type' in case
        
        assert case['title'] == f'Test Case {i}'
        assert len(case['steps']) > 0


def test_property_case_insensitive_priority_and_type():
    """测试优先级和类型的大小写不敏感性"""
    tool = FormatTestCaseTool()
    
    test_cases = [
        {
            'title': 'Test High Priority',
            'preconditions': '',
            'steps': [{'step_number': 1, 'action': 'Action', 'expected': 'Expected'}],
            'expected_result': 'Result',
            'priority': 'High',  # 大写
            'type': 'Functional'  # 大写
        },
        {
            'title': 'Test Medium Priority',
            'preconditions': '',
            'steps': [{'step_number': 1, 'action': 'Action', 'expected': 'Expected'}],
            'expected_result': 'Result',
            'priority': 'MEDIUM',  # 全大写
            'type': 'BOUNDARY'  # 全大写
        }
    ]
    
    formatted = run_async(tool.execute(test_cases))
    
    # 验证优先级和类型被标准化为小写
    assert formatted[0]['priority'] == 'high'
    assert formatted[0]['type'] == 'functional'
    assert formatted[1]['priority'] == 'medium'
    assert formatted[1]['type'] == 'boundary'


def test_property_empty_steps_filtered():
    """测试空步骤被过滤"""
    tool = FormatTestCaseTool()
    
    test_case = {
        'title': 'Test',
        'preconditions': '',
        'steps': [
            {'step_number': 1, 'action': 'Valid action', 'expected': 'Valid expected'},
            {'step_number': 2, 'action': '', 'expected': ''},  # 空步骤
            {'step_number': 3, 'action': 'Another action', 'expected': 'Another expected'}
        ],
        'expected_result': 'Result',
        'priority': 'medium',
        'type': 'functional'
    }
    
    formatted = run_async(tool.execute([test_case]))
    
    # 验证空步骤被过滤
    assert len(formatted[0]['steps']) == 2, "空步骤应该被过滤"
    assert formatted[0]['steps'][0]['action'] == 'Valid action'
    assert formatted[0]['steps'][1]['action'] == 'Another action'
