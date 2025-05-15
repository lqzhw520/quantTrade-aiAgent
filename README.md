# quantTrade-aiAgent

基于 Python Flask 和 Vue3 的全栈量化交易系统，用于个人投资策略回测和分析。

## 项目简介

quantTrade-aiAgent 是一个面向个人投资者的量化交易系统，提供市场数据获取、策略回测、交易信号生成和结果可视化功能。系统采用现代前后端分离架构，让用户可以通过直观的界面进行策略参数设置和结果分析。

## 技术栈

### 前端
- Vue 3 (组合式 API)
- TypeScript
- Vite
- Tailwind CSS
- Socket.IO 客户端
- ECharts (数据可视化)

### 后端
- Flask (Python Web 框架)
- Flask-SocketIO (WebSocket 通信)
- yfinance (Yahoo Finance 数据获取)
- pandas (数据处理和分析)
- NumPy (数学计算)

## 系统架构

```
quantTrade-aiAgent/
├── quant_frontend/                # Vue3 前端
│   ├── src/
│   │   ├── components/           # UI 组件
│   │   │   ├── StrategyRunner.vue    # 策略运行控制组件
│   │   │   ├── ResultsChart.vue      # 结果图表组件
│   │   │   └── PerformanceMetrics.vue # 性能指标组件 
│   │   ├── config/               # API 和 WebSocket 配置
│   │   │   └── websocket.ts      # WebSocket 连接配置
│   │   ├── services/             # API 服务封装
│   │   │   └── api.ts            # 后端 API 调用
│   │   ├── assets/               # 静态资源
│   │   └── main.ts               # 应用入口
│   ├── public/                   # 静态资源
│   └── index.html                # HTML 模板
│
├── quant_backend/                 # Flask 后端
│   ├── api/                      # API 路由
│   │   ├── market_data_routes.py # 市场数据 API
│   │   └── strategy_routes.py    # 策略回测 API
│   ├── services/                 # 业务逻辑服务
│   │   ├── market_data_service.py # 市场数据服务
│   │   └── strategy_service.py   # 策略服务
│   ├── utils/                    # 工具类
│   │   └── technical_indicators.py # 技术指标计算
│   ├── tests/                    # 单元测试
│   └── app.py                    # Flask 应用入口
│
├── .github/                      # GitHub 配置
│   └── workflows/                # CI/CD 工作流
│       └── ci.yml                # 持续集成配置
├── requirements.txt              # Python 依赖
└── README.md                     # 项目文档
```

## 功能特点

- **市场数据获取**：从 Yahoo Finance 获取股票历史数据
- **技术指标计算**：支持移动平均线等技术指标
- **策略回测**：基于历史数据执行交易策略回测
- **实时数据可视化**：交互式图表展示价格、指标和交易信号
- **WebSocket 实时通信**：前后端实时数据交互
- **响应式设计**：适配桌面端和移动端的界面
- **策略预设模板**：提供保守型和激进型预设策略
- **绩效分析**：计算关键绩效指标如年化收益率、最大回撤和夏普比率

## API 接口说明

### 后端 API 接口

#### 市场数据接口
- `GET /api/market_data/historical`：获取股票历史数据
  - 参数：symbol（股票代码）, start_date（开始日期）, end_date（结束日期）
  - 响应：包含日期、收盘价和交易量的时间序列数据

- `GET /api/market_data/latest_price`：获取最新价格
  - 参数：symbol（股票代码）
  - 响应：最新价格和时间戳

#### 策略接口
- `POST /api/strategy/backtest`：执行策略回测
  - 参数：strategy_name, symbol, start_date, end_date, initial_capital, short_window, long_window
  - 响应：包含绩效指标和图表数据的回测结果

### WebSocket 事件
- `client_event`：客户端发送消息到服务器
- `server_response`：服务器响应客户端消息
- `connect`：WebSocket 连接建立
- `disconnect`：WebSocket 连接断开

## 安装与运行

### 环境要求
- Python 3.8+ 
- Node.js 16+
- npm 或 yarn

### 后端设置

1. **克隆仓库**
   ```bash
   git clone https://github.com/yourusername/quantTrade-aiAgent.git
   cd quantTrade-aiAgent
   ```

2. **创建虚拟环境**（可选但推荐）
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装 Python 依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动后端服务**
   ```bash
   cd quant_backend
   PYTHONPATH=.. python3 app.py
   ```
   后端服务将在 http://localhost:5002 启动

### 前端设置

1. **安装 Node.js 依赖**
   ```bash
   cd quant_frontend
   npm install
   ```

2. **启动前端开发服务器**
   ```bash
   npm run dev
   ```
   前端服务将在 http://localhost:5173 启动（或其他可用端口）

3. **构建生产环境版本**
   ```bash
   npm run build
   ```
   构建后的文件将位于 `dist` 目录中

## 使用指南

1. **访问前端界面**
   - 打开浏览器，访问 http://localhost:5173 (或终端显示的其他端口)

2. **策略回测**
   - 填写股票代码（例如：TSLA）
   - 设置回测时间范围
   - 输入初始资金数额
   - 调整短期和长期移动平均线窗口期
   - 点击"运行回测"按钮

3. **查看回测结果**
   - 图表展示股票价格、移动平均线和交易信号
   - 绩效指标显示总收益率、年化收益率、最大回撤和夏普比率
   - 交易记录表格展示各笔交易详情

4. **使用预设模板**
   - 可以点击预设的策略模板（保守型、激进型）快速填充参数

## 系统演示

系统主要分为三个部分：

1. **策略参数设置区**：左侧面板用于设置回测参数和运行策略
2. **交易图表**：右侧上方展示价格走势、移动平均线和交易信号
3. **绩效指标**：右侧下方展示策略的表现指标和交易记录

回测完成后，系统会自动生成交易信号图表和绩效指标：

- 蓝色线条：股票价格
- 绿色/红色线条：短期/长期移动平均线 
- 绿色箭头：买入信号
- 红色箭头：卖出信号
- 下方蓝色区域：资产净值变化

绩效指标面板会显示总收益率、年化收益率、最大回撤等关键指标，以及详细的交易记录。

## CI/CD 集成

本项目已配置 GitHub Actions 进行自动化测试和部署。当您将代码推送到 GitHub 仓库或创建 Pull Request 时，会自动触发测试流程。

### 自动测试配置

在项目根目录下创建 `.github/workflows/ci.yml` 文件以配置 GitHub Actions 工作流：

```yaml
name: Python Flask + Vue CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install -r requirements.txt
        
    - name: Run backend tests
      run: |
        cd quant_backend
        PYTHONPATH=.. pytest --cov=. --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./quant_backend/coverage.xml
        flags: backend

  frontend-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '16.x'
        
    - name: Install dependencies
      run: |
        cd quant_frontend
        npm install
        
    - name: Run frontend tests
      run: |
        cd quant_frontend
        npm run test:unit
        
    - name: Build frontend
      run: |
        cd quant_frontend
        npm run build
```

### 部署配置示例

对于自动部署，可以添加部署步骤到 CI 工作流文件中：

```yaml
deploy:
  needs: [backend-test, frontend-test]
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  runs-on: ubuntu-latest
  
  steps:
  - uses: actions/checkout@v4
  
  # 构建前端
  - name: Set up Node.js
    uses: actions/setup-node@v3
    with:
      node-version: '16.x'
      
  - name: Build frontend
    run: |
      cd quant_frontend
      npm install
      npm run build
  
  # 部署到服务器
  - name: Deploy to server
    uses: appleboy/scp-action@master
    with:
      host: ${{ secrets.HOST }}
      username: ${{ secrets.USERNAME }}
      key: ${{ secrets.SSH_KEY }}
      source: "quant_backend/, quant_frontend/dist/, requirements.txt"
      target: "/path/to/deploy"
      
  - name: Setup remote server
    uses: appleboy/ssh-action@master
    with:
      host: ${{ secrets.HOST }}
      username: ${{ secrets.USERNAME }}
      key: ${{ secrets.SSH_KEY }}
      script: |
        cd /path/to/deploy
        python -m venv venv || true
        source venv/bin/activate
        pip install -r requirements.txt
        sudo systemctl restart quant-agent.service
```

## 常见问题 (Q&A)

### 1. 端口冲突问题

**问题**: 启动服务时出现错误 `Address already in use`

**解决方案**: 
```bash
# 查找占用端口的进程
lsof -i :5002 | grep LISTEN

# 终止对应进程
kill -9 <进程ID>

# 或指定一个不同的端口启动服务
cd quant_backend && PYTHONPATH=.. python3 app.py --port=5003
```

### 2. Python 模块导入错误

**问题**: 启动后端时报错 `ModuleNotFoundError: No module named 'quant_backend'`

**解决方案**:
```bash
# 确保设置正确的 PYTHONPATH
cd quant_backend
PYTHONPATH=.. python3 app.py
```

### 3. WebSocket 连接问题

**问题**: 前端显示 WebSocket 连接失败

**解决方案**:
- 确保后端服务正常运行
- 检查浏览器控制台是否有 CORS 错误，确认 app.py 中配置了正确的 CORS 设置
- 前端 WebSocket 配置中的 URL 是否与后端 URL 匹配
- 尝试在浏览器控制台执行 `localStorage.clear()` 清除可能的缓存

### 4. 图表显示不正确

**问题**: 回测结果图表无法正确显示或报错 "Can't get DOM width or height"

**解决方案**:
- 检查浏览器控制台是否有错误信息
- 确保回测请求参数有效（日期格式正确，MA窗口期合理）
- 尝试调整浏览器窗口大小或刷新页面
- 在图表容器中设置明确的宽高值

### 5. 回测请求失败

**问题**: 发送回测请求后无响应或返回错误

**解决方案**:
- 检查后端日志是否有异常信息
- 确认请求参数格式正确
- 验证 API 路径是否正确 (应为 `/api/strategy/backtest`)
- 检查网络连接和 CORS 设置

### 6. macOS 上的端口 5000 被占用

**问题**: 在 macOS 上端口 5000 可能被 AirPlay Receiver 服务占用

**解决方案**:
- 在系统设置中禁用 AirPlay Receiver 服务
- 或者在后端配置中使用其他端口（例如 5001 或 5002）

### 7. 无法获取股票数据

**问题**: 使用 yfinance 获取数据时返回空或出错

**解决方案**:
- 确认股票代码正确（例如，"AAPL" 而非 "APPLE"）
- 检查日期范围是否有效（非交易日可能没有数据）
- 确保网络连接正常，没有被限制访问 Yahoo Finance
- 尝试降低请求频率，避免被 API 限流

## 待办事项（未来开发计划）

以下是计划在未来版本中添加的功能：

1. **多策略支持**：除了移动平均线交叉策略外，增加更多的常用策略实现
   - 布林带策略
   - RSI 指标策略
   - MACD 策略
   - 趋势跟踪策略

2. **策略参数优化**：基于遗传算法、网格搜索等方法寻找最优参数

3. **回测报告导出**：支持将回测结果导出为 PDF 或 Excel 格式

4. **多周期分析**：支持不同时间周期（日、周、月）的回测比较

5. **数据源扩展**：
   - 支持更多数据源（如 Alpha Vantage、Polygon 等）
   - 增加基本面数据分析

6. **风险管理功能**：
   - 止损/止盈设置
   - 头寸管理
   - 风险评估仪表板

7. **用户账户系统**：
   - 添加用户注册/登录功能
   - 保存用户策略配置和回测历史

8. **实时市场数据**：接入实时市场数据，支持模拟交易

## 开发与贡献

欢迎提交 issue 和 pull request 来改进项目。请确保代码遵循项目的风格指南和测试要求。

### 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个 Pull Request

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 致谢

- [yfinance](https://github.com/ranaroussi/yfinance) - 提供 Yahoo Finance 数据访问
- [ECharts](https://echarts.apache.org/) - 强大的交互式图表库
- [Vue.js](https://vuejs.org/) - 响应式前端框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Python Web 框架
- [Tailwind CSS](https://tailwindcss.com/) - 实用优先的 CSS 框架
