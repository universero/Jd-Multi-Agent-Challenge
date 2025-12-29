import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Union


@dataclass
class Step:
    """
    执行步骤
    """
    callee: str  # 执行者
    prompts: str  # 提示词
    tools: List[str]  # 工具列表
    actions: List[str]  # 执行步骤
