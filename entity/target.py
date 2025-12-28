import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Union


@dataclass
class Target:
    """
    一个执行目标
    """
    target: str  # 基本目标
    requirement: str | None  # 特殊要求
    sequence: int | None  # 执行序号
