"""
生成工具

提供测试用例生成和格式化能力，使用 LLM 生成详细的测试用例。
"""

import json
from typing import List, Dict, Any, Optional
from .base import BaseTool, ToolError
from app.integration import BRConnectorClient


class GenerateTestCaseTool(BaseTool):
    """
    生成测试用例工具。
    
    基于测试点和上下文信息，使用 LLM 生成详细的测试用例，包括：
    - 测试用例标题
    - 前置条件
    - 测试步骤（详细、可执行）
    - 预期结果
    - 优先级
    - 测试类型
    """
    
    def __init__(self, llm_client: BRConnectorClient):
        """
        初始化测试用例生成工具。
        
        Args:
            llm_client: BRConnector 客户端（Claude API）
        """
        super().__init__(
            name="generate_test_case",
            description="基于测试点生成详细的测试用例"
        )
        self.llm_client = llm_client
    
    async def execute(
        self,
        test_point: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行测试用例生成。
        
        Args:
            test_point: 测试点信息（来自 ExtractTestPointsTool）
            context: 上下文信息（需求分析、历史用例等）
            **kwargs: 其他参数（如 API 密钥、模型等）
            
        Returns:
            详细的测试用例，包含：
            - title: 测试用例标题
            - preconditions: 前置条件
            - steps: 测试步骤列表（每步包含 step_number, action, expected）
            - expected_result: 预期结果
            - priority: 优先级（high/medium/low）
            - type: 测试类型（functional/boundary/exception）
            
        Raises:
            ToolError: 如果生成失败
        """
        try:
            self.logger.info(f"生成测试用例: {test_point.get('description', 'Unknown')[:50]}...")
            
            # 构建提示词
            prompt = self._build_prompt(test_point, context or {})
            
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
                temperature=0.7,  # 使用中等温度以平衡创造性和确定性
                max_tokens=2000,
            )
            
            # 解析 LLM 响应
            test_case = self._parse_response(response)
            
            # 确保优先级和类型与测试点一致
            test_case["priority"] = test_point.get("priority", "medium")
            test_case["type"] = test_point.get("type", "functional")
            
            self.logger.info(f"测试用例生成完成: {test_case.get('title', 'Unknown')}")
            return test_case
        
        except Exception as e:
            self.logger.error(f"测试用例生成失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"生成测试用例失败: {str(e)}",
                details={"test_point": test_point.get("description"), "error": str(e)}
            )
    
    def _build_prompt(self, test_point: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        构建生成测试用例的提示词。
        
        Args:
            test_point: 测试点信息
            context: 上下文信息
            
        Returns:
            提示词字符串
        """
        # 提取上下文信息
        requirement_analysis = context.get("requirement_analysis", {})
        historical_cases = context.get("historical_cases", [])
        
        # 构建历史用例参考
        historical_ref = ""
        if historical_cases:
            historical_ref = "\n\n参考历史测试用例（学习格式和风格）：\n"
            for i, case in enumerate(historical_cases[:2], 1):  # 只取前2个
                historical_ref += f"\n示例 {i}:\n"
                historical_ref += f"标题: {case.get('title', 'N/A')}\n"
                if case.get('content'):
                    historical_ref += f"内容: {case.get('content', '')[:200]}...\n"
        
        return f"""你是一个测试用例设计专家。请基于以下测试点生成一个详细的、可执行的测试用例。

测试点信息：
- 描述: {test_point.get('description', '')}
- 类型: {test_point.get('type', 'functional')}
- 优先级: {test_point.get('priority', 'medium')}
- 原因: {test_point.get('rationale', '')}

需求上下文：
{json.dumps(requirement_analysis, ensure_ascii=False, indent=2) if requirement_analysis else '无'}
{historical_ref}

请生成一个详细的测试用例，包含：

1. **title**: 清晰、具体的测试用例标题（格式：测试[功能/场景]）
2. **preconditions**: 前置条件（执行测试前需要满足的条件）
3. **steps**: 测试步骤列表，每个步骤包含：
   - step_number: 步骤编号（1, 2, 3...）
   - action: 操作描述（具体、可执行）
   - expected: 该步骤的预期结果
4. **expected_result**: 整体预期结果（测试通过的标准）

输出格式（纯 JSON，不要包含任何其他文本）：
{{
  "title": "测试用例标题",
  "preconditions": "前置条件描述",
  "steps": [
    {{
      "step_number": 1,
      "action": "操作描述",
      "expected": "预期结果"
    }},
    ...
  ],
  "expected_result": "整体预期结果"
}}

注意：
- 标题要清晰、具体，能够准确描述测试内容
- 前置条件要完整，包括数据准备、环境配置等
- 测试步骤要详细、可执行，每步都有明确的操作和预期
- 步骤编号从 1 开始连续递增
- 预期结果要明确、可验证
- 只输出 JSON，不要包含任何解释或额外文本"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 响应为测试用例。
        
        Args:
            response: LLM 响应文本
            
        Returns:
            测试用例字典
            
        Raises:
            ToolError: 如果解析失败
        """
        try:
            # 尝试直接解析 JSON
            test_case = json.loads(response.strip())
            
            # 验证必需字段
            required_fields = ["title", "preconditions", "steps", "expected_result"]
            for field in required_fields:
                if field not in test_case:
                    if field == "steps":
                        test_case[field] = []
                    else:
                        test_case[field] = ""
            
            # 验证步骤格式
            if isinstance(test_case["steps"], list):
                for i, step in enumerate(test_case["steps"]):
                    if "step_number" not in step:
                        step["step_number"] = i + 1
                    if "action" not in step:
                        step["action"] = ""
                    if "expected" not in step:
                        step["expected"] = ""
            
            return test_case
        
        except json.JSONDecodeError as e:
            # 如果直接解析失败，尝试提取 JSON 部分
            self.logger.warning(f"JSON 解析失败，尝试提取 JSON 部分: {e}")
            
            # 查找 JSON 代码块
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    test_case = json.loads(json_match.group(1))
                    return test_case
                except json.JSONDecodeError:
                    pass
            
            # 查找花括号包围的内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    test_case = json.loads(json_match.group(0))
                    return test_case
                except json.JSONDecodeError:
                    pass
            
            raise ToolError(
                tool_name=self.name,
                message="无法解析 LLM 响应为 JSON",
                details={"response": response[:500], "error": str(e)}
            )


class FormatTestCaseTool(BaseTool):
    """
    格式化测试用例工具。
    
    将生成的测试用例格式化为标准结构，确保：
    - 字段完整性
    - 数据类型正确
    - 格式统一
    - 符合系统要求
    """
    
    def __init__(self):
        """初始化测试用例格式化工具。"""
        super().__init__(
            name="format_test_case",
            description="格式化测试用例为标准结构"
        )
    
    async def execute(
        self,
        test_cases: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        执行测试用例格式化。
        
        Args:
            test_cases: 测试用例列表（来自 GenerateTestCaseTool）
            **kwargs: 其他参数
            
        Returns:
            格式化后的测试用例列表
            
        Raises:
            ToolError: 如果格式化失败
        """
        try:
            self.logger.info(f"格式化 {len(test_cases)} 个测试用例")
            
            formatted_cases = []
            for i, test_case in enumerate(test_cases):
                try:
                    formatted_case = self._format_single_case(test_case, i + 1)
                    formatted_cases.append(formatted_case)
                except Exception as e:
                    self.logger.warning(f"格式化测试用例 {i+1} 失败: {e}")
                    # 继续处理其他用例
                    continue
            
            self.logger.info(f"成功格式化 {len(formatted_cases)} 个测试用例")
            return formatted_cases
        
        except Exception as e:
            self.logger.error(f"测试用例格式化失败: {e}")
            raise ToolError(
                tool_name=self.name,
                message=f"格式化测试用例失败: {str(e)}",
                details={"count": len(test_cases), "error": str(e)}
            )
    
    def _format_single_case(self, test_case: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        格式化单个测试用例。
        
        Args:
            test_case: 原始测试用例
            index: 用例索引（用于生成默认标题）
            
        Returns:
            格式化后的测试用例
        """
        formatted = {
            # 基本信息
            "title": str(test_case.get("title", f"测试用例 {index}")).strip(),
            "preconditions": str(test_case.get("preconditions", "")).strip(),
            "expected_result": str(test_case.get("expected_result", "")).strip(),
            
            # 优先级（标准化）
            "priority": self._normalize_priority(test_case.get("priority", "medium")),
            
            # 测试类型（标准化）
            "type": self._normalize_type(test_case.get("type", "functional")),
            
            # 测试步骤（格式化）
            "steps": self._format_steps(test_case.get("steps", [])),
        }
        
        return formatted
    
    def _normalize_priority(self, priority: Any) -> str:
        """
        标准化优先级。
        
        Args:
            priority: 原始优先级
            
        Returns:
            标准化的优先级（high/medium/low）
        """
        priority_str = str(priority).lower().strip()
        
        # 映射表
        priority_map = {
            "high": "high",
            "高": "high",
            "p0": "high",
            "p1": "high",
            "medium": "medium",
            "中": "medium",
            "p2": "medium",
            "low": "low",
            "低": "low",
            "p3": "low",
            "p4": "low",
        }
        
        return priority_map.get(priority_str, "medium")
    
    def _normalize_type(self, test_type: Any) -> str:
        """
        标准化测试类型。
        
        Args:
            test_type: 原始测试类型
            
        Returns:
            标准化的测试类型（functional/boundary/exception）
        """
        type_str = str(test_type).lower().strip()
        
        # 映射表
        type_map = {
            "functional": "functional",
            "功能": "functional",
            "功能测试": "functional",
            "boundary": "boundary",
            "边界": "boundary",
            "边界值": "boundary",
            "exception": "exception",
            "异常": "exception",
            "异常测试": "exception",
            "错误": "exception",
        }
        
        return type_map.get(type_str, "functional")
    
    def _format_steps(self, steps: Any) -> List[Dict[str, Any]]:
        """
        格式化测试步骤。
        
        Args:
            steps: 原始步骤列表
            
        Returns:
            格式化后的步骤列表
        """
        if not isinstance(steps, list):
            return []
        
        formatted_steps = []
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            
            formatted_step = {
                "step_number": int(step.get("step_number", i + 1)),
                "action": str(step.get("action", "")).strip(),
                "expected": str(step.get("expected", "")).strip(),
            }
            
            # 只添加有效的步骤（至少有操作描述）
            if formatted_step["action"]:
                formatted_steps.append(formatted_step)
        
        return formatted_steps
