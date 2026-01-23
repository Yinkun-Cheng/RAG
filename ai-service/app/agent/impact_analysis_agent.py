"""
影响分析 Agent

分析需求变更对现有测试用例和模块的影响。
"""

import logging
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from ..integration.brconnector_client import BRConnectorClient, BRConnectorError


logger = logging.getLogger(__name__)


@dataclass
class ImpactReport:
    """影响分析报告"""
    summary: str  # 影响摘要
    affected_modules: List[str]  # 受影响的模块列表
    affected_test_cases: List[Dict[str, Any]]  # 受影响的测试用例列表
    risk_level: str  # 风险等级：low, medium, high
    recommendations: List[str]  # 建议措施
    change_type: str  # 变更类型：feature_add, feature_modify, feature_remove, bug_fix
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'summary': self.summary,
            'affected_modules': self.affected_modules,
            'affected_test_cases': self.affected_test_cases,
            'risk_level': self.risk_level,
            'recommendations': self.recommendations,
            'change_type': self.change_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImpactReport':
        """从字典创建"""
        return cls(
            summary=data.get('summary', ''),
            affected_modules=data.get('affected_modules', []),
            affected_test_cases=data.get('affected_test_cases', []),
            risk_level=data.get('risk_level', 'medium'),
            recommendations=data.get('recommendations', []),
            change_type=data.get('change_type', 'feature_modify')
        )


class ImpactAnalysisAgent:
    """
    影响分析 Agent
    
    分析需求变更对现有系统的影响，包括：
    - 识别受影响的模块
    - 识别需要更新的测试用例
    - 评估变更风险
    - 提供建议措施
    """
    
    def __init__(self, brconnector_client: BRConnectorClient):
        """
        初始化影响分析 Agent
        
        Args:
            brconnector_client: BRConnector 客户端
        """
        self.brconnector = brconnector_client
        self.logger = logging.getLogger(f"{__name__}.ImpactAnalysisAgent")
    
    async def analyze_impact(
        self,
        change_description: str,
        related_prds: Optional[List[Dict[str, Any]]] = None,
        existing_test_cases: Optional[List[Dict[str, Any]]] = None
    ) -> ImpactReport:
        """
        分析需求变更的影响
        
        Args:
            change_description: 变更描述
            related_prds: 相关的历史 PRD
            existing_test_cases: 现有的测试用例
            
        Returns:
            影响分析报告
            
        Raises:
            BRConnectorError: 如果 LLM 调用失败
            ValueError: 如果无法解析 LLM 响应
        """
        self.logger.info(f"开始分析变更影响，变更描述长度: {len(change_description)} 字符")
        
        # 准备历史 PRD 上下文
        prd_context = ""
        if related_prds:
            prd_context = "相关历史 PRD：\n"
            for i, prd in enumerate(related_prds[:3], 1):  # 最多使用前 3 个
                prd_context += f"\n{i}. {prd.get('title', 'N/A')}\n"
                prd_context += f"   内容摘要: {prd.get('content', 'N/A')[:200]}...\n"
        
        # 准备现有测试用例上下文
        testcase_context = ""
        if existing_test_cases:
            testcase_context = "现有测试用例：\n"
            for i, case in enumerate(existing_test_cases[:5], 1):  # 最多使用前 5 个
                testcase_context += f"\n{i}. {case.get('title', 'N/A')}\n"
                testcase_context += f"   模块: {case.get('module', 'N/A')}\n"
                testcase_context += f"   优先级: {case.get('priority', 'N/A')}\n"
        
        # 构建提示词
        prompt = f"""你是一个专业的测试工程师，负责分析需求变更对现有系统的影响。

变更描述：
{change_description}

{prd_context}

{testcase_context}

请分析这个变更的影响，并以 JSON 格式返回分析报告，包含以下字段：

1. summary: 影响摘要（简要描述变更的主要影响）
2. affected_modules: 受影响的模块列表（数组，如 ["用户管理", "权限系统"]）
3. affected_test_cases: 受影响的测试用例列表（数组，每个元素包含 title, reason, action）
   - title: 测试用例标题
   - reason: 受影响的原因
   - action: 建议的操作（update, retest, remove, add_new）
4. risk_level: 风险等级（low, medium, high）
5. recommendations: 建议措施列表（数组，如 ["更新用户管理模块的测试用例", "增加新功能的测试覆盖"]）
6. change_type: 变更类型（feature_add, feature_modify, feature_remove, bug_fix）

请确保返回的是有效的 JSON 格式。"""

        try:
            # 调用 LLM
            response = await self.brconnector.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # 较低的温度以获得更一致的结果
                max_tokens=2000
            )
            
            # 提取响应内容
            content = response['content'][0]['text']
            self.logger.debug(f"LLM 响应: {content[:200]}...")
            
            # 解析 JSON 响应
            impact_data = self._parse_llm_response(content)
            
            # 创建影响报告
            report = ImpactReport.from_dict(impact_data)
            
            self.logger.info(
                f"影响分析完成: 风险等级={report.risk_level}, "
                f"受影响模块数={len(report.affected_modules)}, "
                f"受影响测试用例数={len(report.affected_test_cases)}"
            )
            
            return report
            
        except BRConnectorError as e:
            self.logger.error(f"LLM 调用失败: {e}")
            raise
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.error(f"解析 LLM 响应失败: {e}")
            raise ValueError(f"无法解析 LLM 响应: {str(e)}")
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """
        解析 LLM 响应
        
        Args:
            content: LLM 响应内容
            
        Returns:
            解析后的字典
            
        Raises:
            ValueError: 如果无法解析
        """
        # 尝试提取 JSON（可能在 markdown 代码块中）
        content = content.strip()
        
        # 如果响应在 markdown 代码块中
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            if end != -1:
                content = content[start:end].strip()
        
        # 解析 JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试查找 JSON 对象
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("响应中未找到有效的 JSON")
        
        # 验证必需字段
        required_fields = ['summary', 'affected_modules', 'affected_test_cases', 'risk_level', 'recommendations', 'change_type']
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"响应中缺少字段: {field}，使用默认值")
                if field == 'summary':
                    data[field] = "影响分析完成"
                elif field in ['affected_modules', 'affected_test_cases', 'recommendations']:
                    data[field] = []
                elif field == 'risk_level':
                    data[field] = 'medium'
                elif field == 'change_type':
                    data[field] = 'feature_modify'
        
        # 标准化风险等级
        if data['risk_level'] not in ['low', 'medium', 'high']:
            self.logger.warning(f"无效的风险等级: {data['risk_level']}，使用 medium")
            data['risk_level'] = 'medium'
        
        # 标准化变更类型
        valid_change_types = ['feature_add', 'feature_modify', 'feature_remove', 'bug_fix']
        if data['change_type'] not in valid_change_types:
            self.logger.warning(f"无效的变更类型: {data['change_type']}，使用 feature_modify")
            data['change_type'] = 'feature_modify'
        
        return data
