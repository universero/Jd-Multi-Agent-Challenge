import asyncio
import os

from entity.config import Config
from entity.processor import Processor
from entity.task import Task

# 运行模式：valid（验证模式）或 test（测试模式）
MODE = "valid"


async def process_tasks(tasks):
    """
    处理任务列表
    
    Args:
        tasks: 任务列表
        
    Returns:
        list: 处理结果列表
    """
    results = []
    try:
        for task in tasks:
            result = await Processor(task).process()
            results.append(result)
    except Exception as e:
        print(f"处理任务时发生错误: {e}")
        return []

    return results


def main():
    """主函数：初始化配置、加载任务、处理任务并保存结果"""
    # 设置实验名称，实验产生的中间产物会以这个为前缀以供后续脱敏
    Config.set_app_name("exp_1_v1")
    Config.set("LLM_API_KEY", os.getenv("DEFAULT_LLM_API_KEY"))
    Config.set("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    Config.set("LLM_MODEL_NAME", "qwen3-max")

    # 加载任务
    tasks = Task.load_from_file(f"./data/{MODE}/data.jsonl")

    # 处理任务
    answers = asyncio.run(process_tasks(tasks))

    # 保存完整结果
    Task.save_to_file(answers, f"./experiment/{Config.get_app_name()}/step.jsonl")


if __name__ == "__main__":
    main()
