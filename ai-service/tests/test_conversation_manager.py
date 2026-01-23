"""
ConversationManager 单元测试
"""

import pytest
from datetime import datetime
from app.agent.conversation_manager import (
    ConversationManager,
    Conversation,
    Message
)


def test_message_creation():
    """测试消息创建"""
    message = Message(
        role='user',
        content='测试消息',
        metadata={'test': 'data'}
    )
    
    assert message.role == 'user'
    assert message.content == '测试消息'
    assert message.metadata == {'test': 'data'}
    assert isinstance(message.timestamp, datetime)


def test_message_to_dict():
    """测试消息转换为字典"""
    message = Message(
        role='assistant',
        content='AI 响应',
        metadata={'model': 'claude'}
    )
    
    message_dict = message.to_dict()
    
    assert message_dict['role'] == 'assistant'
    assert message_dict['content'] == 'AI 响应'
    assert message_dict['metadata'] == {'model': 'claude'}
    assert 'timestamp' in message_dict


def test_message_from_dict():
    """测试从字典创建消息"""
    data = {
        'role': 'user',
        'content': '测试内容',
        'timestamp': '2024-01-01T00:00:00',
        'metadata': {'key': 'value'}
    }
    
    message = Message.from_dict(data)
    
    assert message.role == 'user'
    assert message.content == '测试内容'
    assert message.metadata == {'key': 'value'}


def test_conversation_creation():
    """测试对话创建"""
    conversation = Conversation(
        conversation_id='conv-123',
        project_id='proj-456',
        metadata={'user_id': 'user-789'}
    )
    
    assert conversation.conversation_id == 'conv-123'
    assert conversation.project_id == 'proj-456'
    assert conversation.metadata == {'user_id': 'user-789'}
    assert len(conversation.messages) == 0


def test_conversation_add_message():
    """测试添加消息到对话"""
    conversation = Conversation(
        conversation_id='conv-123',
        project_id='proj-456'
    )
    
    message = Message(role='user', content='你好')
    conversation.add_message(message)
    
    assert len(conversation.messages) == 1
    assert conversation.messages[0] == message


def test_conversation_get_messages():
    """测试获取消息列表"""
    conversation = Conversation(
        conversation_id='conv-123',
        project_id='proj-456'
    )
    
    # 添加多条消息
    for i in range(5):
        conversation.add_message(Message(role='user', content=f'消息 {i}'))
    
    # 获取所有消息
    all_messages = conversation.get_messages()
    assert len(all_messages) == 5
    
    # 获取最近 3 条消息
    recent_messages = conversation.get_messages(limit=3)
    assert len(recent_messages) == 3
    assert recent_messages[0].content == '消息 2'
    assert recent_messages[2].content == '消息 4'


def test_conversation_get_context():
    """测试获取对话上下文"""
    conversation = Conversation(
        conversation_id='conv-123',
        project_id='proj-456'
    )
    
    # 添加消息
    conversation.add_message(Message(role='user', content='问题 1'))
    conversation.add_message(Message(role='assistant', content='回答 1'))
    conversation.add_message(Message(role='user', content='问题 2'))
    
    # 获取上下文
    context = conversation.get_context(window_size=2)
    
    assert len(context) == 2
    assert context[0] == {'role': 'assistant', 'content': '回答 1'}
    assert context[1] == {'role': 'user', 'content': '问题 2'}


def test_conversation_to_dict():
    """测试对话转换为字典"""
    conversation = Conversation(
        conversation_id='conv-123',
        project_id='proj-456'
    )
    conversation.add_message(Message(role='user', content='测试'))
    
    conv_dict = conversation.to_dict()
    
    assert conv_dict['conversation_id'] == 'conv-123'
    assert conv_dict['project_id'] == 'proj-456'
    assert len(conv_dict['messages']) == 1
    assert 'created_at' in conv_dict
    assert 'updated_at' in conv_dict


def test_conversation_from_dict():
    """测试从字典创建对话"""
    data = {
        'conversation_id': 'conv-123',
        'project_id': 'proj-456',
        'messages': [
            {
                'role': 'user',
                'content': '测试',
                'timestamp': '2024-01-01T00:00:00',
                'metadata': {}
            }
        ],
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-01T00:00:00',
        'metadata': {}
    }
    
    conversation = Conversation.from_dict(data)
    
    assert conversation.conversation_id == 'conv-123'
    assert conversation.project_id == 'proj-456'
    assert len(conversation.messages) == 1


def test_conversation_manager_initialization():
    """测试对话管理器初始化"""
    manager = ConversationManager(default_window_size=5)
    
    assert manager.default_window_size == 5
    assert manager.get_conversation_count() == 0


def test_create_conversation():
    """测试创建对话"""
    manager = ConversationManager()
    
    conversation = manager.create_conversation(
        conversation_id='conv-123',
        project_id='proj-456',
        metadata={'user': 'test'}
    )
    
    assert conversation.conversation_id == 'conv-123'
    assert conversation.project_id == 'proj-456'
    assert manager.get_conversation_count() == 1


def test_get_conversation():
    """测试获取对话"""
    manager = ConversationManager()
    manager.create_conversation('conv-123', 'proj-456')
    
    conversation = manager.get_conversation('conv-123')
    
    assert conversation is not None
    assert conversation.conversation_id == 'conv-123'


def test_get_conversation_not_found():
    """测试获取不存在的对话"""
    manager = ConversationManager()
    
    conversation = manager.get_conversation('non-existent')
    
    assert conversation is None


def test_get_or_create_conversation():
    """测试获取或创建对话"""
    manager = ConversationManager()
    
    # 第一次调用，创建新对话
    conversation1 = manager.get_or_create_conversation('conv-123', 'proj-456')
    assert conversation1.conversation_id == 'conv-123'
    assert manager.get_conversation_count() == 1
    
    # 第二次调用，返回已存在的对话
    conversation2 = manager.get_or_create_conversation('conv-123', 'proj-456')
    assert conversation2 is conversation1
    assert manager.get_conversation_count() == 1


def test_add_message():
    """测试添加消息"""
    manager = ConversationManager()
    manager.create_conversation('conv-123', 'proj-456')
    
    message = manager.add_message(
        conversation_id='conv-123',
        role='user',
        content='测试消息',
        metadata={'test': True}
    )
    
    assert message.role == 'user'
    assert message.content == '测试消息'
    assert message.metadata == {'test': True}
    
    # 验证消息已添加到对话
    messages = manager.get_messages('conv-123')
    assert len(messages) == 1
    assert messages[0] == message


def test_add_message_to_nonexistent_conversation():
    """测试向不存在的对话添加消息"""
    manager = ConversationManager()
    
    with pytest.raises(ValueError, match="对话 .* 不存在"):
        manager.add_message('non-existent', 'user', '测试')


def test_get_messages():
    """测试获取消息列表"""
    manager = ConversationManager()
    manager.create_conversation('conv-123', 'proj-456')
    
    # 添加多条消息
    for i in range(5):
        manager.add_message('conv-123', 'user', f'消息 {i}')
    
    # 获取所有消息
    all_messages = manager.get_messages('conv-123')
    assert len(all_messages) == 5
    
    # 获取最近 3 条消息
    recent_messages = manager.get_messages('conv-123', limit=3)
    assert len(recent_messages) == 3


def test_get_messages_from_nonexistent_conversation():
    """测试从不存在的对话获取消息"""
    manager = ConversationManager()
    
    with pytest.raises(ValueError, match="对话 .* 不存在"):
        manager.get_messages('non-existent')


def test_get_context():
    """测试获取对话上下文"""
    manager = ConversationManager(default_window_size=2)
    manager.create_conversation('conv-123', 'proj-456')
    
    # 添加消息
    manager.add_message('conv-123', 'user', '问题 1')
    manager.add_message('conv-123', 'assistant', '回答 1')
    manager.add_message('conv-123', 'user', '问题 2')
    
    # 使用默认窗口大小
    context = manager.get_context('conv-123')
    assert len(context) == 2
    assert context[0]['content'] == '回答 1'
    assert context[1]['content'] == '问题 2'
    
    # 使用自定义窗口大小
    context_all = manager.get_context('conv-123', window_size=10)
    assert len(context_all) == 3


def test_get_context_from_nonexistent_conversation():
    """测试从不存在的对话获取上下文"""
    manager = ConversationManager()
    
    with pytest.raises(ValueError, match="对话 .* 不存在"):
        manager.get_context('non-existent')


def test_delete_conversation():
    """测试删除对话"""
    manager = ConversationManager()
    manager.create_conversation('conv-123', 'proj-456')
    
    assert manager.get_conversation_count() == 1
    
    # 删除对话
    result = manager.delete_conversation('conv-123')
    
    assert result is True
    assert manager.get_conversation_count() == 0
    assert manager.get_conversation('conv-123') is None


def test_delete_nonexistent_conversation():
    """测试删除不存在的对话"""
    manager = ConversationManager()
    
    result = manager.delete_conversation('non-existent')
    
    assert result is False


def test_list_conversations():
    """测试列出所有对话"""
    manager = ConversationManager()
    
    manager.create_conversation('conv-1', 'proj-1')
    manager.create_conversation('conv-2', 'proj-1')
    manager.create_conversation('conv-3', 'proj-2')
    
    # 列出所有对话
    all_conversations = manager.list_conversations()
    assert len(all_conversations) == 3
    
    # 列出特定项目的对话
    proj1_conversations = manager.list_conversations(project_id='proj-1')
    assert len(proj1_conversations) == 2
    assert all(c.project_id == 'proj-1' for c in proj1_conversations)


def test_clear_all():
    """测试清空所有对话"""
    manager = ConversationManager()
    
    manager.create_conversation('conv-1', 'proj-1')
    manager.create_conversation('conv-2', 'proj-2')
    
    assert manager.get_conversation_count() == 2
    
    manager.clear_all()
    
    assert manager.get_conversation_count() == 0


def test_export_conversation():
    """测试导出对话"""
    manager = ConversationManager()
    manager.create_conversation('conv-123', 'proj-456')
    manager.add_message('conv-123', 'user', '测试消息')
    
    exported = manager.export_conversation('conv-123')
    
    assert exported is not None
    assert exported['conversation_id'] == 'conv-123'
    assert exported['project_id'] == 'proj-456'
    assert len(exported['messages']) == 1


def test_export_nonexistent_conversation():
    """测试导出不存在的对话"""
    manager = ConversationManager()
    
    exported = manager.export_conversation('non-existent')
    
    assert exported is None


def test_import_conversation():
    """测试导入对话"""
    manager = ConversationManager()
    
    data = {
        'conversation_id': 'conv-123',
        'project_id': 'proj-456',
        'messages': [
            {
                'role': 'user',
                'content': '导入的消息',
                'timestamp': '2024-01-01T00:00:00',
                'metadata': {}
            }
        ],
        'created_at': '2024-01-01T00:00:00',
        'updated_at': '2024-01-01T00:00:00',
        'metadata': {}
    }
    
    conversation = manager.import_conversation(data)
    
    assert conversation.conversation_id == 'conv-123'
    assert manager.get_conversation_count() == 1
    assert len(manager.get_messages('conv-123')) == 1


def test_context_window_limit():
    """测试上下文窗口限制"""
    manager = ConversationManager(default_window_size=3)
    manager.create_conversation('conv-123', 'proj-456')
    
    # 添加 10 条消息
    for i in range(10):
        manager.add_message('conv-123', 'user', f'消息 {i}')
    
    # 获取上下文（应该只返回最近 3 条）
    context = manager.get_context('conv-123')
    
    assert len(context) == 3
    assert context[0]['content'] == '消息 7'
    assert context[1]['content'] == '消息 8'
    assert context[2]['content'] == '消息 9'


def test_multiple_conversations():
    """测试管理多个对话"""
    manager = ConversationManager()
    
    # 创建多个对话
    manager.create_conversation('conv-1', 'proj-1')
    manager.create_conversation('conv-2', 'proj-1')
    manager.create_conversation('conv-3', 'proj-2')
    
    # 向不同对话添加消息
    manager.add_message('conv-1', 'user', '对话1的消息')
    manager.add_message('conv-2', 'user', '对话2的消息')
    manager.add_message('conv-3', 'user', '对话3的消息')
    
    # 验证每个对话的消息独立
    assert len(manager.get_messages('conv-1')) == 1
    assert len(manager.get_messages('conv-2')) == 1
    assert len(manager.get_messages('conv-3')) == 1
    
    assert manager.get_messages('conv-1')[0].content == '对话1的消息'
    assert manager.get_messages('conv-2')[0].content == '对话2的消息'
    assert manager.get_messages('conv-3')[0].content == '对话3的消息'
