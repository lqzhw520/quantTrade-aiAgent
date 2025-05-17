# 项目记忆文件（memories.md）

## 项目简介
quantTrade-aiAgent 是一个基于 Flask 和 Vue3 的个人量化交易系统，支持 A 股历史数据获取、技术指标分析、策略回测和交互式图表展示。

---

## 📈 策略模块
- 策略逻辑核心位于 `quant_backend/services/strategy_service.py`
- 所有策略通过 `/api/strategy/backtest` POST 接口传参执行
- 常见错误包括 symbol 缺失、日期格式不合法、AKShare 返回空数据
- 建议参数校验逻辑优先放在 `strategy_routes.py` 中完成
- 推荐用例：回测含 1 个 symbol 和 2 个技术指标（如 MA, MACD）

---

## 📊 图表模块
- 图表绘制逻辑主要集中在 `ResultsChart.vue`
- 使用 ECharts 渲染回测绩效与指标曲线，注意响应式宽高适配问题（已多次出现 offsetWidth 为 undefined 的报错）
- 使用 `<el-tabs>` 控制不同图层切换，确保切换后 DOM 正确初始化
- 如需动态更新数据，调用 `echartsInstance.setOption(option, true)`

---

## 🌐 WebSocket 通信模块
- 使用 Socket.IO 实现客户端实时数据推送
- 客户端配置见 `quant_frontend/src/config/websocket.ts`
- 后端初始化见 `quant_backend/app.py` 中 `socketio = SocketIO(app)`
- 常见问题：连接断开/超时、命名空间不一致、CORS 问题
- 调试建议：前端用 Chrome DevTools WebSocket 面板监测连接状态

---

## ✅ 测试说明
- 后端测试位于 `quant_backend/tests/`，使用 `pytest`
- 前端测试位于 `quant_frontend/tests/`，使用 `vitest` + `@vue/test-utils`
- 若修复图表组件，请确保至少运行以下命令：
  ```bash
  cd quant_frontend && npm run test
  ```

---

## 🔄 已解决问题与经验

### 前端日期处理

1. **el-date-picker 类型不一致问题**：
   - 问题：`value-format="YYYYMMDD"` 会导致 v-model 变为字符串，而非 Date 对象
   - 解决方案：去掉 value-format，保持 v-model 类型为 Date 对象，在 emit 前手动格式化
   - 相关文件：`StockSelector.vue`, `App.vue`
   - 代码示例：
     ```js
     if (code && startDate.value && endDate.value) {
       // 确保为Date对象
       const start = startDate.value instanceof Date ? startDate.value : new Date(startDate.value);
       const end = endDate.value instanceof Date ? endDate.value : new Date(endDate.value);
       // 格式化为后端需要的格式
       const formattedStart = start.toISOString().slice(0, 10).replace(/-/g, '');
       const formattedEnd = end.toISOString().slice(0, 10).replace(/-/g, '');
       emit('select', code, [start, end]);
     }
     ```

2. **日期类型兼容性处理**：
   - 问题：`onDateChange` 中 instanceof Date 检查失败
   - 解决方案：增加字符串日期转换为 Date 对象的逻辑
   - 相关文件：`StockSelector.vue`
   - 代码示例：
     ```js
     if (typeof start === 'string') {
       start = new Date(start.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'));
     }
     ```

### Cypress 测试兼容性

1. **el-select 远程模式与 Cypress 兼容性问题**：
   - 问题：即使 `filteredStocks` 有数据，使用 `cy.get('.el-select-dropdown__item')` 也无法找到下拉项
   - 原因：Element Plus 的 el-select 远程模式在 headless 环境下下拉渲染有特殊机制
   - 解决方案：
     - 方案1：使用 `npx cypress open` 手动测试，非 headless 模式更稳定
     - 方案2：将 el-select 切换为本地 filterable 模式仅用于测试
     - 方案3：mock 股票数据接口，确保始终返回测试用数据

2. **Cypress 测试元素定位优化**：
   - 所有关键交互元素添加 `data-cy` 属性
   - 示例：`data-cy="stock-select"`, `data-cy="start-date"`, `data-cy="indicator-chart"`
   - 测试脚本使用如 `cy.get('[data-cy=stock-select]')` 定位，提高稳定性

### AKShare 数据源使用

1. **参数格式校验**：
   - 问题：错误的日期格式或股票代码会导致 AKShare 接口失败
   - 解决方案：在服务层增加参数校验逻辑
   - 相关文件：`market_data_service.py`, `akshare_service.py`
   - 实现：检查日期格式（必须为 YYYYMMDD）、股票代码格式
     ```python
     def validate_stock_code(stock_code: str) -> bool:
         """验证股票代码格式"""
         pattern = r'^\d{6}\.(SZ|SH)$'
         return bool(re.match(pattern, stock_code))
     ```

2. **错误处理与友好提示**：
   - 封装 AKShare 接口调用，统一处理异常
   - 捕获具体异常类型（如 KeyError, ValueError），返回友好错误信息
   - 日志记录，便于排查问题

### 前端组件架构优化

1. **StockSelector 独立日期选择**：
   - 实现：将 dateRange 改为独立的 startDate 和 endDate
   - 确保日期选择互相独立，不互相影响
   - 在选择完成后自动触发指标计算

2. **IndicatorChart 空数据处理**：
   - 增加 `<div v-if="!props.indicators">暂无数据</div>` 提示
   - 添加 `data-cy="no-data-message"` 和 `data-cy="indicator-chart"` 便于测试
   - 对空数组或 null/undefined 数据进行健壮性处理

---

## 🤖 Agent 操作建议
- 若任务来自 DOM 错误，优先查看 ResultsChart.vue 与组件挂载时机
- 涉及策略回测失败，请检查 `strategy_service.py` 与调用参数
- 涉及 websocket 报错，应确认配置一致性（config 与 server）
- 执行完修复操作后，建议运行：
  ```bash
  cd quant_backend && pytest
  cd quant_frontend && npm run test
  ```
- 对于前端日期处理问题，确保去掉 value-format，保持 Date 对象一致性
- 对于 Cypress 测试问题，考虑使用 npx cypress open 手动操作验证
```
