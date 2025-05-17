<template>
  <DashboardLayout>
    <template #header>
      <header class="bg-white shadow-sm sticky top-0 z-10">
        <div class="w-full mx-auto py-3 px-2 flex justify-between items-center">
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
    </template>
    <template #default>
      <main class="w-full">
        <div class="w-full">
          <Splitpanes class="default-theme h-full min-h-[600px]" horizontal :push-other-panes="false" data-cy="main-splitpanes">
            <Pane min-size="20" max-size="30" size="25" data-cy="left-pane" class="h-full">
              <!-- 左侧：股票选择与参数 -->
              <div class="bg-white rounded-lg shadow p-4 mb-4">
                <h2 class="text-lg font-bold mb-3">股票选股与多指标可视化</h2>
                <StockSelector @select="onSelectStock" />
                <IndicatorChart v-if="indicators" :indicators="indicators" class="mt-4" />
              </div>
              <div class="bg-white rounded-lg shadow p-4 sticky top-20">
                <StrategyRunner @backtest-completed="handleBacktestResults" />
              </div>
            </Pane>
            <Pane min-size="40" max-size="60" size="50" data-cy="center-pane" class="h-full flex-1">
              <!-- 中间：工具栏+主图表区 -->
              <ChartToolbar class="mb-1" />
              <ChartWorkspace>
                <ResultsChart v-if="backtestResults" :results="backtestResults" />
                <div v-else class="p-6 text-center text-gray-500 min-h-[400px] flex items-center justify-center bg-gray-50">
                  <div>
                    <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                    <p class="text-lg">请在左侧设置参数并运行策略回测</p>
                    <p class="text-sm mt-2">回测结果将在此处显示</p>
                  </div>
                </div>
              </ChartWorkspace>
              <div v-if="backtestResults" class="mt-4">
                <PerformanceMetrics 
                  :performance="backtestResults.performance"
                  :buy-signals="backtestResults.chart_data?.buy_signals"
                  :sell-signals="backtestResults.chart_data?.sell_signals"
                  :total-days="backtestResults.chart_data?.dates?.length || 0"
                />
              </div>
            </Pane>
            <Pane min-size="20" max-size="30" size="25" data-cy="right-pane" class="h-full">
              <!-- 右侧：分析面板 -->
              <div class="bg-white rounded-lg shadow p-4">
                <AnalysisPanel />
              </div>
            </Pane>
          </Splitpanes>
        </div>
      </main>
    </template>
    <template #footer>
      <footer class="bg-white mt-4 py-3 border-t border-gray-200">
        <div class="w-full mx-auto px-2">
          <p class="text-center text-sm text-gray-500">
            个人量化交易系统 &copy; {{ new Date().getFullYear() }} | 基于Vue3、Flask和ECharts构建
          </p>
        </div>
      </footer>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { initWebSocket, disconnectWebSocket, sendMessage, socket } from './config/websocket';
import StrategyRunner from './components/StrategyRunner.vue';
import ResultsChart from './components/ResultsChart.vue';
import PerformanceMetrics from './components/PerformanceMetrics.vue';
import StockSelector from './components/StockSelector.vue';
import IndicatorChart from './components/IndicatorChart.vue';
import ChartWorkspace from './components/ChartWorkspace.vue';
import ChartToolbar from './components/ChartToolbar.vue';
import AnalysisPanel from './components/AnalysisPanel.vue';
import { apiService } from './services/api';
import DashboardLayout from './components/DashboardLayout.vue';
import type { IndicatorResult, BacktestResult as ApiBacktestResult } from './services/api';
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

const socketStatus = ref<string | null>('disconnected');

onMounted(() => {
  initWebSocket();
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

onUnmounted(() => {
  disconnectWebSocket();
});

const backtestResults = ref<ApiBacktestResult | null>(null);
const indicators = ref<IndicatorResult | null>(null);

function handleBacktestResults(results: ApiBacktestResult) {
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
      const [startRaw, endRaw] = dateRange;
      const startObj = (startRaw instanceof Date && !isNaN(startRaw.getTime())) ? startRaw : new Date(startRaw);
      const endObj = (endRaw instanceof Date && !isNaN(endRaw.getTime())) ? endRaw : new Date(endRaw);
      if (isNaN(startObj.getTime()) || isNaN(endObj.getTime())) {
        indicators.value = null;
        return;
      }
      startDate = startObj.toISOString().slice(0, 10).replace(/-/g, '');
      endDate = endObj.toISOString().slice(0, 10).replace(/-/g, '');
    } else {
      const now = new Date();
      const end = new Date(now);
      const start = new Date(now);
      start.setDate(start.getDate() - 7);
      endDate = end.toISOString().slice(0, 10).replace(/-/g, '');
      startDate = start.toISOString().slice(0, 10).replace(/-/g, '');
    }
    const res = await apiService.getIndicators({
      ts_code,
      start_date: startDate,
      end_date: endDate,
      ma_windows: '5,20,60',
      vma_windows: '5'
    });
    indicators.value = res;
  } catch (e: any) {
    indicators.value = null;
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
  overflow-x: hidden;
  width: 100%;
}
html {
  scroll-behavior: smooth;
  overflow-x: hidden;
  width: 100%;
}
.chart-container {
  background-color: white;
  width: 100%;
}
/* Splitpanes自定义样式 */
.splitpanes__pane {
  box-sizing: border-box !important;
}
.splitpanes--horizontal > .splitpanes__splitter {
  min-height: 6px;
  background: #f0f0f0;
}
.splitpanes--vertical > .splitpanes__splitter {
  min-width: 6px;
  background: #f0f0f0;
}
.splitpanes__splitter:hover {
  background: #e0e0e0 !important;
}
</style>
