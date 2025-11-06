from entity.config import Config
from entity.processor import Processor
from entity.task import Task

Mode = "valid"  # valid, 验证模式 | test, 测试模式

if __name__ == "__main__":
    # 设置实验名称, 实验产生的中间产物会以这个为前缀以供后续脱敏
    Config.set_app_name("exp_1_v1")
    # 读取任务
    tasks = Task.load_from_file(f"./data/{Mode}")
    # 处理任务
    answers = [Processor.process(task) for task in tasks]
    # 保存完全结果
    Task.save_to_file(answers, f"./experiment/{Config.get_app_name()}/step.jsonl")
    # 生成提交文件
    Task.gen_submit(answers, f"./experiment/{Config.get_app_name()}/submit.jsonl")
