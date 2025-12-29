from typing import List, Dict

from oxygent import OxyRequest, MAS, oxy

from act.act import Act
from entity.step import Step
from entity.target import Target
from entity.task import Task
from entity.cst import *
from planning.planning import Planning
from refine.refine import Refine

DEFAULT_MODEL = "qwen3-vl"


class Processor:
    """
    通用任务处理器，用于对输入 Task 执行处理逻辑
    """

    def __init__(self, task: Task):
        self.task = task
        self.planning = Planning(
            name=PLANNING_AGENT,
            llm_model=DEFAULT_MODEL,
        )
        self.refine = Refine(
            name=REFINE_AGENT,
            llm_model=DEFAULT_MODEL,
        )
        self.oxy_space = [
            self.planning,
            self.refine,
        ]

    async def process(self) -> Task:
        """
        对单个 Task 执行完整 MAS 工作流
        """
        result = Task(
            task_id=self.task.task_id,
            query=self.task.query,
            level=self.task.level,
            file_name=self.task.file_name,
        )
        # 执行 workflow
        result.answer = await self.run()
        return result

    async def run(self) -> str:
        """
        单 Task 的完整工作流
        """
        async with MAS(oxy_space=self.oxy_space) as mas:
            # Planning 得到target
            targets = await self.planning.plan(mas, self.task)

            # Refine 得到Step
            steps = []
            results = []
            for target in targets:
                step = await self.refine.refine(mas, target)
                steps.extend(step)
                for s in step:
                    # 注册执行者 Act
                    act = Act(step=s)
                    mas.add_oxy(act)
                    results.append(await act.act(mas, s))
            # 感觉这里可以尝试使用下提供的web界面
            mas.start_web_service(first_query=self.task.query)
            return await self.summarize(self.task, targets, steps, results)

    # TODO
    async def summarize(self, task: Task, targets: List[Target], steps: List[Step], results: List[Dict]) -> str:
        """
        对结果进行总结
        """
        return "answer"
