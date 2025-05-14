# quantTrade-aiAgent

使用 Python 和 AI 驱动的量化交易个人投资系统。

## 项目简介

quantTrade-aiAgent 是一个旨在帮助个人投资者进行自动化交易决策和执行的量化交易系统。该项目利用 Python 生态系统进行数据获取、分析、策略回测和可视化。

## 核心功能

- **市场数据获取**: 从 Yahoo Finance 等来源获取股票历史和实时数据。
- **技术指标计算**: 计算常用的技术指标，如移动平均线 (MA), 指数移动平均线 (EMA), 相对强弱指数 (RSI), MACD, 布林带等。
- **交易策略开发**: 实现和测试不同的交易策略。
- **策略回测**: 对交易策略进行历史数据回测，评估策略表现。
- **结果可视化**: 通过图表展示价格、指标、交易信号和策略收益。

## 项目结构

```
quantTrade-aiAgent/
├── src/
│   ├── __init__.py             # 使 src 成为一个包
│   ├── data/
│   │   └── market_data.py     # 市场数据获取模块
│   ├── strategies/
│   │   └── ma_cross_strategy.py # 移动平均线交叉策略实现
│   ├── backtest/                # 回测相关模块 (待实现)
│   ├── visualization/           # 可视化相关模块 (待实现)
│   ├── utils/
│   │   └── technical_indicators.py # 技术指标计算工具
│   └── run_strategy.py          # 策略运行和可视化示例脚本
├── tests/                     # 单元测试和集成测试
├── docs/                      # 项目文档
├── requirements.txt           # Python 依赖列表
├── setup.py                   # 项目打包配置
├── README.md                  # 项目说明文件
└── .gitignore                 # Git 忽略文件配置
```

## 安装指南

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/yourusername/quantTrade-aiAgent.git
    cd quantTrade-aiAgent
    ```

2.  **创建虚拟环境** (推荐):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate    # Windows
    ```

3.  **安装 TA-Lib C 库**:
    - **macOS**: `brew install ta-lib`
    - **Linux (Ubuntu/Debian)**: `wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib/ && ./configure --prefix=/usr && make && sudo make install && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz`
    - **Windows**: 下载 [ta-lib-0.4.0-msvc.zip](https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-msvc.zip/download) 并按照说明安装。

4.  **安装 Python 依赖**: 
    ```bash
    pip install -r requirements.txt
    ```
    或者在开发模式下安装:
    ```bash
    pip install -e .
    ```

## 快速开始

运行示例策略 (移动平均线交叉):

```bash
python src/run_strategy.py
```

该脚本将：
1. 从 Yahoo Finance 获取苹果公司 (AAPL) 的历史数据。
2. 计算短期 (20天) 和长期 (50天) 移动平均线。
3. 基于移动平均线的交叉生成买入/卖出信号。
4. 对策略进行回测并打印性能指标 (总收益率, 年化收益率, 最大回撤)。
5. 使用 Matplotlib 绘制价格、移动平均线、交易信号和资产曲线图。

*(注意: `run_strategy.py` 中的股票代码和时间范围可以修改)*

## 开发与贡献

(待补充：可以添加代码风格、测试要求、分支策略、提交流程等贡献指南)

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 致谢

(待补充：可以感谢使用的库、数据源或提供帮助的人)
