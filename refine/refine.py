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

REFINE_PROMPT = """提示词"""


class Refine(oxy.ChatAgent):
    def __init__(self, **kwargs):
        kwargs["prompt"] = REFINE_PROMPT
        super().__init__(**kwargs)

    async def refine(self, mas: MAS, target: Target) -> List[Step]:
        result = await mas.call(
            callee=self.name,
            arguments={"query": target.target},
        )
        # 处理result
        return [Step(
            callee=self.name,
            prompts=result.output,
            tools=[],
            actions=[],
        )]
