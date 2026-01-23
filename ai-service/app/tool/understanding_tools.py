"""
理解工具

提供需求解析和测试点提取能力，使用 LLM 理解自然语言需求。
"""

import json
from typing import List, Dict, Any, Optional
from .base import BaseTool, ToolError
from app.integration import BRConnectorClient


class ParseRequirementTool(BaseTool):
    """
    解析需求工具。
    
    使用 LLM 将自然语言需求解析为结构化格式，提取：
    - 功能名称
    - 功能描述
    - 功能点列表
    - 约束条件
    - 验收标准
    """
    
    def __init__(self, llm_client: BRConnectorClient):
        """
        初始化需求解析工具。
        
        Args:
            llm_client: BRConnector 客户端（Claude API）
        """
        super().__init__(
            name="parse_requirement",
            description="将自然语言需求解析为结构化格式"
        )
        self.llm_client = llm_client
    
    async def execute(
        self,
        requirement: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行需求解析。
        
        Args:
            requirement: 需求文本（自然语言）
            **kwargs: 其他参数（如 API 密钥、模型等）
            
        Returns:
            结构化的需求信息，包含：
            - feature_name: 功能名称
            - description: 功能描述
            - functional_points: 功能点列表
            - constraints: 约束条件列表
            - acceptance_criteria: 验收标准列表
            
        Raises:
            ToolError: 如果解析失败
        """
        try:
            self.logger.info(f"解析需求: {requirement[:100]}...")
            
            # 构建提示词
            prompt = self._build_prompt(requirement)
            
            # 调用 LLM
            response = await self.llm_client.chat(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                api_key=kwargs.get("api_key"),
                model=kwargs.get("model"),
                base_url=kwargs.get("base_url"),
                temperature=0.3,  # 使用较低的温度以获得更确定的输出
                max_tokens=2000,
            )
            
            # 解析 LLM 响应
            result = self._parse_response(response)
            
            self.logger.info(f"需求解析完成: {result.get('feature_name', 'Unknown')}")
            return result
        
        except Exception as e:
            self.logger.error(f"需求解析失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"解析需求失败: {str(e)}",
                details={"requirement": requirement[:200], "error": str(e)}
            )
    
    def _build_prompt(self, requirement: str) -> str:
        """
        构建解析需求的提示词。
        
        Args:
            requirement: 需求文本
            
        Returns:
            提示词字符串
        """
        return f"""你是一个需求分析专家。请将以下需求解析为结构化的 JSON 格式。

需求描述：
{requirement}

请提取以下信息：
1. feature_name: 功能名称（简短、清晰）
2. description: 功能描述（详细说明功能的目的和价值）
3. functional_points: 功能点列表（具体的功能要求，每个功能点一句话）
4. constraints: 约束条件列表（性能、安全、兼容性等约束）
5. acceptance_criteria: 验收标准列表（如何验证功能是否完成）

输出格式（纯 JSON，不要包含任何其他文本）：
{{
  "feature_name": "功能名称",
  "description": "功能描述",
  "functional_points": ["功能点1", "功能点2", ...],
  "constraints": ["约束1", "约束2", ...],
  "acceptance_criteria": ["标准1", "标准2", ...]
}}

注意：
- 如果某个字段无法从需求中提取，请使用空列表 [] 或空字符串 ""
- 功能点应该具体、可测试
- 验收标准应该明确、可衡量
- 只输出 JSON，不要包含任何解释或额外文本"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 响应为结构化数据。
        
        Args:
            response: LLM 响应文本
            
        Returns:
            结构化的需求信息
            
        Raises:
            ToolError: 如果解析失败
        """
        try:
            # 尝试直接解析 JSON
            result = json.loads(response.strip())
            
            # 验证必需字段
            required_fields = [
                "feature_name",
                "description",
                "functional_points",
                "constraints",
                "acceptance_criteria"
            ]
            
            for field in required_fields:
                if field not in result:
                    result[field] = [] if field != "feature_name" and field != "description" else ""
            
            return result
        
        except json.JSONDecodeError as e:
            # 如果直接解析失败，尝试提取 JSON 部分
            self.logger.warning(f"JSON 解析失败，尝试提取 JSON 部分: {e}")
            
            # 查找 JSON 代码块
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    return result
                except json.JSONDecodeError:
                    pass
            
            # 查找花括号包围的内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                    return result
                except json.JSONDecodeError:
                    pass
            
            raise ToolError(
                tool_name=self.name,
                message="无法解析 LLM 响应为 JSON",
                details={"response": response[:500], "error": str(e)}
            )


class ExtractTestPointsTool(BaseTool):
    """
    提取测试点工具。
    
    从需求分析结果中提取可测试的测试点，包括：
    - 功能测试点
    - 异常测试点
    - 边界值测试点
    """
    
    def __init__(self, llm_client: BRConnectorClient):
        """
        初始化测试点提取工具。
        
        Args:
            llm_client: BRConnector 客户端（Claude API）
        """
        super().__init__(
            name="extract_test_points",
            description="从需求分析中提取测试点"
        )
        self.llm_client = llm_client
    
    async def execute(
        self,
        requirement_analysis: Dict[str, Any],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行测试点提取。
        
        Args:
            requirement_analysis: 需求分析结果（来自 ParseRequirementTool）
            **kwargs: 其他参数（如 API 密钥、模型等）
            
        Returns:
            测试点列表，每个测试点包含：
            - type: 测试类型（functional/exception/boundary）
            - description: 测试点描述
            - priority: 优先级（high/medium/low）
            - rationale: 为什么需要这个测试点
            
        Raises:
            ToolError: 如果提取失败
        """
        try:
            self.logger.info(f"提取测试点: {requirement_analysis.get('feature_name', 'Unknown')}")
            
            # 构建提示词
            prompt = self._build_prompt(requirement_analysis)
            
            # 调用 LLM
            response = await self.llm_client.chat(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                api_key=kwargs.get("api_key"),
                model=kwargs.get("model"),
                base_url=kwargs.get("base_url"),
                temperature=0.5,  # 使用中等温度以平衡创造性和确定性
                max_tokens=3000,
            )
            
            # 解析 LLM 响应
            test_points = self._parse_response(response)
            
            self.logger.info(f"提取了 {len(test_points)} 个测试点")
            return test_points
        
        except Exception as e:
            self.logger.error(f"测试点提取失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"提取测试点失败: {str(e)}",
                details={"feature_name": requirement_analysis.get("feature_name"), "error": str(e)}
            )
    
    def _build_prompt(self, requirement_analysis: Dict[str, Any]) -> str:
        """
        构建提取测试点的提示词。
        
        Args:
            requirement_analysis: 需求分析结果
            
        Returns:
            提示词字符串
        """
        return f"""你是一个测试设计专家。基于以下需求分析，提取所有需要测试的测试点。

需求分析：
{json.dumps(requirement_analysis, ensure_ascii=False, indent=2)}

请提取以下类型的测试点：

1. **功能测试点（functional）**：
   - 验证每个功能点是否正常工作
   - 验证正常流程是否符合预期
   - 优先级：high

2. **异常测试点（exception）**：
   - 验证错误处理是否正确
   - 验证异常情况下的系统行为
   - 验证错误提示是否友好
   - 优先级：medium 或 high

3. **边界值测试点（boundary）**：
   - 验证输入的最小值、最大值
   - 验证边界条件下的行为
   - 验证特殊值（0、空、null 等）
   - 优先级：medium

输出格式（纯 JSON 数组，不要包含任何其他文本）：
[
  {{
    "type": "functional",
    "description": "测试点描述（具体、可执行）",
    "priority": "high",
    "rationale": "为什么需要这个测试点"
  }},
  ...
]

注意：
- 每个测试点应该具体、可执行
- 描述应该清晰说明要测试什么
- 优先级应该合理（high/medium/low）
- rationale 应该解释测试的重要性
- 只输出 JSON 数组，不要包含任何解释或额外文本"""
    
    def _parse_response(self, response: str) -> List[Dict[str, Any]]:
        """
        解析 LLM 响应为测试点列表。
        
        Args:
            response: LLM 响应文本
            
        Returns:
            测试点列表
            
        Raises:
            ToolError: 如果解析失败
        """
        try:
            # 尝试直接解析 JSON
            test_points = json.loads(response.strip())
            
            # 验证是否为列表
            if not isinstance(test_points, list):
                raise ToolError(
                    tool_name=self.name,
                    message="LLM 响应不是 JSON 数组",
                    details={"response": response[:500]}
                )
            
            # 验证每个测试点的字段
            for point in test_points:
                if "type" not in point:
                    point["type"] = "functional"
                if "description" not in point:
                    point["description"] = ""
                if "priority" not in point:
                    point["priority"] = "medium"
                if "rationale" not in point:
                    point["rationale"] = ""
            
            return test_points
        
        except json.JSONDecodeError as e:
            # 如果直接解析失败，尝试提取 JSON 部分
            self.logger.warning(f"JSON 解析失败，尝试提取 JSON 部分: {e}")
            
            # 查找 JSON 代码块
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    test_points = json.loads(json_match.group(1))
                    return test_points
                except json.JSONDecodeError:
                    pass
            
            # 查找方括号包围的内容
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                try:
                    test_points = json.loads(json_match.group(0))
                    return test_points
                except json.JSONDecodeError:
                    pass
            
            raise ToolError(
                tool_name=self.name,
                message="无法解析 LLM 响应为 JSON 数组",
                details={"response": response[:500], "error": str(e)}
            )
