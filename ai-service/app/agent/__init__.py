"""
Agent 模块

包含所有 AI Agent 实现。
"""

from app.agent.requirement_analysis_agent import (
    RequirementAnalysisAgent,
    AnalysisResult,
)
from app.agent.test_design_agent import (
    TestDesignAgent,
    TestCaseDesign,
)
from app.agent.quality_review_agent import (
    QualityReviewAgent,
    ReviewResult,
)
from app.agent.impact_analysis_agent import (
    ImpactAnalysisAgent,
    ImpactReport,
)
from app.agent.test_engineer_agent import (
    TestEngineerAgent,
    AgentResponse,
    TaskType,
)
from app.agent.conversation_manager import (
    ConversationManager,
    Conversation,
    Message,
)

__all__ = [
    'RequirementAnalysisAgent',
    'AnalysisResult',
    'TestDesignAgent',
    'TestCaseDesign',
    'QualityReviewAgent',
    'ReviewResult',
    'ImpactAnalysisAgent',
    'ImpactReport',
    'TestEngineerAgent',
    'AgentResponse',
    'TaskType',
    'ConversationManager',
    'Conversation',
    'Message',
]
