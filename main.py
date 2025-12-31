import asyncio
import os

from entity.config import Config
from entity.processor import Processor
from entity.task import Task

Mode = "valid"  # valid, 验证模式 | test, 测试模式


# 处理任务
async def process_tasks():
    results = []
    try:
        for task in tasks[:1]:
            result = await Processor(task).process()
            results.append(result)
    except Exception as e:
        print(f"处理任务时发生错误: {e}")
        return []
    return results


if __name__ == "__main__":
    # 设置实验名称, 实验产生的中间产物会以这个为前缀以供后续脱敏
    Config.set_app_name("exp_1_v1")
    Config.set("LLM_API_KEY", "sk-b1423fb8e0af4be0be479e90e46471c1")
    Config.set("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    # Config.set("LLM_MODEL_NAME", "qwen3-max")
    Config.set("LLM_MODEL_NAME", "deepseek-v3.2")
    # 读取任务
    tasks = Task.load_from_file(f"./data/{Mode}/data.jsonl")
    # 处理
    answers = asyncio.run(process_tasks())
    # 保存完全结果
    Task.save_to_file(answers, f"./experiment/{Config.get_app_name()}/step.jsonl")
