import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Union

LEVEL_BASIC = "1"  # 基础任务
LEVEL_ADVANCED = "2"  # 进阶任务
LEVEL_COMPLEX = "3"  # 复杂任务


@dataclass
class Task:
    """
    表示一个任务数据条目的结构化对象。
    """
    task_id: str  # 任务唯一标识符
    query: str  # 待解决的问题描述
    level: Union[str, int]  # 任务难度等级
    file_name: Optional[str] = None  # 可选，关联文件名
    answer: Optional[str] = None  # 验证集答案（非所有任务都有）
    steps: Optional[str] = None  # 预估完成步骤（验证集专用）

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典创建 TaskItem 对象"""
        return cls(
            task_id=data.get("task_id", ""),
            query=data.get("query", ""),
            level=data.get("level", ""),
            file_name=data.get("file_name"),
            answer=data.get("answer"),
            steps=data.get("steps"),
        )

    def to_dict(self) -> dict:
        """转换为字典形式"""
        return asdict(self)

    @staticmethod
    def load_from_file(path: str) -> List["Task"]:
        """
        从 JSON 文件加载任务列表
        支持文件内容为:
        1. [ {...}, {...} ] 任务列表
        2. {...} 单个任务
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return [Task.from_dict(item) for item in data]
        elif isinstance(data, dict):
            return [Task.from_dict(data)]
        else:
            raise ValueError("JSON 文件格式错误，必须是对象或数组。")

    @staticmethod
    def save_to_file(tasks: List["Task"], path: str, indent: int = 2):
        """将任务列表保存为 JSON 文件"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=indent)

    @staticmethod
    def gen_submit(tasks: List["Task"], path: str, indent: int = 2):
        """
        生成提交文件，只保留 task_id 和 answer 字段。
        输出格式:
        [
          {"task_id": "...", "answer": "..."},
          {"task_id": "...", "answer": "..."}
        ]
        """
        submit_data = []
        for t in tasks:
            if not t.task_id:
                raise ValueError("任务缺少 task_id，无法生成提交文件。")
            if t.answer is None:
                raise ValueError(f"任务 {t.task_id} 缺少 answer 字段。")
            submit_data.append({"task_id": t.task_id, "answer": t.answer})

        with open(path, "w", encoding="utf-8") as f:
            json.dump(submit_data, f, ensure_ascii=False, indent=indent)

    def __repr__(self):
        return (
            f"TaskItem(task_id={self.task_id!r}, level={self.level!r}, "
            f"query={self.query[:20]!r}..., answer={self.answer!r})"
        )
