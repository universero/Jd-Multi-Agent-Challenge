from dataclasses import dataclass
from typing import Optional


@dataclass
class Target:
    """
    表示一个执行目标的数据类
    
    Attributes:
        query (str): 原始提问内容
        target (str): 基本目标内容
        requirement (Optional[str]): 特殊要求，默认为 None
        sequence (Optional[int]): 执行序号，默认为 None
    """
    query: str
    target: str
    requirement: Optional[str] = None
    sequence: Optional[int] = None
