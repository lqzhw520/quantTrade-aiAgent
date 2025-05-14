<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">API 测试</h2>
    
    <!-- 历史数据测试 -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">历史数据测试</h3>
      <div class="flex gap-2 mb-2">
        <input v-model="historicalParams.symbol" placeholder="股票代码" class="border p-2 rounded" />
        <input v-model="historicalParams.start_date" type="date" class="border p-2 rounded" />
        <input v-model="historicalParams.end_date" type="date" class="border p-2 rounded" />
        <button @click="fetchHistoricalData" class="bg-blue-500 text-white px-4 py-2 rounded">
          获取历史数据
        </button>
      </div>
      <div v-if="historicalData" class="mt-2">
        <p>数据点数量: {{ historicalData.dates.length }}</p>
        <p>最新收盘价: {{ historicalData.close_prices[historicalData.close_prices.length - 1] }}</p>
      </div>
    </div>

    <!-- 最新价格测试 -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">最新价格测试</h3>
      <div class="flex gap-2 mb-2">
        <input v-model="latestPriceSymbol" placeholder="股票代码" class="border p-2 rounded" />
        <button @click="fetchLatestPrice" class="bg-blue-500 text-white px-4 py-2 rounded">
          获取最新价格
        </button>
      </div>
      <div v-if="latestPrice" class="mt-2">
        <p>价格: {{ latestPrice.price }}</p>
        <p>时间: {{ latestPrice.timestamp }}</p>
      </div>
    </div>

    <!-- 回测测试 -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2">回测测试</h3>
      <div class="grid grid-cols-2 gap-4 mb-2">
        <input v-model="backtestParams.symbol" placeholder="股票代码" class="border p-2 rounded" />
        <input v-model="backtestParams.start_date" type="date" class="border p-2 rounded" />
        <input v-model="backtestParams.end_date" type="date" class="border p-2 rounded" />
        <input v-model.number="backtestParams.initial_capital" type="number" placeholder="初始资金" class="border p-2 rounded" />
        <input v-model.number="backtestParams.short_window" type="number" placeholder="短期窗口" class="border p-2 rounded" />
        <input v-model.number="backtestParams.long_window" type="number" placeholder="长期窗口" class="border p-2 rounded" />
      </div>
      <button @click="runBacktest" class="bg-blue-500 text-white px-4 py-2 rounded">
        执行回测
      </button>
      <div v-if="backtestResult" class="mt-2">
        <p>总收益率: {{ (backtestResult.returns * 100).toFixed(2) }}%</p>
        <p>交易次数: {{ backtestResult.trades.length }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { apiService } from '../services/api';
import type { HistoricalDataParams, HistoricalData, BacktestParams, BacktestResult } from '../services/api';

// 历史数据测试
const historicalParams = ref<HistoricalDataParams>({
  symbol: 'TSLA',
  start_date: '2023-01-01',
  end_date: '2023-12-31'
});
const historicalData = ref<HistoricalData | null>(null);

const fetchHistoricalData = async () => {
  try {
    historicalData.value = await apiService.getHistoricalData(historicalParams.value);
  } catch (error) {
    console.error('获取历史数据失败:', error);
  }
};

// 最新价格测试
const latestPriceSymbol = ref('TSLA');
const latestPrice = ref<{ price: number; timestamp: string } | null>(null);

const fetchLatestPrice = async () => {
  try {
    latestPrice.value = await apiService.getLatestPrice(latestPriceSymbol.value);
  } catch (error) {
    console.error('获取最新价格失败:', error);
  }
};

// 回测测试
const backtestParams = ref<BacktestParams>({
  strategy_name: 'ma_cross',
  symbol: 'TSLA',
  start_date: '2023-01-01',
  end_date: '2023-12-31',
  initial_capital: 100000,
  short_window: 5,
  long_window: 20
});
const backtestResult = ref<BacktestResult | null>(null);

const runBacktest = async () => {
  try {
    backtestResult.value = await apiService.runBacktest(backtestParams.value);
  } catch (error) {
    console.error('执行回测失败:', error);
  }
};
</script> 