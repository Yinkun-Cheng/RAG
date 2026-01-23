"""
质量审查 Agent

负责审查测试用例的质量和完整性。
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple, Optional
from app.integration.brconnector_client import BRConnectorClient, BRConnectorError
from app.agent.requirement_analysis_agent import AnalysisResult
from app.agent.test_design_agent import TestCaseDesign

logger = logging.getLogger(__name__)


@dataclass
class ReviewResult:
    """质量审查结果"""
    coverage_score: int  # 覆盖率评分 (0-100)
    issues: List[str]  # 发现的问题
    suggestions: List[str]  # 改进建议
    approved_cases: List[int]  # 通过的测试用例索引
    rejected_cases: List[Tuple[int, str]]  # 拒绝的测试用例（索引，原因）
    overall_quality: str  # 整体质量: 'excellent' | 'good' | 'needs_improvement'
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewResult':
        """从字典创建"""
        # 转换 rejected_cases 为元组列表
        if 'rejected_cases' in data and isinstance(data['rejected_cases'], list):
            data['rejected_cases'] = [
                tuple(item) if isinstance(item, list) else item
                for item in data['rejected_cases']
            ]
        return cls(**data)


class QualityReviewAgent:
    """
    质量审查专家 Agent
    
    职责：
    - 检查测试覆盖率完整性
    - 验证测试用例结构
    - 检测重复测试用例
    - 验证是否符合标准
    - 提供改进建议
    """
    
    # Prompt 模板
    SYSTEM_PROMPT = """你是一位资深的质量保证专家，负责审查测试用例的质量和完整性。

你的任务是评估测试用例，依据以下标准：

1. **覆盖率完整性**:
   - 是否覆盖所有功能点？
   - 是否测试了异常条件？
   - 是否包含边界值？

2. **结构质量**:
   - 标题是否清晰、描述性强？
   - 前置条件是否完整？
   - 步骤是否可操作、有编号？
   - 预期结果是否具体、可衡量？

3. **重复检查**:
   - 是否有冗余的测试用例？
   - 是否可以合并某些用例？

4. **标准合规性**:
   - 是否遵循命名约定？
   - 优先级分配是否合理？
   - 类型分类是否正确？

请提供：
- 覆盖率评分 (0-100)
- 发现的问题列表
- 改进建议列表
- 通过的测试用例索引
- 拒绝的测试用例（索引和原因）
- 整体质量评估

请以 JSON 格式输出审查结果。"""
    
    REVIEW_PROMPT_TEMPLATE = """请审查以下测试用例的质量和完整性：

测试用例：
{test_cases}

原始需求：
{requirement}

需求分析：
{analysis}

请提供审查结果，使用以下 JSON 格式：

```json
{{
  "coverage_score": 85,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"],
  "approved_cases": [0, 1, 2],
  "rejected_cases": [[3, "拒绝原因"]],
  "overall_quality": "good"
}}
```

注意：
- coverage_score 应该是 0-100 的整数
- approved_cases 是通过审查的测试用例索引数组
- rejected_cases 是 [索引, 原因] 对的数组
- overall_quality 应该是 'excellent', 'good', 或 'needs_improvement'"""
    
    def __init__(self, brconnector_client: BRConnectorClient):
        """
        初始化质量审查 Agent
        
        Args:
            brconnector_client: BRConnector 客户端（用于调用 Claude API）
        """
        self.llm = brconnector_client
        self.logger = logging.getLogger(f"{__name__}.QualityReviewAgent")
    
    async def review(
        self,
        test_cases: List[TestCaseDesign],
        requirement: str,
        analysis: AnalysisResult
    ) -> ReviewResult:
        """
        审查测试用例的质量和完整性
        
        Args:
            test_cases: 测试用例设计列表
            requirement: 原始需求描述
            analysis: 需求分析结果
            
        Returns:
            审查结果
            
        Raises:
            BRConnectorError: 如果 LLM 调用失败
            ValueError: 如果无法解析 LLM 响应
        """
        self.logger.info(f"开始审查 {len(test_cases)} 个测试用例")
        
        # 准备测试用例数据
        test_cases_data = [
            {
                'index': i,
                'title': tc.title,
                'preconditions': tc.preconditions,
                'steps': tc.steps,
                'expected_result': tc.expected_result,
                'priority': tc.priority,
                'type': tc.type
            }
            for i, tc in enumerate(test_cases)
        ]
        
        # 构建提示词
        prompt = self.REVIEW_PROMPT_TEMPLATE.format(
            test_cases=json.dumps(test_cases_data, ensure_ascii=False, indent=2),
            requirement=requirement,
            analysis=json.dumps(analysis.to_dict(), ensure_ascii=False, indent=2)
        )
        
        try:
            # 调用 LLM
            self.logger.debug("调用 Claude API 进行质量审查")
            response = await self.llm.chat_simple(
                prompt=prompt,
                system=self.SYSTEM_PROMPT,
                temperature=0.3,  # 较低温度以获得更一致的评估
                max_tokens=2000
            )
            
            self.logger.debug(f"收到 LLM 响应，长度: {len(response)} 字符")
            
            # 解析响应
            review_result = self._parse_review(response)
            
            self.logger.info(
                f"质量审查完成: 覆盖率 {review_result.coverage_score}%, "
                f"通过 {len(review_result.approved_cases)} 个, "
                f"拒绝 {len(review_result.rejected_cases)} 个, "
                f"整体质量: {review_result.overall_quality}"
            )
            
            return review_result
        
        except BRConnectorError as e:
            self.logger.error(f"LLM 调用失败: {e}")
            raise
        except Exception as e:
            self.logger.error(f"质量审查失败: {e}")
            raise ValueError(f"质量审查失败: {e}") from e
    
    def _parse_review(self, raw_result: str) -> ReviewResult:
        """
        解析 LLM 输出为审查结果
        
        Args:
            raw_result: LLM 的原始响应
            
        Returns:
            解析后的审查结果
            
        Raises:
            ValueError: 如果无法解析响应
        """
        try:
            # 尝试提取 JSON（可能在 markdown 代码块中）
            json_str = raw_result.strip()
            
            # 如果响应包含 markdown 代码块，提取其中的 JSON
            if "```json" in json_str:
                start = json_str.find("```json") + 7
                end = json_str.find("```", start)
                json_str = json_str[start:end].strip()
            elif "```" in json_str:
                start = json_str.find("```") + 3
                end = json_str.find("```", start)
                json_str = json_str[start:end].strip()
            
            # 解析 JSON
            data = json.loads(json_str)
            
            # 验证和标准化字段
            if 'coverage_score' not in data:
                self.logger.warning("缺少 coverage_score，使用默认值 0")
                data['coverage_score'] = 0
            
            if 'issues' not in data:
                data['issues'] = []
            
            if 'suggestions' not in data:
                data['suggestions'] = []
            
            if 'approved_cases' not in data:
                data['approved_cases'] = []
            
            if 'rejected_cases' not in data:
                data['rejected_cases'] = []
            
            if 'overall_quality' not in data:
                # 根据覆盖率评分推断质量
                score = data['coverage_score']
                if score >= 90:
                    data['overall_quality'] = 'excellent'
                elif score >= 70:
                    data['overall_quality'] = 'good'
                else:
                    data['overall_quality'] = 'needs_improvement'
            
            # 标准化 overall_quality
            data['overall_quality'] = data['overall_quality'].lower()
            
            # 确保 coverage_score 在 0-100 范围内
            data['coverage_score'] = max(0, min(100, int(data['coverage_score'])))
            
            # 转换 rejected_cases 为元组列表
            if isinstance(data['rejected_cases'], list):
                rejected_cases = []
                for item in data['rejected_cases']:
                    if isinstance(item, list) and len(item) >= 2:
                        rejected_cases.append((int(item[0]), str(item[1])))
                    elif isinstance(item, tuple) and len(item) >= 2:
                        rejected_cases.append((int(item[0]), str(item[1])))
                data['rejected_cases'] = rejected_cases
            
            return ReviewResult.from_dict(data)
        
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON 解析失败: {e}")
            self.logger.debug(f"原始响应: {raw_result[:500]}...")
            raise ValueError(f"无法解析 LLM 响应为 JSON: {e}")
        except Exception as e:
            self.logger.error(f"解析审查结果失败: {e}")
            raise ValueError(f"解析审查结果失败: {e}")
