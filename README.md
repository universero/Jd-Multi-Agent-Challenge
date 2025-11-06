# Jd Multi-Agent Challenge

探索多智能体在复杂业务场景下的协同决策能力。
赛题要求参赛者基于京东零售开源的多智能体（**Multi-Agent**）协作框架 **OxyGent**，构建高效协作的多智能体系统，以应对现实环境中的不确定性和多目标优化问题。

---

## 📂 目录结构

```bash
Jd-Multi-Agent-Challenge/
├── data/                          # 数据目录
│   ├── test/                      # 测试数据集
│   ├── valid/                     # 验证数据集
│   ├── desensitize_data/          # 数据脱敏脚本
│   └── submit_example.jsonl       # 提交示例文件
│
├── src/                           # 主程序与智能体实现
│   ├── agents/                    # 智能体定义与逻辑
│   ├── envs/                      # 环境定义与交互接口
│   ├── strategies/                # 策略与调度逻辑
│   └── utils/                     # 工具与通用模块
│
├── configs/                       # 配置文件目录（模型参数、超参等）
│   └── default.yaml
│
├── experiments/                   # 实验脚本与结果保存
│   ├── logs/
│   └── checkpoints/
│
├── pyproject.toml                 # uv 配置文件，管理虚拟环境与依赖
├── README.md                      # 项目说明文档
└── LICENSE                        # 许可证
```

---

## ⚙️ 环境管理

本项目基于 **[uv](https://github.com/astral-sh/uv)** 管理 Python 虚拟环境与依赖。
克隆项目后，可按以下步骤配置开发环境：

### 1️⃣ 克隆项目

```bash
git clone https://github.com/yourusername/Jd-Multi-Agent-Challenge.git
cd Jd-Multi-Agent-Challenge
```

### 2️⃣ 安装 uv（若未安装）

```bash
pip install uv
```

或使用官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3️⃣ 创建并激活环境

```bash
uv venv
source .venv/bin/activate  # Windows 下使用 .venv\Scripts\activate
```

### 4️⃣ 安装依赖

使用 `pyproject.toml` 中的声明：

```bash
uv sync
```

### 5️⃣ 验证安装

```bash
python -m src.main --help
```

### 6️⃣ 添加依赖

若需要为项目添加新的第三方库，可使用 uv add 命令。
该命令会自动安装依赖并更新 pyproject.toml 与 uv.lock 文件，无需手动编辑。

✅ 示例：添加单个依赖
```bash
uv add numpy
```

✅ 指定版本号
```bash
uv add fastapi==0.115.0
```

安装后，uv 会自动更新环境与锁文件，确保团队成员或部署环境可复现依赖状态。

---

是否希望我接着帮你加上「运行与提交说明」部分（比如如何运行 agent、生成结果并提交 JSONL）？这样你的 README 就能完整覆盖参赛准备流程。
