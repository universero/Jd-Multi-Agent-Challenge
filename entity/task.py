import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Union

from entity.step import Step
from entity.target import Target

# 任务难度等级常量
LEVEL_BASIC = "1"  # 基础任务
LEVEL_ADVANCED = "2"  # 进阶任务
LEVEL_COMPLEX = "3"  # 复杂任务


@dataclass
class Task:
    """
    表示一个任务数据条目的结构化对象。
    
    Attributes:
        task_id: 任务唯一标识符
        query: 待解决的问题描述
        level: 任务难度等级
        file_name: 关联文件名（可选）
        answer: 验证集答案（非所有任务都有）
        steps: 预估完成步骤（验证集专用）
        targets: 目标列表（可选）
        refine_steps: 优化步骤列表（可选）
    """
    task_id: str
    query: str
    level: Union[str, int]
    file_name: Optional[str] = None
    answer: Optional[str] = None
    steps: Optional[str] = None
    targets: Optional[List[Target]] = None
    refine_steps: Optional[List[Step]] = None
    act_results: Optional[List[dict]] = None
    final_answer: Optional[str] = None
    success: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        从字典创建 Task 对象
        
        Args:
            data: 包含任务信息的字典
            
        Returns:
            Task: 创建的 Task 对象
        """
        task = cls(
            task_id=data.get("task_id", ""),
            query=data.get("query", ""),
            level=data.get("level", ""),
            file_name=data.get("file_name"),
            answer=data.get("answer"),
            steps=data.get("steps"),
        )
        return task

    def to_dict(self) -> dict:
        """
        将 Task 对象转换为字典形式
        
        Returns:
            dict: 包含任务信息的字典
        """
        return asdict(self)

    @staticmethod
    def load_from_file(path: str) -> List["Task"]:
        """
        从 JSONL 文件加载任务列表。
        每行一个合法的 JSON 对象，对应一个 Task。
        
        Args:
            path: JSONL 文件路径
            
        Returns:
            List[Task]: 任务列表
            
        Raises:
            ValueError: 当文件格式不正确时抛出异常
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
                except Exception as e:
                    raise ValueError(f"第 {line_num} 行数据处理失败: {e}")
        return tasks

    @staticmethod
    def save_to_file(tasks: List["Task"], path: str):
        """
        将任务列表保存为 JSONL 文件（每行一个任务对象）
        
        Args:
            tasks: 任务列表
            path: 输出文件路径
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
        
        Args:
            tasks: 任务列表
            path: 输出文件路径
            
        Raises:
            ValueError: 当任务缺少必要字段时抛出异常
        """
        with open(path, "w", encoding="utf-8") as f:
            for t in tasks:
                if not t.task_id:
                    raise ValueError("任务缺少 task_id，无法生成提交文件。")
                if t.answer is None:
                    raise ValueError(f"任务 {t.task_id} 缺少 answer 字段。")

                line = {"task_id": t.task_id, "answer": t.answer}
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    def __repr__(self):
        """
        返回 Task 对象的字符串表示
        
        Returns:
            str: Task 对象的字符串表示
        """
        return (
            f"Task(task_id={self.task_id!r}, level={self.level!r}, "
            f"query={self.query[:20]!r}..., answer={self.answer!r})"
        )
