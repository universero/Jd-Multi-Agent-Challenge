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
        从 JSONL 文件加载任务列表。
        每行一个合法的 JSON 对象，对应一个 Task。
        """
        tasks = []
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue  # 跳过空行
                try:
                    data = json.loads(line)
                    tasks.append(Task.from_dict(data))
                except json.JSONDecodeError as e:
                    raise ValueError(f"第 {line_num} 行 JSON 解析失败: {e}")
        return tasks

    @staticmethod
    def save_to_file(tasks: List["Task"], path: str):
        """
        将任务列表保存为 JSONL 文件（每行一个任务对象）
        """
        with open(path, "w", encoding="utf-8") as f:
            for t in tasks:
                f.write(json.dumps(t.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def gen_submit(tasks: List["Task"], path: str):
        """
        生成提交文件（JSONL格式），只保留 task_id 和 answer 字段。
        每行一个结果：
        {"task_id": "...", "answer": "..."}
        """
        with open(path, "w", encoding="utf-8") as f:
            for t in tasks:
                if not getattr(t, "task_id", None):
                    raise ValueError("任务缺少 task_id，无法生成提交文件。")
                if getattr(t, "answer", None) is None:
                    raise ValueError(f"任务 {t.task_id} 缺少 answer 字段。")

                line = {"task_id": t.task_id, "answer": t.answer}
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def __repr__(self):
        return (
            f"TaskItem(task_id={self.task_id!r}, level={self.level!r}, "
            f"query={self.query[:20]!r}..., answer={self.answer!r})"
        )
