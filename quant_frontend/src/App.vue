<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-full mx-auto py-4 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">个人量化交易系统</h1>
        <div class="flex items-center space-x-4">
          <div class="text-sm text-gray-600">
            <span v-if="socketStatus === 'connected'" class="inline-block w-2 h-2 rounded-full bg-green-500 mr-2"></span>
            <span v-else class="inline-block w-2 h-2 rounded-full bg-red-500 mr-2"></span>
            {{ socketStatus === 'connected' ? '已连接' : '未连接' }}
          </div>
        </div>
      </div>
    </header>
    
    <main class="py-4">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <!-- 主要内容区域 - 采用双列布局 -->
        <div class="flex flex-col lg:flex-row lg:space-x-6">
          
          <!-- 左侧控制面板 - 选股与指标可视化 -->
          <div class="w-full lg:w-2/3 flex-shrink-0 mb-6 lg:mb-0">
            <div class="bg-white rounded-lg shadow p-4 mb-6">
              <h2 class="text-lg font-bold mb-2">股票选股与多指标可视化</h2>
              <StockSelector @select="onSelectStock" />
              <IndicatorChart v-if="indicators" :indicators="indicators" class="mt-4" />
            </div>
            <div class="sticky top-20">
              <!-- 策略回测面板 -->
              <StrategyRunner @backtest-completed="handleBacktestResults" />
              <!-- 性能指标摘要 - 在小屏幕上不显示，在回测结果下方显示 -->
              <div v-if="backtestResults?.performance" class="mt-4 bg-white rounded-lg shadow p-4 hidden lg:block">
                <h3 class="text-lg font-medium mb-2">主要性能指标</h3>
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-500">总收益率</p>
                    <p class="text-lg font-semibold" :class="{ 'text-green-600': backtestResults.performance.total_return > 0, 'text-red-600': backtestResults.performance.total_return < 0 }">
                      {{ (backtestResults.performance.total_return * 100).toFixed(2) }}%
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">年化收益</p>
                    <p class="text-lg font-semibold" :class="{ 'text-green-600': backtestResults.performance.annual_return > 0, 'text-red-600': backtestResults.performance.annual_return < 0 }">
                      {{ (backtestResults.performance.annual_return * 100).toFixed(2) }}%
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">最大回撤</p>
                    <p class="text-lg font-semibold text-red-600">
                      {{ (backtestResults.performance.max_drawdown * 100).toFixed(2) }}%
                    </p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">夏普比率</p>
                    <p class="text-lg font-semibold">
                      {{ backtestResults.performance.sharpe_ratio ? backtestResults.performance.sharpe_ratio.toFixed(2) : 'N/A' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 右侧结果区域 - 占据剩余空间 -->
          <div class="flex-grow">
            <!-- 结果可视化区域 -->
            <div class="bg-white rounded-lg shadow overflow-hidden mt-6">
              <ResultsChart v-if="backtestResults" :results="backtestResults" />
              <div v-else class="p-8 text-center text-gray-500 min-h-[400px] flex items-center justify-center bg-gray-50">
                <div>
                  <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <p class="text-lg">请在左侧设置参数并运行策略回测</p>
                  <p class="text-sm mt-2">回测结果将在此处显示</p>
                </div>
              </div>
            </div>
            
            <!-- 绩效详情 -->
            <div v-if="backtestResults" class="mt-6">
              <PerformanceMetrics 
                :performance="backtestResults.performance"
                :buy-signals="backtestResults.chart_data?.buy_signals"
                :sell-signals="backtestResults.chart_data?.sell_signals"
                :total-days="backtestResults.chart_data?.dates?.length || 0"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
    
    <!-- 底部信息区域 -->
    <footer class="bg-white mt-8 py-4 border-t border-gray-200">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <p class="text-center text-sm text-gray-500">
          个人量化交易系统 &copy; {{ new Date().getFullYear() }} | 基于Vue3、Flask和ECharts构建
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { initWebSocket, disconnectWebSocket, sendMessage, socket } from './config/websocket';
import StrategyRunner from './components/StrategyRunner.vue';
import ResultsChart from './components/ResultsChart.vue';
import PerformanceMetrics from './components/PerformanceMetrics.vue';
import StockSelector from './components/StockSelector.vue';
import IndicatorChart from './components/IndicatorChart.vue';
import { apiService } from './services/api';
import type { IndicatorResult, BacktestResult as ApiBacktestResult } from './services/api';

// WebSocket状态
const socketStatus = ref<string | null>('disconnected');

// 组件挂载时初始化 WebSocket
onMounted(() => {
  initWebSocket();
  
  // 监听socket连接状态
  socket.on('connect', () => {
    socketStatus.value = 'connected';
    console.log('WebSocket连接成功');
  });
  
  socket.on('disconnect', () => {
    socketStatus.value = 'disconnected';
    console.log('WebSocket断开连接');
  });
  
  socket.on('connect_error', (error) => {
    socketStatus.value = 'disconnected';
    console.error('WebSocket连接错误:', error);
  });
});

// 组件卸载时断开 WebSocket
onUnmounted(() => {
  disconnectWebSocket();
});

// 回测结果
const backtestResults = ref<ApiBacktestResult | null>(null);
const indicators = ref<IndicatorResult | null>(null);

// 处理回测结果
function handleBacktestResults(results: ApiBacktestResult) {
  console.log('回测结果:', results);
  backtestResults.value = results;
  if (results && results.performance && typeof results.performance.sharpe_ratio === 'undefined') {
    const totalReturn = results.performance.total_return;
    const maxDrawdown = Math.abs(results.performance.max_drawdown);
    if (maxDrawdown > 0) {
      results.performance.sharpe_ratio = totalReturn / maxDrawdown;
    } else {
      results.performance.sharpe_ratio = totalReturn > 0 ? 3 : 0;
    }
  }
}

async function onSelectStock(ts_code: string, dateRange?: [Date, Date]) {
  indicators.value = null;
  try {
    let startDate: string, endDate: string;
    
    if (dateRange && dateRange.length === 2) {
      // 健壮性判断，确保为合法Date
      const [startRaw, endRaw] = dateRange;
      const startObj = (startRaw instanceof Date && !isNaN(startRaw.getTime())) ? startRaw : new Date(startRaw);
      const endObj = (endRaw instanceof Date && !isNaN(endRaw.getTime())) ? endRaw : new Date(endRaw);
      if (isNaN(startObj.getTime()) || isNaN(endObj.getTime())) {
        indicators.value = null;
        console.error('无效日期:', dateRange);
        return;
      }
      startDate = startObj.toISOString().slice(0, 10).replace(/-/g, '');
      endDate = endObj.toISOString().slice(0, 10).replace(/-/g, '');
    } else {
      // 默认使用最近7天
      const now = new Date();
      const end = new Date(now);
      const start = new Date(now);
      start.setDate(start.getDate() - 7);
      endDate = end.toISOString().slice(0, 10).replace(/-/g, '');
      startDate = start.toISOString().slice(0, 10).replace(/-/g, '');
    }
    
    console.log('请求指标数据:', { ts_code, startDate, endDate });
    
    const res = await apiService.getIndicators({
      ts_code,
      start_date: startDate,
      end_date: endDate,
      ma_windows: '5,20,60',
      vma_windows: '5'
    });
    
    indicators.value = res;
    console.log('获取指标数据成功:', res);
  } catch (e: any) {
    indicators.value = null;
    console.error('获取指标数据失败:', e);
    if (e?.response?.data) {
      console.error('服务器响应:', e.response.data);
    } else {
      console.error('错误详情:', e);
    }
  }
}
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}

/* 响应式大屏幕优化 */
@media (min-width: 1280px) {
  .max-w-full {
    max-width: 1800px;
  }
}

/* 改善滚动行为 */
html {
  scroll-behavior: smooth;
}

/* 提高图表对比度 */
.chart-container {
  background-color: white;
}
</style>
