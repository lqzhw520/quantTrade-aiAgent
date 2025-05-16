<template>
  <div>
    <el-form-item label="选择股票">
      <el-select
        v-model="selectedCode"
        filterable
        remote
        clearable
        :remote-method="onSearch"
        :loading="loading"
        placeholder="请输入名称或代码搜索"
        @change="onStockSelect"
        style="width: 320px"
        data-cy="stock-select"
        @focus="onSearch('')"
        @visible-change="onDropdownVisibleChange"
      >
        <el-option
          v-for="item in filteredStocks"
          :key="item.ts_code"
          :label="`${item.name} (${item.ts_code})`"
          :value="item.ts_code"
        />
      </el-select>
    </el-form-item>
    
    <el-form-item label="开始日期" style="margin-top: 8px;">
      <el-date-picker
        v-model="startDate"
        type="date"
        placeholder="选择开始日期"
        :disabled-date="disabledDate"
        format="YYYY-MM-DD"
        style="width: 320px"
        @change="onDateChange"
        data-cy="start-date"
      />
    </el-form-item>
    
    <el-form-item label="结束日期" style="margin-top: 8px;">
      <el-date-picker
        v-model="endDate"
        type="date"
        placeholder="选择结束日期"
        :disabled-date="disabledDate"
        format="YYYY-MM-DD"
        style="width: 320px"
        @change="onDateChange"
        data-cy="end-date"
      />
    </el-form-item>
    
    <el-alert v-if="error" :title="error" type="error" show-icon style="margin-top: 8px;" />
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
const selectedCode = ref<string | null>(null);

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
const onStockSelect = (code: string) => {
  if (code && startDate.value && endDate.value) {
    emitSelection(code, [startDate.value, endDate.value]);
  }
};

const onDateChange = () => {
  if (!startDate.value || !endDate.value) {
    console.log('[StockSelector] onDateChange: 缺少日期', startDate.value, endDate.value);
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
    console.log('[StockSelector] onDateChange: start 非法', start);
    return;
  }
  if (!(end instanceof Date) || isNaN(end.getTime())) {
    console.log('[StockSelector] onDateChange: end 非法', end);
    return;
  }

  // 确保开始日期不晚于结束日期
  if (start > end) {
    error.value = '开始日期不能晚于结束日期';
    console.log('[StockSelector] onDateChange: 开始日期晚于结束日期', start, end);
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
  if (selectedCode.value) {
    emitSelection(selectedCode.value, [start, end]);
  }
};

const emitSelection = (code: string, dates: [Date, Date]) => {
  console.log('[StockSelector] emitSelection', code, dates);
  emit('select', code, dates);
};

// 远程搜索方法
const onSearch = (query: string) => {
  if (!query) {
    filteredStocks.value = stocks.value;
    console.log('[StockSelector] onSearch: query为空, filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
    return;
  }
  const q = query.trim().toLowerCase();
  filteredStocks.value = stocks.value.filter(
    s => s.ts_code.toLowerCase().includes(q) || s.name.includes(query)
  );
  console.log('[StockSelector] onSearch: query', query, 'filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
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

const onDropdownVisibleChange = (visible: boolean) => {
  console.log('[StockSelector] 下拉面板可见:', visible, 'filteredStocks.length:', filteredStocks.value.length);
};

onMounted(() => {
  fetchStockList();
  setTimeout(() => {
    onSearch('');
    console.log('[StockSelector] onMounted: filteredStocks', filteredStocks.value.length, filteredStocks.value.slice(0, 3));
  }, 200);
});
</script>

<style scoped>
</style> 