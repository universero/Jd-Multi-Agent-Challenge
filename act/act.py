import json
from typing import Dict, List

from oxygent import oxy, MAS

from entity.step import Step
from util import util

"""
输入: Step
输出: Dict
执行Refine阶段得到的具体步骤
"""

ACT_EXECUTION_PROMPT = """
你是一个多智能体执行系统中的 **Act Agent（任务执行代理）**。
你的任务是：
**严格按照给定的指令执行具体的任务步骤**。

<输入说明>
你将接收到：
- prompt: ${prompt} (智能体的system级指令)
- tools: ${tools} (可使用的工具列表)
- actions: ${actions} (具体的行动步骤)

<输出要求>
你**必须且只能**输出一个 **JSON 对象**，不得包含任何其他内容。
JSON 的格式必须**严格遵循**以下 schema：
{
  "thought": "<执行思路和过程>",
  "result": <执行结果>,
  "status": "success"或"failed"
}

<详细规则>
1. 执行要求
- 严格按照给定的actions执行每一步
- 使用prompt中的system级指令指导你的行为
- 如果提供了tools，在需要时使用它们

2. 输出格式
- 必须输出有效的JSON格式
- 必须包含thought、result和status三个字段
- status只能是"success"或"failed"
- result可以是任何有效的JSON类型
- thought应详细说明你的执行过程和思路

3. 错误处理
- 如果执行过程中遇到错误，status设为"failed"
- 在result中说明具体的错误信息
- 在thought中解释错误发生的原因
"""


class Act(oxy.ChatAgent):
    def __init__(self, **kwargs):
        kwargs["prompt"] = ACT_EXECUTION_PROMPT
        super().__init__(**kwargs)

    async def act(self, mas: MAS, step: Step, previous_results: List[Dict] = None) -> Dict:
        """
        执行单个步骤
        
        Args:
            mas: MAS实例
            step: 要执行的步骤
            previous_results: 之前步骤的执行结果，用于上下文传递
            
        Returns:
            Dict: 执行结果，包含success、result、thought等字段
        """
        # 如果有之前的结果，将其添加到提示中
        context_prompt = ""
        if previous_results:
            context_prompt = "# 上下文信息\n" + "\n".join([
                f"## 步骤 {i+1} 结果\n" + 
                f"- 状态: {'成功' if result['success'] else '失败'}\n" +
                f"- 结果: {json.dumps(result.get('result', {}), ensure_ascii=False)}\n" +
                f"- 思考: {result.get('thought', '')}\n"
                for i, result in enumerate(previous_results)
            ])
            
        result = await mas.call(
            callee=self.name,  # 使用当前Act代理的名称
            arguments={
                "prompt": f"{context_prompt}\n\n{step.prompts}" if context_prompt else step.prompts,
                "tools": step.tools,
                "actions": step.actions,
                "previous_results": previous_results or []
            },
        )

        # 解析返回结果
        try:
            purified_result = util.purify_json(result)
            json_result = json.loads(purified_result)
            
            # 验证输出结构
            if not isinstance(json_result, dict):
                raise ValueError("执行结果必须是JSON对象")
            
            if "status" not in json_result:
                raise ValueError("执行结果缺少status字段")
            
            if "result" not in json_result:
                raise ValueError("执行结果缺少result字段")
            
            return {
                "success": json_result["status"] == "success",
                "result": json_result["result"],
                "thought": json_result.get("thought", ""),
                "raw": result
            }
        except json.JSONDecodeError as e:
            # 非JSON结果
            return {
                "success": True,
                "result": purified_result.strip(),
                "thought": "",
                "raw": result,
                "warning": "执行结果不是有效的JSON格式"
            }
        except Exception as e:
            # 其他错误
            return {
                "success": False,
                "error": str(e),
                "message": "执行结果解析失败"
            }
