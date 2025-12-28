import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Union


@dataclass
class Step:
    """
    一个执行目标
    """
    type: str  # 类型
    action: str | None  # 行为
    tools: List[str] | None  # 工具
