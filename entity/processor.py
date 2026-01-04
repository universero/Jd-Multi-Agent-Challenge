from typing import List, Dict

from oxygent import MAS, oxy, preset_tools

from act.act import Act
from entity.config import Config
from entity.step import Step
from entity.target import Target
from entity.task import Task
from entity.cst import *
from planning.planning import Planning
from refine.refine import Refine
from summary.summary import Summary


class Processor:
    """
    通用任务处理器，用于执行输入的 Task
    该类实现了一个完整的多智能体系统工作流，包括规划、细化和执行阶段
    """

    def __init__(self, task: Task):
        """
        初始化处理器
        
        Args:
            task: 需要处理的任务对象
        """
        self.task = task
        # 初始化各个处理组件
        self.planning = Planning(name=PLANNING_AGENT)
        self.refine = Refine(name=REFINE_AGENT)
        self.act = Act(name=ACT_AGENT)
        self.summary = Summary(name=SUMMARY_AGENT)

        # 配置多智能体系统的工作空间
        self.oxy_space = [
            oxy.HttpLLM(
                name="default_llm",
                api_key=Config.get("LLM_API_KEY"),
                base_url=Config.get("LLM_BASE_URL"),
                model_name=Config.get("LLM_MODEL_NAME"),
            ),
            preset_tools.math_tools,
            preset_tools.file_tools,
            preset_tools.time_tools,
            preset_tools.http_tools,
            preset_tools.string_tools,
            preset_tools.system_tools,
            preset_tools.shell_tools,
            preset_tools.python_tools,
            preset_tools.image_gen_tools,
            self.planning,
            self.refine,
            self.act,
            self.summary,
        ]

    async def process(self) -> Task:
        """
        执行完整的工作流程
        
        Returns:
            处理完成的任务对象，包含目标、细化步骤和执行结果
        """
        return await self.run()

    async def run(self) -> Task:
        """
        执行单个任务的完整工作流
        工作流包括：规划阶段 -> 细化阶段 -> 执行阶段 -> 总结阶段
        
        Returns:
            包含完整处理结果的任务对象
        """
        async with MAS(oxy_space=self.oxy_space) as mas:
            # 规划阶段：根据任务生成目标列表
            targets = await self.planning.plan(mas, self.task)

            # 细化阶段：将每个目标细化为具体步骤
            steps: List[Step] = []
            results: List[Dict] = []
            for target in targets:
                step = await self.refine.refine(mas, target)
                steps.extend(step)

            # 执行阶段：依次执行所有步骤，并将之前的结果传递给后续步骤
            for step in steps:
                result = await self.act.act(mas, step, results)
                results.append(result)

            return await self.summarize(self.task, mas, targets, steps, results)

    async def summarize(self, task: Task, mas: MAS, targets: List[Target], steps: List[Step],
                        results: List[Dict]) -> Task:
        """
        汇总处理结果并更新任务对象
        
        Args:
            task: 原始任务对象
            targets: 生成的目标列表
            steps: 执行的步骤列表
            results: 步骤执行结果列表
            mas: 执行环境
            
        Returns:
            更新后的任务对象，包含所有处理结果
        """
        task.targets = targets
        task.refine_steps = steps
        task.act_results = results
        success, ans = await self.summary.summary(mas, task)
        if success:
            task.success = True
            task.answer = ans
        else:
            task.query = ans
        return task
