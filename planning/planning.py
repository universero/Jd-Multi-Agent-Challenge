import json
from typing import List

from oxygent import oxy, MAS

from entity.target import Target
from entity.task import Task

PLANNING_PROMPT = """你是一个任务规划专家，请根据以下任务信息，将任务分解为具体的执行目标，并为每个目标指定执行顺序。

任务信息：
- 问题描述：{query}
- 任务级别：{level}
- 关联文件：{file_name}

请按照以下要求生成执行目标：
1. 将任务分解为2-4个具体的执行目标，每个目标应该是一个明确的、可执行的步骤
2. 为每个目标分配一个唯一的执行顺序号（1-3，相同数字表示可以并行执行）
3. 每个目标应该包含：
   - target：目标的具体描述
   - requirement：完成该目标的特殊要求（可选）
   - sequence：执行顺序号（1-3）

请以JSON数组格式输出，示例：
[{{
        "target": "分析问题的约束条件和逻辑关系",
        "requirement": "需要考虑时间限制和资源约束",
        "sequence": 1
    }},
    {{
        "target": "设计实验方案",
        "requirement": "确保在规定时间内完成",
        "sequence": 1
    }},
    {{
        "target": "计算需要的资源数量",
        "requirement": "使用数学模型进行计算",
        "sequence": 2
    }},
    {{
        "target": "验证方案的可行性",
        "requirement": "检查是否满足所有约束条件",
        "sequence": 3
    }}
]"""


class Planning(oxy.ChatAgent):
    def __init__(self, **kwargs):
        kwargs["prompt"] = PLANNING_PROMPT
        super().__init__(**kwargs)

    async def plan(self, mas: MAS, task: Task) -> List[Target]:
        # 格式化提示词
        formatted_prompt = PLANNING_PROMPT.format(
            query=task.query,
            level=task.level,
            file_name=task.file_name or "无"
        )
        
        result = await mas.call(
            callee=self.name,
            arguments={"prompt": formatted_prompt},
        )
        
        # 解析返回结果
        try:
            targets_data = json.loads(result.output)
            targets = []
            for target_data in targets_data:
                targets.append(Target(
                    target=target_data.get("target", ""),
                    requirement=target_data.get("requirement", None),
                    sequence=target_data.get("sequence", None),
                ))
            return targets
        except Exception as e:
            # 如果解析失败，返回默认目标
            return [Target(
                target="完成任务",
                requirement="根据任务描述完成",
                sequence=1,
            )]
