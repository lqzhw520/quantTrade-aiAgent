<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-lg font-bold mb-4">策略回测</h2>
    
    <div class="mb-4">
      <label class="block text-gray-700 mb-2">股票代码</label>
      <el-input
        v-model="params.symbol"
        placeholder="例如: AAPL, TSLA"
        class="w-full"
        data-cy="strategy-symbol"
      />
    </div>
    
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">开始日期</label>
        <el-date-picker
          v-model="params.start_date"
          type="date"
          placeholder="选择开始日期"
          class="w-full"
          data-cy="strategy-start-date"
        />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">结束日期</label>
        <el-date-picker
          v-model="params.end_date"
          type="date"
          placeholder="选择结束日期"
          class="w-full"
          data-cy="strategy-end-date"
        />
      </div>
    </div>
    
    <div class="mb-4">
      <label class="block text-gray-700 mb-2">初始资金</label>
      <el-input-number 
        v-model="params.initial_capital" 
        :min="1000" 
        :step="10000"
        class="w-full"
        data-cy="strategy-capital"
      />
    </div>
    
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">短期 MA</label>
        <el-input-number 
          v-model="params.short_window" 
          :min="5" 
          :max="params.long_window" 
          :step="5"
          class="w-full"
          data-cy="strategy-short-ma"
        />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">长期 MA</label>
        <el-input-number 
          v-model="params.long_window" 
          :min="params.short_window" 
          :step="5"
          class="w-full"
          data-cy="strategy-long-ma"
        />
      </div>
    </div>
    
    <el-button 
      type="primary" 
      @click="submitBacktest" 
      :disabled="isLoading || !isFormValid"
      :loading="isLoading"
      class="w-full mt-4 mb-2"
      data-cy="run-backtest-btn"
    >
      {{ isLoading ? '回测中...' : '运行策略回测' }}
    </el-button>
    
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="mt-4"
      data-cy="strategy-error"
    />
    
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { apiService } from '../services/api';

const props = defineProps({});
const emit = defineEmits(['backtestCompleted']);

// 回测参数
const params = ref({
  strategy_name: 'ma_cross',
  symbol: '',  // 不设默认值，由用户选择
  start_date: formatDate(new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)),  // 默认90天前
  end_date: formatDate(new Date()),
  initial_capital: 100000,
  short_window: 20,
  long_window: 50,
});

// 状态管理
const isLoading = ref(false);
const error = ref('');

// 添加表单验证计算属性
const isFormValid = computed(() => {
  return params.value.symbol && 
         params.value.start_date && 
         params.value.end_date && 
         params.value.initial_capital >= 1000 &&
         params.value.short_window >= 5 &&
         params.value.long_window > params.value.short_window;
});

// 格式化日期为 YYYY-MM-DD
function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

// 应用预设模板
const applyTemplate = (type: string) => {
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
  // 参数验证
  if (!params.value.symbol) {
    error.value = '请选择股票';
    return;
  }

  if (params.value.short_window >= params.value.long_window) {
    error.value = '短期MA窗口必须小于长期MA窗口';
    return;
  }

  // 日期验证
  const start = new Date(params.value.start_date);
  const end = new Date(params.value.end_date);
  const now = new Date();

  if (start > end) {
    error.value = '开始日期不能晚于结束日期';
    return;
  }

  if (end > now) {
    error.value = '结束日期不能晚于今天';
    return;
  }

  if (params.value.initial_capital <= 0) {
    error.value = '初始资金必须大于0';
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

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-date-editor) {
  width: 100%;
}
</style> 