"""
ConversationManager - 对话上下文管理器

负责管理多轮对话的历史记录、上下文传递和窗口管理。
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """对话消息"""
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """从字典创建消息"""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data.get('timestamp'), str) else data.get('timestamp', datetime.now()),
            metadata=data.get('metadata', {})
        )


@dataclass
class Conversation:
    """对话"""
    conversation_id: str
    project_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: Message) -> None:
        """添加消息到对话"""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """
        获取消息列表
        
        Args:
            limit: 限制返回的消息数量（最近的 N 条）
            
        Returns:
            消息列表
        """
        if limit is None or limit <= 0:
            return self.messages
        
        return self.messages[-limit:]
    
    def get_context(self, window_size: int = 10) -> List[Dict[str, str]]:
        """
        获取对话上下文（用于 LLM）
        
        Args:
            window_size: 上下文窗口大小（最近的 N 条消息）
            
        Returns:
            上下文消息列表，格式为 [{'role': 'user', 'content': '...'}]
        """
        recent_messages = self.get_messages(limit=window_size)
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in recent_messages
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'conversation_id': self.conversation_id,
            'project_id': self.project_id,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """从字典创建对话"""
        return cls(
            conversation_id=data['conversation_id'],
            project_id=data['project_id'],
            messages=[Message.from_dict(msg) for msg in data.get('messages', [])],
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            updated_at=datetime.fromisoformat(data['updated_at']) if isinstance(data.get('updated_at'), str) else data.get('updated_at', datetime.now()),
            metadata=data.get('metadata', {})
        )


class ConversationManager:
    """
    对话上下文管理器
    
    职责：
    - 管理多个对话的历史记录
    - 提供对话的存储和检索
    - 支持上下文窗口管理
    - 支持对话的创建、更新和删除
    """
    
    def __init__(self, default_window_size: int = 10):
        """
        初始化对话管理器
        
        Args:
            default_window_size: 默认上下文窗口大小
        """
        self.conversations: Dict[str, Conversation] = {}
        self.default_window_size = default_window_size
        
        logger.info(f"ConversationManager 初始化完成，默认窗口大小: {default_window_size}")
    
    def create_conversation(
        self,
        conversation_id: str,
        project_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        创建新对话
        
        Args:
            conversation_id: 对话 ID
            project_id: 项目 ID
            metadata: 元数据
            
        Returns:
            创建的对话对象
        """
        if conversation_id in self.conversations:
            logger.warning(f"对话 {conversation_id} 已存在，将被覆盖")
        
        conversation = Conversation(
            conversation_id=conversation_id,
            project_id=project_id,
            metadata=metadata or {}
        )
        
        self.conversations[conversation_id] = conversation
        logger.info(f"创建对话: {conversation_id} (项目: {project_id})")
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        获取对话
        
        Args:
            conversation_id: 对话 ID
            
        Returns:
            对话对象，如果不存在则返回 None
        """
        return self.conversations.get(conversation_id)
    
    def get_or_create_conversation(
        self,
        conversation_id: str,
        project_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        获取或创建对话
        
        Args:
            conversation_id: 对话 ID
            project_id: 项目 ID
            metadata: 元数据
            
        Returns:
            对话对象
        """
        conversation = self.get_conversation(conversation_id)
        
        if conversation is None:
            conversation = self.create_conversation(conversation_id, project_id, metadata)
        
        return conversation
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        添加消息到对话
        
        Args:
            conversation_id: 对话 ID
            role: 角色（'user' 或 'assistant'）
            content: 消息内容
            metadata: 元数据
            
        Returns:
            添加的消息对象
            
        Raises:
            ValueError: 如果对话不存在
        """
        conversation = self.get_conversation(conversation_id)
        
        if conversation is None:
            raise ValueError(f"对话 {conversation_id} 不存在")
        
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        conversation.add_message(message)
        logger.debug(f"添加消息到对话 {conversation_id}: {role} - {content[:50]}...")
        
        return message
    
    def get_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取对话的消息列表
        
        Args:
            conversation_id: 对话 ID
            limit: 限制返回的消息数量（最近的 N 条）
            
        Returns:
            消息列表
            
        Raises:
            ValueError: 如果对话不存在
        """
        conversation = self.get_conversation(conversation_id)
        
        if conversation is None:
            raise ValueError(f"对话 {conversation_id} 不存在")
        
        return conversation.get_messages(limit=limit)
    
    def get_context(
        self,
        conversation_id: str,
        window_size: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        获取对话上下文（用于 LLM）
        
        Args:
            conversation_id: 对话 ID
            window_size: 上下文窗口大小，如果为 None 则使用默认值
            
        Returns:
            上下文消息列表
            
        Raises:
            ValueError: 如果对话不存在
        """
        conversation = self.get_conversation(conversation_id)
        
        if conversation is None:
            raise ValueError(f"对话 {conversation_id} 不存在")
        
        if window_size is None:
            window_size = self.default_window_size
        
        return conversation.get_context(window_size=window_size)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        删除对话
        
        Args:
            conversation_id: 对话 ID
            
        Returns:
            是否成功删除
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"删除对话: {conversation_id}")
            return True
        
        logger.warning(f"尝试删除不存在的对话: {conversation_id}")
        return False
    
    def list_conversations(self, project_id: Optional[str] = None) -> List[Conversation]:
        """
        列出所有对话
        
        Args:
            project_id: 项目 ID，如果指定则只返回该项目的对话
            
        Returns:
            对话列表
        """
        conversations = list(self.conversations.values())
        
        if project_id is not None:
            conversations = [c for c in conversations if c.project_id == project_id]
        
        return conversations
    
    def clear_all(self) -> None:
        """清空所有对话"""
        count = len(self.conversations)
        self.conversations.clear()
        logger.info(f"清空所有对话，共 {count} 个")
    
    def get_conversation_count(self) -> int:
        """获取对话总数"""
        return len(self.conversations)
    
    def export_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        导出对话为字典
        
        Args:
            conversation_id: 对话 ID
            
        Returns:
            对话字典，如果不存在则返回 None
        """
        conversation = self.get_conversation(conversation_id)
        
        if conversation is None:
            return None
        
        return conversation.to_dict()
    
    def import_conversation(self, data: Dict[str, Any]) -> Conversation:
        """
        从字典导入对话
        
        Args:
            data: 对话字典
            
        Returns:
            导入的对话对象
        """
        conversation = Conversation.from_dict(data)
        self.conversations[conversation.conversation_id] = conversation
        
        logger.info(f"导入对话: {conversation.conversation_id}")
        
        return conversation
