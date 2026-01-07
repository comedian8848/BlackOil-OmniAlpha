# OmniAlpha: 全场景智能量化研究与交易引擎

**OmniAlpha** 是一个专为 A 股市场设计的模块化量化交易平台。它不仅集成了实时行情获取、历史回测和模拟盘执行，更核心的突破在于其**双循环架构**：内置基于遗传算法与强化学习的 **AlphaGen 因子挖掘工厂**，并预留了 **LLM（大语言模型）** 接口，用于语义情感分析与策略自动化生成。

## 🌟 核心特性

* **🛠️ 模块化架构 (Modular Arch)**: 采用依赖倒置设计，支持 Data Provider、Strategy、Model、Trader 各层级自由热插拔。
* **🧬 AlphaGen 因子工厂**: 支持通过遗传编程 (Genetic Programming) 自动挖掘高 IC 因子，告别手动编写公式的低效。
* **🤖 智算引擎 (Intelli-Engine)**: 预留大模型接口，支持接入 GPT-4、Claude 或国产大模型进行研报解析、新闻情绪分析及策略代码优化。
* **实时模拟盘**: 毫秒级事件驱动引擎，支持对接实时数据流进行模拟撮合。
* **📊 交互式可视化**: 基于 Streamlit 打造的研究仪表盘，支持因子分布、回测曲线、持仓分析的实时动态展示。

---

## 📂 项目结构 (Project Structure)

目前项目已完成核心选股引擎的模块化重构，代码结构更加清晰，便于扩展：

```text
BlackOil-OmniAlpha/
├── main.py                 # 🚀 统一入口：负责参数解析与任务调度
├── core/                   # 🧠 核心逻辑层
│   ├── data_provider.py    # 数据适配器 (目前集成 Baostock)
│   └── engine.py           # 策略执行引擎
├── strategies/             # 📈 策略仓库
│   ├── __init__.py         # 策略注册中心 (在此注册新策略)
│   ├── base.py             # 策略基类接口 (StockStrategy)
│   ├── technical.py        # 技术面策略 (均线 MA, 量价 Vol, 换手率 Turn)
│   └── fundamental.py      # 基本面策略 (低估值 PE)
└── utils/                  # 🛠️ 工具集
    ├── file_io.py          # CSV 文件读写
    └── date_utils.py       # 日期处理
```

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备

```bash
pip install baostock pandas
```

### 2. 运行选股引擎

**CLI 模式支持多种灵活用法：**

*   **⚡️ 快速测试 (Quick Mode)**
    *   仅扫描沪深300前20只股票，用于测试策略逻辑。
    ```bash
    python main.py --quick --strategies ma,pe
    ```

*   **🎯 组合策略选股**
    *   同时满足“均线趋势(ma)”和“低估值(pe)”的股票（取交集）。
    ```bash
    python main.py --strategies ma,pe
    ```
    *   **可用策略代码**:
        *   `ma`: 均线多头 (Close > MA20 & MA5 > MA20)
        *   `vol`: 放量上涨 (量比 > 1.5 & 涨幅 > 2%)
        *   `turn`: 资金活跃 (换手率 > 5% & 非ST)
        *   `pe`: 价值洼地 (0 < PE_TTM < 30)

*   **🔗 管道模式 (Pipeline Mode)**
    *   导入已有的 CSV 股票池文件，进行进一步筛选（例如从技术面选出的股票中再筛低估值）。
    ```bash
    # 假设你已经有一个 selection_xxxx.csv 文件
    python main.py --file selection_2026-01-07_ma.csv --strategies pe
    ```

---

## 📊 数据源说明

目前项目默认使用 **Baostock** 作为基础数据源：
*   **免费开源**: 无需注册 API Key，开箱即用。
*   **数据覆盖**: 支持日线、周月线、分钟线。
*   **丰富指标**: 包含基础财务指标 (`peTTM`, `pbMRQ`) 和交易状态 (`turn`, `isST`)。

---

## 📅 项目规划 (Roadmap)

* [x] **Phase 1**: 核心选股引擎重构，实现模块化设计 (Core/Strategies/Utils)。
* [x] **Phase 2**: 集成 Baostock 数据源，实现技术面与基本面（估值）策略。
* [ ] **Phase 3**: 接入 Backtrader 回测框架，验证选股结果。
* [ ] **Phase 4**: 因子挖掘工厂 (AlphaGen) 模块上线。
* [ ] **Phase 5**: 接入 LLM 接口，实现基于新闻情绪的因子加权。

---

## 🤝 团队协作指南

1. **Feature Branching**: 所有新功能请在 `feature/` 分支开发。
2. **Code Review**: 合并至 `main` 需经过至少一名队友的 Review。
3. **Factor Submission**: 挖掘出的新因子需提交至 `factor_library/` 并附带 IC 分析报告。

---