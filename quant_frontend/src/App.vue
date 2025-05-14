<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow">
      <div class="max-w-full mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold text-gray-900">个人量化交易系统</h1>
      </div>
    </header>
    <main>
      <div class="max-w-full mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <!-- 主布局 - 使用响应式多列布局 -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <!-- 策略回测面板 - 占左侧列 -->
          <div class="lg:col-span-1">
            <StrategyRunner @backtest-completed="handleBacktestResults" />
            
            <!-- WebSocket测试 -->
            <div class="p-4 bg-white rounded-lg shadow mt-6">
              <h2 class="text-xl font-bold mb-4">WebSocket测试</h2>
              <button 
                @click="sendTestMessage" 
                class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
              >
                发送测试消息
              </button>
              <div v-if="socketStatus" class="mt-2 text-sm">
                <p class="text-green-600" v-if="socketStatus === 'connected'">WebSocket已连接</p>
                <p class="text-red-600" v-else>WebSocket未连接</p>
              </div>
            </div>
          </div>
          
          <!-- 结果可视化区域 - 占右侧列 -->
          <div class="lg:col-span-3">
            <!-- 回测结果图表 -->
            <ResultsChart v-if="backtestResults" :results="backtestResults" />
            <div v-else class="p-4 bg-white rounded-lg shadow text-center text-gray-500 min-h-[200px] flex items-center justify-center">
              <p>运行策略后，图表将在此处显示</p>
            </div>
            
            <!-- 绩效指标 -->
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
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { initWebSocket, disconnectWebSocket, sendMessage, socket } from './config/websocket';
import StrategyRunner from './components/StrategyRunner.vue';
import ResultsChart from './components/ResultsChart.vue';
import PerformanceMetrics from './components/PerformanceMetrics.vue';

// WebSocket状态
const socketStatus = ref<string | null>(null);

// 组件挂载时初始化 WebSocket
onMounted(() => {
  initWebSocket();
  
  // 监听socket连接状态
  socket.on('connect', () => {
    socketStatus.value = 'connected';
  });
  
  socket.on('disconnect', () => {
    socketStatus.value = 'disconnected';
  });
});

// 组件卸载时断开 WebSocket
onUnmounted(() => {
  disconnectWebSocket();
});

// 回测结果
const backtestResults = ref(null);

// 处理回测结果
function handleBacktestResults(results) {
  console.log('回测结果:', results);
  backtestResults.value = results;
}

// 发送测试消息
function sendTestMessage() {
  sendMessage('client_event', { 
    message: '来自Vue客户端的测试消息', 
    timestamp: new Date().toISOString() 
  });
}
</script>

<style>
/* 全局样式 */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 响应式大屏幕优化 */
@media (min-width: 1280px) {
  .max-w-full {
    max-width: 1600px;
  }
}
</style>
