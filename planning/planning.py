from typing import List

from oxygent import oxy, MAS

from entity.target import Target
from entity.task import Task

PLANNING_PROMPT = """提示词"""


class Planning(oxy.ChatAgent):
    def __init__(self, **kwargs):
        kwargs["prompt"] = PLANNING_PROMPT
        super().__init__(**kwargs)

    # TODO
    async def plan(self, mas: MAS, task: Task) -> List[Target]:
        result = await mas.call(
            callee=self.name,
            arguments={},
        )
        return [Target(
            target=result.output,
            requirement=None,
            sequence=None,
        )]
