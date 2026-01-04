import json
from typing import List

from oxygent import oxy, MAS
from entity.target import Target
from entity.step import Step
from entity.cst import *
from util import util

REFINE_PROMPT = """
你是一个多智能体执行系统中的 **Refine Agent（任务细化代理）**。
你的任务是：
**给定一个高层执行目标（Target），将其分解为一组具体、可执行的步骤（Steps）。**
每一个 Step **必须能够由单一的、具备明确职责的专用智能体直接执行**。
不能在执行步骤中给出过于具体分析, 更不能随意的得出结论导致后续环节错误 

<输入说明>
你将接收到：
- query: ${query} (原始问题, 可以参考, 但要聚焦当前目标)
- target：${target} (需要完成的高层目标)
- requirement：${requirement} (额外的约束条件或特殊要求)

<输出要求>
你**必须且只能**输出一个 **JSON 对象**，不得包含任何其他内容。
JSON 的格式必须**严格遵循**以下 schema：
{
  "steps": [
    {
      "callee": "<agent_name>",
      "prompt": "<该智能体的 system 级指令>",
      "tools": ["<tool_name_1>", "<tool_name_2>"],
      "actions": [
        "<行动步骤 1>",
        "<行动步骤 2>",
        "<行动步骤 3>"
      ]
    }
  ]
}

<详细规则>
1. 步骤拆解（Step Decomposition）
- 如有必要，将目标拆解为多个步骤。
- 每个步骤应在逻辑上相对独立，并且可以按顺序执行。
- 避免过度细粒度拆分；每个步骤应代表一个有意义的任务单元。
- 对于简单的思考过程可以直接一个步骤, 指导思考过程即可
- 生成过程中不应该直接思考更不能直接得出结论, 只需要指导思考过程

2. 智能体选择（callee）
- 为每个步骤指定一个清晰、具有描述性的智能体名称, 需要和执行的任务相关, 不能是宽泛的search_agent之类的。
- 不同步骤必须使用不同的智能体，其职责应有所区分。
- 智能体名称应体现其执行的行为，例如："搜索Github获取人物"、"思考金条切分"。

3. 智能体指令（prompt）
- prompt 必须是 **system 级别的指令**。
- 明确说明该智能体的角色、专业能力以及期望行为。
- 不得在 prompt 中包含执行结果或面向用户的最终答案。

4. 工具（tools）
- 仅在该步骤确实需要时才包含工具。
- 如果不需要任何工具，返回空数组 []。
- 工具名称必须是明确且可执行的。
- 可用工具有[
    "math_tools",
    "file_tools",
    "time_tools",
    "http_tools",
    "string_tools",
    "system_tools",
    "shell_tools",
    "python_tools",
    "image_gen_tools",
]

5. 行动列表（actions）
- actions 必须是一个自然语言指令列表。
- 行动应以祈使句形式编写。
- 每一条行动都应清晰到足以被 ReAct 风格的智能体直接执行。

6. 步骤数量与任务难度（Step Count vs. Task Complexity）
- 你必须根据 **任务的复杂度、不确定性和认知负载** 来动态决定步骤数量。
- 对于 **简单、直接、低依赖的任务**，应使用 **尽量少的步骤**，避免不必要的拆解。
- 对于 **复杂、多阶段、高依赖或需要推理/规划的任务**，应使用 **更多步骤**，以确保每个步骤职责清晰、可控、可执行。
- 不允许为了形式完整而机械地增加步骤；每一个步骤都必须对完成目标具有实际价值。

7. 约束条件
- 不要实际执行任务。
- 不要调用任何工具。
- 不要解释你的推理过程。
- 不要输出 JSON 以外的任何内容。
- 不要包含 Markdown、注释或额外说明文字。

<质量标准>
- 最终步骤应能够直接导向原始目标的完成。
- 步骤数量应与任务难度成正比，既不过少也不过多。
- 输出结构必须是确定性的、可被机器解析的。
"""


class Refine(oxy.ChatAgent):
    """
    任务细化代理（Refine Agent）
    
    将Planning规划阶段得到的初步目标精化为具体的可执行步骤
    
    输入: Target
    输出: List[Step]
    """

    def __init__(self, **kwargs):
        # 定义细化代理的提示词
        kwargs["prompt"] = REFINE_PROMPT
        super().__init__(**kwargs)

    async def refine(self, mas: MAS, target: Target) -> List[Step]:
        """
        将高层目标细化为具体可执行的步骤

        Args:
            mas: 多智能体系统
            target: 需要细化的目标

        Returns:
            List[Step]: 细化后的步骤列表

        Raises:
            ValueError: 当模型输出不是有效JSON或步骤为空时
        """
        # 调用细化代理获取步骤
        result = await mas.call(
            callee=self.name,
            arguments={
                "query": target.query,
                "target": target.target,
                "requirement": target.requirement or "无",
            },
        )

        # 解析模型输出
        try:
            payload = json.loads(util.purify_json(result))
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Refine agent output is not valid JSON: {result}"
            ) from e

        raw_steps = payload.get("steps", [])
        if not raw_steps:
            raise ValueError("Refine agent returned empty steps")

        # 处理结果，转换为Step对象
        steps: List[Step] = []
        for idx, raw in enumerate(raw_steps):
            callee = raw.get("callee")
            prompt = raw.get("prompt")
            tools = raw.get("tools", [])
            actions = raw.get("actions", [])

            if not callee or not prompt or not actions:
                raise ValueError(
                    f"Invalid step definition at index {idx}: {raw}"
                )

            step = Step(
                callee=callee,
                prompts=prompt,
                tools=tools,
                actions=actions,
            )
            steps.append(step)

        return steps
