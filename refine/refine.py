import json
from typing import List

from oxygent import oxy, MAS
from entity.target import Target
from entity.step import Step
from entity.cst import *

"""
输入: Target
输出: List[Step]
将Planning规划阶段得到的初步目标精化为具体的可执行步骤
"""

REFINE_PROMPT = """
You are a Refine Agent in a multi-agent execution system.

Your task:
Given a high-level execution Target, decompose it into a list of concrete, executable Steps.
Each Step MUST be directly executable by a single specialized agent.

<INPUT>
You will receive:
- target: the high-level goal to be achieved
- requirement (optional): additional constraints or special requirements

<OUTPUT REQUIREMENTS>
You MUST output a single JSON object and NOTHING ELSE.
The JSON format MUST strictly follow this schema:
{
  "steps": [
    {
      "callee": "<agent_name>",
      "prompt": "<system prompt for this agent>",
      "tools": ["<tool_name_1>", "<tool_name_2>"],
      "actions": [
        "<action step 1>",
        "<action step 2>",
        "<action step 3>"
      ]
    }
  ]
}

<DETAILED RULES>
1. Step Decomposition
- Decompose the target into multiple steps if necessary.
- Each step should be logically independent and sequentially executable.
- Avoid overly fine-grained steps; each step should represent a meaningful task.

2. Agent Selection (callee)
- Assign a clear and descriptive agent name for each step.
- Different steps MAY use different agents if their responsibilities differ.
- Agent names should reflect their role (e.g., "search_agent", "analysis_agent", "writing_agent").

3. Agent Prompt (prompt)
- The prompt MUST be a system-level instruction for the agent.
- Clearly define the agent’s role, expertise, and expected behavior.
- Do NOT include execution results or user-facing answers in the prompt.

4. Tools
- Only include tools that are necessary for the step.
- If no tools are needed, return an empty list [].
- Tool names must be explicit and executable.

5. Actions
- Actions MUST be a list of natural-language instructions.
- Actions should be written as imperative steps.
- Each action should be clear enough to be directly executed by a ReAct-style agent.

6. Constraints
- Do NOT execute the task.
- Do NOT call tools.
- Do NOT explain your reasoning.
- Do NOT output anything outside the JSON object.
- Do NOT include markdown, comments, or additional text.


<QUALITY CRITERIA>
- The final step should lead directly to fulfilling the original target.
- The steps should be minimal but sufficient.
- The structure must be deterministic and machine-parseable.
If the target cannot be refined due to missing information, generate a single step whose action is to ask for clarification.
"""


class Refine(oxy.ChatAgent):
    def __init__(self, **kwargs):
        kwargs["prompt"] = REFINE_PROMPT
        super().__init__(**kwargs)

    async def refine(self, mas: MAS, target: Target) -> List[Step]:
        result = await mas.call(
            callee=self.name,
            arguments={
                "target": target.target,
                "requirement": target.requirement,
            },
        )
        # 解析模型输出
        try:
            payload = json.loads(result.output)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Refine agent output is not valid JSON: {result.output}"
            ) from e
        raw_steps = payload.get("steps", [])
        if not raw_steps:
            raise ValueError("Refine agent returned empty steps")

        # 处理result
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
            steps.append(
                Step(
                    callee=callee,
                    prompts=prompt,
                    tools=tools,
                    actions=actions,
                )
            )

        return steps
