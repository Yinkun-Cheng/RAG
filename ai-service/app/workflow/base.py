"""
工作流基类

定义所有 Workflow 的基础接口和数据结构。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class WorkflowError(Exception):
    """工作流执行错误"""
    pass


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'metadata': self.metadata
        }


class BaseWorkflow(ABC):
    """工作流基类"""
    
    @abstractmethod
    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """
        执行工作流
        
        Args:
            input_data: 输入数据
            context: 上下文信息（可选）
            
        Returns:
            WorkflowResult: 工作流执行结果
            
        Raises:
            WorkflowError: 工作流执行失败
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工作流名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工作流描述"""
        pass
