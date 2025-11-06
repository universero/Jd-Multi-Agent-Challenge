from entity.config import Config
from entity.task import Task

if __name__ == "__main__":
    # 设置实验名称
    Config.set_app_name("exp_1_v1")
    # 读取任务
    tasks = Task.load_from_file("")
