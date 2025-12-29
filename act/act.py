from typing import Dict

from oxygent import oxy, MAS

from entity.step import Step


class Act(oxy.ChatAgent):
    def __init__(self, step: Step, **kwargs):
        kwargs["name"] = step.callee
        kwargs["prompt"] = step.prompts
        kwargs["tool"] = step.tools
        super().__init__(**kwargs)

    # TODO
    async def act(self, mas: MAS, step: Step) -> Dict:
        return {}
