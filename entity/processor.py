from entity.task import Task


class Processor:
    """
    通用任务处理器，用于对输入 Task 执行处理逻辑
    """

    def __init__(self):
        # 可以在此处加载模型、工具或配置
        pass

    @classmethod
    def process(cls, task: Task) -> Task:
        """
        处理任务，返回一个带有结果的 Task 实例
        """
        # 复制输入任务
        result = Task(
            task_id=task.task_id,
            query=task.query,
            level=task.level,
            file_name=task.file_name,
        )

        result.answer = f"处理完成：{task.query}"
        return result
