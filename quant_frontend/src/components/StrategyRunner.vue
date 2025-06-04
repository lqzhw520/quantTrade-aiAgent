<template>
  <div class="p-4 bg-white rounded-lg shadow">
    <h2 class="text-lg font-bold mb-4">策略回测</h2>
    
    <div class="mb-4">
      <label class="block text-gray-700 mb-2">回测引擎</label>
      <el-radio-group v-model="engineType" class="w-full">
        <el-radio label="default" border data-cy="engine-default">默认引擎</el-radio>
        <el-radio label="backtrader" border data-cy="engine-backtrader">Backtrader</el-radio>
      </el-radio-group>
      <div class="text-xs text-gray-500 mt-1" v-if="engineType === 'backtrader'">
        使用 Backtrader 提供更专业的回测支持
      </div>
    </div>
    
    <div class="mb-4">
      <label class="block text-gray-700 mb-2">策略类型</label>
      <el-select 
        v-model="params.strategy_name" 
        class="w-full" 
        placeholder="选择策略类型"
        data-cy="strategy-type"
        @change="onStrategyChange"
      >
        <el-option label="均线交叉策略" value="ma_cross" data-cy="strategy-ma-cross" />
        <el-option label="交易量突破策略" value="volume_breakout" data-cy="strategy-volume-breakout" />
      </el-select>
      <div class="text-xs text-gray-500 mt-1">
        <span v-if="params.strategy_name === 'ma_cross'">短期均线穿过长期均线时产生交易信号</span>
        <span v-else-if="params.strategy_name === 'volume_breakout'">交易量放大且价格突破时产生交易信号</span>
      </div>
    </div>
    
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
    
    <!-- 均线交叉策略参数 -->
    <div v-if="params.strategy_name === 'ma_cross'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
    
    <!-- 交易量突破策略参数 -->
    <div v-if="params.strategy_name === 'volume_breakout'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">交易量窗口</label>
        <el-input-number 
          v-model="volumeBreakoutParams.volume_window" 
          :min="5" 
          :step="5"
          class="w-full"
          data-cy="strategy-volume-window"
        />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">放量倍数阈值</label>
        <el-input-number 
          v-model="volumeBreakoutParams.volume_mult" 
          :min="1.1" 
          :step="0.1"
          :precision="1"
          class="w-full"
          data-cy="strategy-volume-mult"
        />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">价格变化阈值(%)</label>
        <el-input-number 
          v-model="volumeBreakoutParams.price_change_threshold" 
          :min="0.5" 
          :step="0.5"
          :precision="1"
          class="w-full"
          data-cy="strategy-price-threshold"
        />
      </div>
      
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">回看天数</label>
        <el-input-number 
          v-model="volumeBreakoutParams.lookback_days" 
          :min="1" 
          :step="1"
          class="w-full"
          data-cy="strategy-lookback-days"
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
        <button 
          type="button"
          @click="applyTemplate('volume_breakout')"
          class="text-left p-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50"
        >
          大成交量突破
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { apiService, type BacktestEngineType } from '../services/api';

const props = defineProps({});
const emit = defineEmits(['backtestCompleted']);

// 回测引擎类型
const engineType = ref<BacktestEngineType>('default');

// 回测参数
const params = ref({
  strategy_name: 'ma_cross',
  symbol: '',  // 不设默认值，由用户选择
  start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),  // 默认90天前，使用Date对象
  end_date: new Date(),  // 使用Date对象
  initial_capital: 100000,
  short_window: 20,
  long_window: 50,
});

// 交易量突破策略专用参数
const volumeBreakoutParams = reactive({
  volume_window: 20,
  volume_mult: 2.0,
  price_change_threshold: 2.0,
  lookback_days: 3
});

// 状态管理
const isLoading = ref(false);
const error = ref('');

// 监听策略变化
const onStrategyChange = (value: string) => {
  // 清除错误信息
  error.value = '';
  
  // 根据策略类型重置表单
  if (value === 'ma_cross') {
    // 如果是切换回均线策略，不需要特殊处理
  } else if (value === 'volume_breakout') {
    // 切换到交易量突破策略
  }
};

// 添加表单验证计算属性
const isFormValid = computed(() => {
  // 通用验证
  const baseValid = params.value.symbol && 
                    params.value.start_date && 
                    params.value.end_date && 
                    params.value.initial_capital >= 1000;
  
  // 根据策略类型添加特定验证
  if (params.value.strategy_name === 'ma_cross') {
    return baseValid &&
           params.value.short_window >= 5 &&
           params.value.long_window > params.value.short_window;
  } 
  else if (params.value.strategy_name === 'volume_breakout') {
    return baseValid &&
           volumeBreakoutParams.volume_window >= 5 &&
           volumeBreakoutParams.volume_mult >= 1.1 &&
           volumeBreakoutParams.price_change_threshold >= 0.5 &&
           volumeBreakoutParams.lookback_days >= 1;
  }
  
  return baseValid;
});

// 格式化日期为 YYYY-MM-DD
function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

// 应用预设模板
const applyTemplate = (type: string) => {
  if (type === 'conservative') {
    params.value.strategy_name = 'ma_cross';
    params.value.short_window = 30;
    params.value.long_window = 90;
    params.value.initial_capital = 200000;
  } else if (type === 'aggressive') {
    params.value.strategy_name = 'ma_cross';
    params.value.short_window = 10;
    params.value.long_window = 30;
    params.value.initial_capital = 50000;
  } else if (type === 'volume_breakout') {
    params.value.strategy_name = 'volume_breakout';
    volumeBreakoutParams.volume_window = 15;
    volumeBreakoutParams.volume_mult = 2.5;
    volumeBreakoutParams.price_change_threshold = 3.0;
    volumeBreakoutParams.lookback_days = 2;
    params.value.initial_capital = 100000;
  }
};

// 准备请求参数
const prepareRequestParams = () => {
  const requestParams = { ...params.value };
  
  // 根据策略类型添加特定参数
  if (params.value.strategy_name === 'volume_breakout') {
    // 添加交易量突破特有参数
    Object.assign(requestParams, volumeBreakoutParams);
  }
  
  return requestParams;
};

// 提交回测请求
const submitBacktest = async () => {
  // 参数验证
  if (!params.value.symbol) {
    error.value = '请选择股票';
    return;
  }

  // 策略特定验证
  if (params.value.strategy_name === 'ma_cross' && params.value.short_window >= params.value.long_window) {
    error.value = '短期MA窗口必须小于长期MA窗口';
    return;
  }

  // 日期验证
  const start = params.value.start_date instanceof Date 
    ? params.value.start_date 
    : new Date(params.value.start_date);
  const end = params.value.end_date instanceof Date 
    ? params.value.end_date 
    : new Date(params.value.end_date);
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
    // 准备请求参数
    const requestParams = prepareRequestParams();
    
    console.log(`发送${engineType.value === 'backtrader' ? 'Backtrader' : '默认'}回测请求，参数:`, requestParams);
    const results = await apiService.runBacktest(requestParams, engineType.value);
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

:deep(.el-radio-group) {
  display: flex;
  gap: 10px;
}

:deep(.el-radio.is-bordered) {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0;
}
</style> 