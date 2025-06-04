# quantTrade-aiAgent

基于 Python Flask 和 Vue 3 的全栈量化交易系统，支持多引擎策略回测与实时数据可视化。

## 🚀 项目简介

quantTrade-aiAgent 是一个现代化的量化交易平台，专为个人投资者设计。系统提供完整的策略开发、回测分析和结果可视化功能，采用前后端分离架构，支持多种回测引擎，让量化交易变得更加简单和直观。

### ✨ 核心特性

- **🔥 双引擎支持**: 内置默认策略引擎 + 专业 Backtrader 引擎
- **📊 实时数据源**: 基于 AKShare 的 A 股市场数据获取
- **🎯 策略多样化**: 移动平均线交叉、交易量突破等多种策略
- **📈 可视化分析**: ECharts 驱动的交互式图表与技术指标
- **⚡ 实时通信**: WebSocket 实现前后端实时数据交互
- **🧪 全面测试**: 前后端单元测试 + E2E 自动化测试
- **📱 响应式设计**: 支持桌面端和移动端访问

## 🛠️ 技术栈详解

### 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | ^3.4.0 | 渐进式前端框架，采用组合式 API |
| **TypeScript** | ^5.0.0 | 类型安全的 JavaScript 超集 |
| **Vite** | ^5.0.0 | 快速构建工具与开发服务器 |
| **Element Plus** | ^2.8.0 | Vue 3 企业级 UI 组件库 |
| **ECharts** | ^5.5.0 | 百度开源的数据可视化图表库 |
| **Tailwind CSS** | ^3.4.0 | 实用优先的 CSS 框架 |
| **Socket.IO Client** | ^4.7.0 | WebSocket 客户端通信 |
| **Axios** | ^1.6.0 | HTTP 客户端库 |
| **Splitpanes** | ^3.1.0 | 可调整大小的面板组件 |

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **Flask** | ^3.0.0 | 轻量级 Python Web 框架 |
| **Flask-SocketIO** | ^5.3.0 | WebSocket 服务端支持 |
| **Flask-CORS** | ^4.0.0 | 跨域资源共享处理 |
| **Backtrader** | ^1.9.78 | 专业 Python 量化回测框架 |
| **AKShare** | ^1.14.0 | A 股数据获取库 |
| **pandas** | ^2.2.0 | 数据分析与处理 |
| **NumPy** | ^1.26.0 | 数值计算基础库 |
| **matplotlib** | 3.2.2 | 图表绘制（Backtrader 兼容） |

### 开发与测试工具
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vitest** | ^2.1.0 | 前端单元测试框架 |
| **Vue Test Utils** | ^2.4.0 | Vue 组件测试工具 |
| **Cypress** | ^13.0.0 | E2E 自动化测试 |
| **pytest** | ^7.4.0 | Python 单元测试框架 |
| **ESLint** | ^9.0.0 | JavaScript/TypeScript 代码检查 |

## 📁 系统架构

```
quantTrade-aiAgent/
├── 🎨 quant_frontend/               # Vue 3 前端应用
│   ├── src/
│   │   ├── components/             # UI 组件库
│   │   │   ├── StrategyRunner.vue      # 策略执行控制面板
│   │   │   ├── ResultsChart.vue        # 回测结果图表
│   │   │   ├── PerformanceMetrics.vue  # 性能指标展示
│   │   │   ├── StockSelector.vue       # 股票选择器
│   │   │   ├── IndicatorChart.vue      # 技术指标图表
│   │   │   └── DashboardLayout.vue     # 仪表板布局
│   │   ├── services/               # API 服务层
│   │   │   └── api.ts                  # 统一 API 接口
│   │   ├── config/                 # 配置文件
│   │   │   └── websocket.ts            # WebSocket 配置
│   │   └── types/                  # TypeScript 类型定义
│   ├── tests/                      # 前端测试
│   └── cypress/                    # E2E 测试
│
├── ⚙️ quant_backend/                # Flask 后端服务
│   ├── api/                        # RESTful API 路由
│   │   ├── market_data_routes.py       # 市场数据 API
│   │   └── strategy_routes.py          # 策略回测 API
│   ├── services/                   # 业务逻辑服务
│   │   ├── akshare_service.py          # AKShare 数据服务
│   │   └── strategy_service.py         # 策略服务
│   ├── bt_strategies/              # Backtrader 策略模块
│   │   ├── strategies/                 # 策略实现
│   │   │   ├── ma_cross_strategy.py        # 均线交叉策略
│   │   │   └── volume_breakout_strategy.py # 交易量突破策略
│   │   ├── backtest_runner.py          # 回测执行引擎
│   │   └── bt_result_parser.py         # 结果解析器
│   ├── utils/                      # 工具类
│   │   └── technical_indicators.py    # 技术指标计算
│   └── tests/                      # 后端测试
│
├── 📋 .github/workflows/            # CI/CD 工作流
├── 📄 requirements.txt              # Python 依赖管理
├── 📄 pyproject.toml               # 项目配置
└── 📚 README.md                    # 项目文档
```

## 🔧 核心功能模块

### 1. 🎯 双引擎回测系统

#### 默认引擎
- **技术栈**: pandas + NumPy
- **特点**: 轻量级、快速执行
- **适用**: 简单策略验证

#### Backtrader 引擎  
- **技术栈**: Backtrader 专业框架
- **特点**: 功能完整、扩展性强
- **适用**: 复杂策略开发

```typescript
// 前端引擎切换
const engineType = ref<BacktestEngineType>('backtrader');
await apiService.runBacktest(params, engineType);
```

### 2. 📊 数据获取与处理

#### AKShare 集成
- **股票列表**: A 股全市场股票信息
- **历史数据**: OHLCV 日线数据
- **技术指标**: MA、OBV、VR、MFI 等

```python
# 后端数据服务
def get_stock_historical_data(ts_code, start_date, end_date):
    return ak.stock_zh_a_hist(symbol=ts_code, 
                              start_date=start_date, 
                              end_date=end_date)
```

### 3. 🎨 交互式可视化

#### ECharts 图表系统
- **价格图表**: K线图、移动平均线
- **技术指标**: 多指标叠加显示  
- **交易信号**: 买卖点标记
- **资金曲线**: 投资组合价值变化

### 4. ⚡ 实时通信架构

#### WebSocket 集成
- **前端**: Socket.IO Client
- **后端**: Flask-SocketIO
- **功能**: 实时数据推送、状态同步

## 🚀 快速开始

### 环境要求
- **Python**: 3.8+ 
- **Node.js**: 16+
- **包管理器**: npm/yarn/pnpm

### 🔧 后端部署

1. **环境准备**
   ```bash
   git clone https://github.com/yourusername/quantTrade-aiAgent.git
   cd quantTrade-aiAgent
   
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate   # Windows
   ```

2. **依赖安装**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务**
   ```bash
   cd quant_backend
   PYTHONPATH=.. python3 app.py
   ```
   服务地址: http://localhost:5002

### 🎨 前端部署

1. **依赖安装**
   ```bash
   cd quant_frontend
   npm install
   ```

2. **开发环境**
   ```bash
   npm run dev
   ```
   访问地址: http://localhost:5173

3. **生产构建**
   ```bash
   npm run build
   ```

## 📖 使用指南

### 1. 策略回测流程

1. **选择回测引擎**
   - 默认引擎：适合快速验证
   - Backtrader：适合专业分析

2. **配置回测参数**
   ```vue
   <template>
     <el-select v-model="params.strategy_name">
       <el-option label="均线交叉策略" value="ma_cross" />
       <el-option label="交易量突破策略" value="volume_breakout" />
     </el-select>
   </template>
   ```

3. **执行回测分析**
   - 设置股票代码（如：000001.SZ）
   - 选择时间范围
   - 调整策略参数
   - 点击"运行策略回测"

### 2. 结果分析面板

#### 性能指标
- **总收益率**: 投资期间总回报
- **年化收益率**: 年化投资回报率  
- **最大回撤**: 最大资金损失幅度
- **夏普比率**: 风险调整后收益

#### 可视化图表
- **价格走势**: 股价变化与均线系统
- **交易信号**: 买入/卖出点位标记
- **资金曲线**: 投资组合价值变化
- **技术指标**: 多维度技术分析

## 🧪 测试体系

### 前端测试
```bash
# 单元测试
npm run test

# E2E 测试  
npm run cypress:open
```

### 后端测试
```bash
# 运行所有测试
pytest

# Backtrader 集成测试
pytest bt_strategies/tests/test_backtest_runner.py -v

# AKShare 服务测试
pytest tests/test_akshare_service.py -v
```

## 🔄 API 接口文档

### 市场数据接口

#### `GET /api/market_data/historical`
获取股票历史数据
```json
{
  "symbol": "000001.SZ",
  "start_date": "2025-01-01", 
  "end_date": "2025-06-01"
}
```

#### `GET /api/market_data/stock_list`
获取A股股票列表
```json
{
  "data": [
    {"ts_code": "000001.SZ", "name": "平安银行"},
    {"ts_code": "000002.SZ", "name": "万科A"}
  ]
}
```

### 策略回测接口

#### `POST /api/strategy/backtest`
默认引擎回测
```json
{
  "strategy_name": "ma_cross",
  "symbol": "000001.SZ",
  "start_date": "2025-01-01",
  "end_date": "2025-06-01", 
  "initial_capital": 100000,
  "short_window": 20,
  "long_window": 50
}
```

#### `POST /api/strategy/backtest_bt`
Backtrader 引擎回测
```json
{
  "strategy_name": "ma_cross",
  "symbol": "000001.SZ", 
  "start_date": "2025-01-01",
  "end_date": "2025-06-01",
  "initial_capital": 100000,
  "short_window": 20,
  "long_window": 50
}
```

## 🎯 策略开发指南

### 创建新策略

1. **Backtrader 策略示例**
   ```python
   class CustomStrategy(bt.Strategy):
       params = (
           ('period', 20),
           ('threshold', 0.02),
       )
       
       def __init__(self):
           self.sma = bt.indicators.SimpleMovingAverage(
               self.datas[0], period=self.params.period
           )
           
       def next(self):
           if not self.position:
               if self.data.close[0] > self.sma[0] * (1 + self.params.threshold):
                   self.buy()
           else:
               if self.data.close[0] < self.sma[0] * (1 - self.params.threshold):
                   self.sell()
   ```

2. **注册新策略**
   ```python
   # 在 bt_strategies/strategies/__init__.py 中添加
   from .custom_strategy import CustomStrategy
   __all__ = ['MaCrossStrategy', 'VolumeBreakoutStrategy', 'CustomStrategy']
   ```

## ⚠️ 常见问题

### 端口冲突
```bash
# 查找占用进程
lsof -i :5002
# 或更换端口
python app.py --port=5003
```

### 模块导入错误
```bash
# 确保正确的 PYTHONPATH
cd quant_backend
PYTHONPATH=.. python3 app.py
```

### WebSocket 连接失败
- 检查后端服务状态
- 确认 CORS 配置
- 清除浏览器缓存

### 图表显示异常
- 检查回测参数有效性
- 确认数据获取成功
- 调整浏览器窗口大小

## 🗺️ 开发路线图

### 🚧 进行中
- [ ] 多品种组合回测
- [ ] 策略性能优化算法
- [ ] 实时行情数据接入

### 📋 计划中
- [ ] 机器学习策略模块
- [ ] 风险管理系统
- [ ] 策略市场平台
- [ ] 移动端 App

### 🎯 长期目标
- [ ] 量化基金管理
- [ ] 社区策略分享
- [ ] 实盘交易接口
- [ ] 多语言国际化

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`) 
5. 创建 Pull Request

### 代码规范
- **前端**: ESLint + Prettier
- **后端**: PEP 8 + Black
- **提交**: Conventional Commits

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 🙏 致谢

感谢以下开源项目的支持：

- [**Vue.js**](https://vuejs.org/) - 渐进式前端框架
- [**Flask**](https://flask.palletsprojects.com/) - 轻量级 Web 框架  
- [**Backtrader**](https://www.backtrader.com/) - Python 回测框架
- [**AKShare**](https://github.com/akfamily/akshare) - 金融数据接口
- [**ECharts**](https://echarts.apache.org/) - 数据可视化图表库
- [**Element Plus**](https://element-plus.org/) - Vue 3 组件库
- [**Tailwind CSS**](https://tailwindcss.com/) - CSS 框架

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给它一个星标！**

[📖 文档](README.md) • [🐛 问题反馈](https://github.com/yourusername/quantTrade-aiAgent/issues) • [💬 讨论](https://github.com/yourusername/quantTrade-aiAgent/discussions)

</div>
