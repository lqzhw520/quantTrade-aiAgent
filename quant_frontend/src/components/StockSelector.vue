<template>
  <div>
    <div class="mb-4">
      <label class="block text-gray-700 mb-2">选择股票</label>
      <el-select
        v-model="selectedStock"
        filterable
        remote
        placeholder="请输入名称或代码"
        :remote-method="querySearch"
        :loading="loading"
        @change="handleStockChange"
        data-cy="stock-select"
        class="w-full"
      >
        <el-option
          v-for="item in filteredStocks"
          :key="item.ts_code"
          :label="`${item.name} (${item.ts_code})`"
          :value="item.ts_code"
          data-cy="stock-option"
        />
      </el-select>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">开始日期</label>
        <el-date-picker
          v-model="startDate"
          type="date"
          placeholder="选择开始日期"
          @change="handleDateChange"
          data-cy="start-date"
          class="w-full"
        />
      </div>
      <div class="mb-4">
        <label class="block text-gray-700 mb-2">结束日期</label>
        <el-date-picker
          v-model="endDate"
          type="date"
          placeholder="选择结束日期"
          @change="handleDateChange"
          data-cy="end-date"
          class="w-full"
        />
      </div>
    </div>
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="false"
      class="mb-4"
      data-cy="error-message"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { StockItem } from '../services/api';
import { apiService } from '../services/api';

const stocks = ref<StockItem[]>([]);
const filteredStocks = ref<StockItem[]>([]);
const loading = ref(false);
const error = ref('');
const selectedStock = ref<string | null>(null);

// 默认日期范围：最近7天
const today = new Date();
const defaultEnd = today;
const defaultStart = new Date();
defaultStart.setDate(today.getDate() - 7);

// 替换dateRange为独立的开始日期和结束日期
const startDate = ref<Date>(defaultStart);
const endDate = ref<Date>(defaultEnd);

function disabledDate(time: Date) {
  // 禁止选择未来日期
  return time.getTime() > today.getTime();
}

// 分离股票选择和日期变更事件
const handleStockChange = (code: string) => {
  if (code && startDate.value && endDate.value) {
    emitSelection(code, [startDate.value, endDate.value]);
  }
};

const handleDateChange = () => {
  if (!startDate.value || !endDate.value) {
    console.log('[StockSelector] handleDateChange: 缺少日期', startDate.value, endDate.value);
    return;
  }

  let start = startDate.value;
  let end = endDate.value;
  // 兼容字符串和Date
  if (typeof start === 'string') {
    start = new Date((start as string).replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'));
  }
  if (typeof end === 'string') {
    end = new Date((end as string).replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'));
  }
  if (!(start instanceof Date) || isNaN(start.getTime())) {
    console.log('[StockSelector] handleDateChange: start 非法', start);
    return;
  }
  if (!(end instanceof Date) || isNaN(end.getTime())) {
    console.log('[StockSelector] handleDateChange: end 非法', end);
    return;
  }

  // 确保开始日期不晚于结束日期
  if (start > end) {
    error.value = '开始日期不能晚于结束日期';
    console.log('[StockSelector] handleDateChange: 开始日期晚于结束日期', start, end);
    return;
  }

  // 确保不超过今天
  if (end.getTime() > today.getTime()) {
    end = new Date(today);
    endDate.value = end;
  }
  if (start.getTime() > today.getTime()) {
    start = new Date(today);
    startDate.value = start;
  }

  error.value = '';

  // 如果已选择股票，则触发更新
  if (selectedStock.value) {
    emitSelection(selectedStock.value, [start, end]);
  }
};

const emitSelection = (code: string, dates: [Date, Date]) => {
  console.log('[StockSelector] emitSelection', code, dates);
  emit('select', code, dates);
};

// 远程搜索方法
const querySearch = (query: string) => {
  if (!query) {
    filteredStocks.value = stocks.value;
    console.log('[StockSelector] querySearch: query为空, filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
    return;
  }
  const q = query.trim().toLowerCase();
  filteredStocks.value = stocks.value.filter(
    s => s.ts_code.toLowerCase().includes(q) || s.name.includes(query)
  );
  console.log('[StockSelector] querySearch: query', query, 'filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
};

const emit = defineEmits<{
  (e: 'select', code: string, dateRange: [Date, Date]): void;
}>();

const fetchStockList = async () => {
  loading.value = true;
  error.value = '';
  try {
    const list = await apiService.getStockList();
    stocks.value = list;
    filteredStocks.value = list;
    console.log('[StockSelector] fetchStockList: stocks', stocks.value.length, stocks.value.slice(0, 3));
    console.log('[StockSelector] fetchStockList: filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
  } catch (e: any) {
    error.value = e.message || '股票列表获取失败';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchStockList();
  setTimeout(() => {
    querySearch('');
    console.log('[StockSelector] onMounted: filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
  }, 200);
});
</script>

<style scoped>
:deep(.el-select) {
  width: 100%;
}
:deep(.el-date-editor) {
  width: 100%;
}
</style> 