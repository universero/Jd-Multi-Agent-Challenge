import json
from typing import List

from oxygent import oxy, MAS

from entity.target import Target
from entity.task import Task
from util import util

PLANNING_PROMPT = """
你是一个**任务规划专家（Planning Agent）**。
你的职责是：  
根据用户提供的任务信息，对 **用户的 query 进行规划级拆解**，将其拆分为少量**可执行的中间目标（Target）**，并明确这些目标之间的**执行顺序与并行关系**。  
该过程属于 **planning 阶段**，不需要执行任务本身，只负责目标拆分与结构化规划。
目标应该尽可能具体并贴合问题, 不要提出形式上没有意义的目标, 需要切实的指导任务
<任务输入>
你将接收到以下信息：
- 问题描述（query）：${query}  
- 任务级别（level）：${level}（用于判断任务复杂度, 越高越复杂）  
- 关联文件（file_name）：${file_name}（如与任务相关，需在目标或要求中体现）
<规划目标生成要求>
1. 目标拆分数量（由任务难度动态决定, 但最多不超过四个）
- **执行目标的数量没有固定上限或下限**，必须根据任务的复杂度、不确定性和依赖关系自行决定。  
- 简单、直接、低依赖的任务，应拆分为**较少的执行目标**。对于部分问题可以直接一个目标
- 复杂、多阶段、高依赖或需要分析/推理/设计的任务，应拆分为**多个更清晰的执行目标**。  
- **不允许为了形式完整而强行拆分目标**；**每一个目标都必须对完成整体任务具有实际价值**。
2. 执行顺序（sequence）
- 为每个目标分配一个 **sequence 执行顺序号** 
- sequence 仅用于表达 **先后依赖关系与并行关系**：  
  - 相同 sequence 表示可以并行执行  
  - 不同 sequence 表示存在先后依赖  
- sequence 的设计必须来源于真实的任务依赖，而不是人为分段或凑数。

3. 目标结构要求
每个执行目标必须包含以下字段：
- target  
  - 对该执行目标的具体描述, 不要宽泛抽象的描述, 需要直接说明目标
  - 必须清晰说明“要做什么”，避免抽象或泛化表述  
- requirement（可选）  
  - 当目标存在额外约束、特殊条件、质量要求、依赖文件或上下文时，必须补充该字段  
  - 若无特殊要求，可以省略该字段  
- sequence  
  - 表示该目标在整体规划中的执行阶段  
4. requirement 使用规则
- 仅在确实存在约束或特殊要求时才添加 requirement，例如：  
  - 依赖特定文件（如 file_name）  
  - 有性能、时间、格式、精度等要求  
  - 需要遵循特定方法、规范或工具  
- 不要为所有目标机械性添加 requirement。
<输出要求>
- 仅输出 **JSON 数组**  
- 不要包含任何解释性文字  
- 不要使用 Markdown  

<输出示例>
level1示例: 100桶水中混有1桶剧毒（饮用后24小时发作无解药），用实验兔检测（每兔可饮多桶，每桶可被多兔饮用），目标：在48小时内用最少的兔子找出毒桶，约束：无法区分中毒先后，且第二次实验需等待24小时，问最少需要几只兔子？
[
  {
    "target": "思考题, 使用2进制思想, 根据要求思考并得出答案",
    "requirement": "仅输出数字"
    "sequence": 1
  }
]
level1示例: 你雇人工作7天，手上仅有一根金条并且需每日支付1/7根金条作为报酬。问最少将金条切成多少段，使得每天能支付当日工资？仅输出数字
[
  {
    "target": "思考题, 根据题目要求思考并得出答案",
    "requirement": "仅输出数字"
    "sequence": 1
  }
]

level2示例: 在github的Huggingface transformers仓库中，2025年8月8日有一位用户反馈了关于输入音频样本和耳语反馈的问题，labels为Audio、Whisper、bug，请输出这位用户附加的网站链接。
[
  {
    "target": "找到Github Huggingface Transformer仓库的issue页的地址",
    "sequence": 1
  },
    {
    "target": "在仓库的issue页中, 根据labels: labels为Audio、Whisper、bug, 查找2025年8月8日的关于音频样本和耳语反馈的问题",
    "sequence": 2
  },
]

level3示例: 截至2024年，有一位人物2014年在南京打破某一项世界青年记录。她后续荣获'感动中国年度人物', 在该获奖视频1分31s处，显示有几个星星？回答数值即可。
[
  {
    "target": "找到2014年在南京打破世界青年记录并或的感动中国的人物",
    "sequence": 1
  },
  {
    "target": "找到这个人物在感动中国颁奖的官方视频",
    "requirement": "cctv的官方视频"
    "sequence": 2
  },  
  {
    "target": "获取1分31s的画面获得星星数量",
    "sequence": 3
  },
]
"""


class Planning(oxy.ChatAgent):
    """
    任务规划代理类，用于将用户任务分解为可执行的中间目标
    """
    def __init__(self, **kwargs):
        """
        初始化规划代理
        """
        kwargs["prompt"] = PLANNING_PROMPT
        super().__init__(**kwargs)

    async def plan(self, mas: MAS, task: Task) -> List[Target]:
        """
        根据任务信息进行规划，将其分解为多个可执行的目标
        
        Args:
            mas: 多代理系统实例
            task: 需要规划的任务
            
        Returns:
            List[Target]: 分解后的目标列表
            
        Raises:
            Exception: 当解析规划结果失败时抛出异常
        """
        # 调用MAS系统进行任务规划
        result = await mas.call(
            callee=self.name,
            arguments={
                "query": task.query,
                "level": task.level,
                "file_name": task.file_name or "无",
            },
        )

        # 解析并构建目标列表
        try:
            # 清理并解析JSON结果
            targets_data = json.loads(util.purify_json(result))
            targets = []
            for target_data in targets_data:
                target = Target(
                    query=task.query,
                    target=target_data.get("target", ""),
                    requirement=target_data.get("requirement", None),
                    sequence=target_data.get("sequence", None),
                )
                targets.append(target)
            return targets
        except Exception as e:
            # 重新抛出异常，保留原始错误信息
            raise e
