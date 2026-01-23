"""
工具基类

为系统中所有工具提供抽象基类。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    所有工具的抽象基类。
    
    工具是可以组合成技能的原子能力。
    每个工具应该专注做好一件事。
    """
    
    def __init__(self, name: str, description: str):
        """
        初始化工具。
        
        Args:
            name: 工具名称
            description: 工具描述
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        执行工具。
        
        Args:
            **kwargs: 工具特定的参数
            
        Returns:
            工具执行结果
            
        Raises:
            ToolError: 如果工具执行失败
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class ToolError(Exception):
    """工具错误的基础异常类"""
    
    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化工具错误。
        
        Args:
            tool_name: 失败的工具名称
            message: 错误消息
            details: 可选的错误详情
        """
        self.tool_name = tool_name
        self.message = message
        self.details = details or {}
        super().__init__(f"[{tool_name}] {message}")
