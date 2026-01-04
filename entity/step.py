from dataclasses import dataclass
from typing import List


@dataclass
class Step:
    """
    执行步骤
    
    Attributes:
        callee: 执行者
        prompts: 提示词
        tools: 工具列表
        actions: 执行步骤
    """
    callee: str  # 执行者
    prompts: str  # 提示词
    tools: List[str]  # 工具列表
    actions: List[str]  # 执行步骤
