<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-xl font-bold mb-4">策略回测</h2>
    
    <form @submit.prevent="submitBacktest" class="space-y-4">
      <!-- 股票代码 -->
      <div class="flex flex-col">
        <label for="symbol" class="text-sm font-medium text-gray-700 mb-1">股票代码</label>
        <input 
          id="symbol" 
          type="text" 
          v-model="params.symbol"
          required
          class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="例如：AAPL, TSLA"
        />
      </div>
      
      <!-- 日期范围 -->
      <div class="space-y-3">
        <div class="flex flex-col">
          <label for="start_date" class="text-sm font-medium text-gray-700 mb-1">开始日期</label>
          <input 
            id="start_date" 
            type="date" 
            v-model="params.start_date"
            required
            class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="flex flex-col">
          <label for="end_date" class="text-sm font-medium text-gray-700 mb-1">结束日期</label>
          <input 
            id="end_date" 
            type="date" 
            v-model="params.end_date"
            required
            class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
      
      <!-- 初始资金 -->
      <div class="flex flex-col">
        <label for="initial_capital" class="text-sm font-medium text-gray-700 mb-1">初始资金</label>
        <input 
          id="initial_capital" 
          type="number" 
          v-model.number="params.initial_capital"
          required
          min="1000"
          class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      
      <!-- 移动平均窗口 -->
      <div class="space-y-3">
        <div class="flex flex-col">
          <label for="short_window" class="text-sm font-medium text-gray-700 mb-1">短期 MA</label>
          <div class="flex items-center">
            <input 
              id="short_window" 
              type="number" 
              v-model.number="params.short_window"
              required
              min="5"
              max="50"
              class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1"
            />
            <span class="ml-2 text-gray-500 text-sm">天</span>
          </div>
        </div>
        <div class="flex flex-col">
          <label for="long_window" class="text-sm font-medium text-gray-700 mb-1">长期 MA</label>
          <div class="flex items-center">
            <input 
              id="long_window" 
              type="number" 
              v-model.number="params.long_window"
              required
              min="20"
              max="200"
              class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 flex-1"
            />
            <span class="ml-2 text-gray-500 text-sm">天</span>
          </div>
        </div>
      </div>
      
      <!-- 提交按钮 -->
      <button 
        type="submit" 
        :disabled="isLoading"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md disabled:bg-blue-300 disabled:cursor-not-allowed"
      >
        {{ isLoading ? '正在回测...' : '运行回测' }}
      </button>
      
      <!-- 错误信息显示 -->
      <div v-if="error" class="p-3 bg-red-100 text-red-700 rounded-md">
        {{ error }}
      </div>
      
      <!-- 预设模板选择 -->
      <div class="mt-4">
        <h3 class="text-sm font-medium text-gray-700 mb-2">预设策略模板</h3>
        <div class="grid grid-cols-2 gap-2">
          <button 
            type="button"
            @click="applyTemplate('conservative')"
            class="text-left p-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50"
          >
            保守型 (长期)
          </button>
          <button 
            type="button"
            @click="applyTemplate('aggressive')"
            class="text-left p-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50"
          >
            激进型 (短期)
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { apiService } from '../services/api';

const props = defineProps({});
const emit = defineEmits(['backtestCompleted']);

// 回测参数
const params = ref({
  strategy_name: 'ma_cross', // 固定为 ma_cross
  symbol: 'TSLA',
  start_date: '2023-01-01',
  end_date: '2023-12-31',
  initial_capital: 100000,
  short_window: 20,
  long_window: 50,
});

// 状态管理
const isLoading = ref(false);
const error = ref('');

// 应用预设模板
const applyTemplate = (type) => {
  if (type === 'conservative') {
    params.value = {
      ...params.value,
      short_window: 30,
      long_window: 90,
      initial_capital: 200000
    };
  } else if (type === 'aggressive') {
    params.value = {
      ...params.value,
      short_window: 10,
      long_window: 30,
      initial_capital: 50000
    };
  }
};

// 提交回测请求
const submitBacktest = async () => {
  // 简单的前端表单验证
  if (params.value.short_window >= params.value.long_window) {
    error.value = '短期MA窗口必须小于长期MA窗口';
    return;
  }

  isLoading.value = true;
  error.value = '';
  
  try {
    console.log('发送回测请求，参数:', params.value);
    const results = await apiService.runBacktest(params.value);
    console.log('回测结果:', results);
    emit('backtestCompleted', results);
  } catch (err: any) {
    console.error('回测错误详情:', err);
    if (err.response) {
      console.error('服务器响应:', err.response.status, err.response.data);
      error.value = `回测失败: ${err.response.data?.error || err.response.statusText}`;
    } else if (err.request) {
      console.error('无响应:', err.request);
      error.value = '服务器无响应，请检查网络连接';
    } else {
      error.value = err instanceof Error ? err.message : '回测失败，请稍后重试';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type=number] {
  -moz-appearance: textfield;
}
</style> 