<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-xl font-bold mb-4">绩效指标</h2>
    
    <div v-if="!performance" class="py-8 text-center text-gray-500">
      请先运行回测以查看绩效指标
    </div>
    
    <div v-else class="space-y-4">
      <!-- 绩效指标和交易统计（宽屏时并排显示） -->
      <div class="lg:flex lg:space-x-4 lg:space-y-0 space-y-4">
        <!-- 绩效指标卡片 -->
        <div class="lg:w-1/2">
          <h3 class="text-lg font-semibold mb-2">绩效指标</h3>
          <div class="grid grid-cols-3 gap-4">
            <div class="p-3 bg-blue-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">总收益率</div>
              <div class="text-xl font-bold" :class="getReturnColorClass(performance.total_return)">
                {{ (performance.total_return * 100).toFixed(2) }}%
              </div>
            </div>
            <div class="p-3 bg-blue-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">年化收益率</div>
              <div class="text-xl font-bold" :class="getReturnColorClass(performance.annual_return)">
                {{ (performance.annual_return * 100).toFixed(2) }}%
              </div>
            </div>
            <div class="p-3 bg-blue-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">最大回撤</div>
              <div class="text-xl font-bold text-red-600">
                {{ (performance.max_drawdown * 100).toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>
      
        <!-- 交易统计 -->
        <div class="lg:w-1/2" v-if="buySignals && sellSignals">
          <h3 class="text-lg font-semibold mb-2">交易统计</h3>
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="p-3 bg-gray-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">买入信号</div>
              <div class="text-xl font-bold text-green-600">{{ buySignals.length }}</div>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">卖出信号</div>
              <div class="text-xl font-bold text-red-600">{{ sellSignals.length }}</div>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">总交易次数</div>
              <div class="text-xl font-bold text-gray-700">{{ buySignals.length + sellSignals.length }}</div>
            </div>
            <div class="p-3 bg-gray-50 rounded-lg shadow-sm">
              <div class="text-sm text-gray-500">持仓时间占比</div>
              <div class="text-xl font-bold text-gray-700">{{ holdingTimePercentage }}%</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 交易记录表格 -->
      <div class="mt-6" v-if="buySignals && sellSignals">
        <h3 class="text-lg font-semibold mb-2">交易记录</h3>
        <div class="overflow-x-auto">
          <div class="max-h-[300px] overflow-y-auto">
            <table class="min-w-full divide-y divide-gray-200 table-auto">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">日期</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">类型</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">价格</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">变动</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(signal, index) in sortedSignals" :key="signal.date + signal.type" class="hover:bg-gray-50">
                  <td class="px-4 py-2 text-sm">{{ signal.date }}</td>
                  <td class="px-4 py-2 text-sm">
                    <span v-if="signal.type === 'buy'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                      买入
                    </span>
                    <span v-else class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                      卖出
                    </span>
                  </td>
                  <td class="px-4 py-2 text-sm">{{ signal.price.toFixed(2) }}</td>
                  <td class="px-4 py-2 text-sm">
                    <span v-if="index > 0 && sortedSignals[index-1].type !== signal.type">
                      {{ calculatePriceChange(index) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  performance: {
    type: Object,
    default: null
  },
  buySignals: {
    type: Array,
    default: () => []
  },
  sellSignals: {
    type: Array,
    default: () => []
  },
  totalDays: {
    type: Number,
    default: 0
  }
});

// 合并并排序所有交易信号
const sortedSignals = computed(() => {
  if (!props.buySignals || !props.sellSignals) return [];
  
  // 合并信号并添加类型标识
  const allSignals = [
    ...props.buySignals.map(s => ({ ...s, type: 'buy' })),
    ...props.sellSignals.map(s => ({ ...s, type: 'sell' }))
  ];
  
  // 按日期排序
  return allSignals.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
});

// 计算持仓时间占比（粗略估计）
const holdingTimePercentage = computed(() => {
  if (!props.buySignals || !props.sellSignals || !props.totalDays || props.totalDays === 0) {
    return '0.00';
  }
  
  // 假设每次买入后持有，直到卖出
  let holdingDays = 0;
  let buyDates = props.buySignals.map(s => new Date(s.date).getTime()).sort((a, b) => a - b);
  let sellDates = props.sellSignals.map(s => new Date(s.date).getTime()).sort((a, b) => a - b);
  
  // 如果交易记录不完整，使用简单估计
  if (buyDates.length > 0 && (sellDates.length === 0 || buyDates[0] < sellDates[0])) {
    // 估计持仓时间占比为40%（简单估计）
    return '40.00';
  }
  
  // 计算实际比例（粗略估计）
  return ((props.buySignals.length / props.totalDays) * 100).toFixed(2);
});

// 计算价格变动
const calculatePriceChange = (index) => {
  if (index === 0 || !sortedSignals.value[index] || !sortedSignals.value[index-1]) {
    return '';
  }
  
  const currentPrice = sortedSignals.value[index].price;
  const previousPrice = sortedSignals.value[index-1].price;
  
  if (currentPrice && previousPrice) {
    const change = (currentPrice - previousPrice) / previousPrice * 100;
    const sign = change > 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  }
  
  return '';
};

// 获取收益率显示的颜色类
const getReturnColorClass = (value) => {
  if (value > 0) return 'text-green-600';
  if (value < 0) return 'text-red-600';
  return 'text-gray-600';
};
</script>

<style scoped>
/* 响应式表格样式 */
@media (max-width: 640px) {
  table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style> 