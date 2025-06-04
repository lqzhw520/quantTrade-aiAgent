<template>
  <div class="chart-toolbar flex items-center gap-4 bg-gray-50 px-4 py-2 rounded-t-lg border-b border-gray-200">
    <button class="btn" data-cy="add-indicator" @click="showIndicatorSelector = true">技术指标</button>
    <button class="btn" data-cy="drawing-tool" @click="showDrawingToolSelector = true">绘图工具</button>
    <el-select v-model="chartType" placeholder="图表类型" class="w-32" data-cy="chart-type-select">
      <el-option v-for="type in chartTypes" :key="type.value" :label="type.label" :value="type.value" :data-cy="`chart-type-${type.value}`" />
    </el-select>
    <button class="btn" data-cy="fullscreen">全屏</button>
    <button class="btn" data-cy="reset">重置</button>
    <IndicatorSelector v-model="showIndicatorSelector" @confirm="onIndicatorConfirm" />
    <DrawingToolSelector v-model="showDrawingToolSelector" @confirm="onDrawingToolConfirm" />
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import IndicatorSelector from './IndicatorSelector.vue';
import DrawingToolSelector from './DrawingToolSelector.vue';
const showIndicatorSelector = ref(false);
const showDrawingToolSelector = ref(false);
const chartType = ref('kline');
const chartTypes = [
  { label: 'K线', value: 'kline' },
  { label: '折线', value: 'line' },
  { label: '面积', value: 'area' },
];
function onIndicatorConfirm(selected: string[]) {
  // 这里后续 emit 给父组件
  // emit('update:indicators', selected)
  // 先打印
  console.log('选中的指标:', selected);
}
function onDrawingToolConfirm(selected: string) {
  // 这里后续 emit 给父组件
  // emit('update:drawingTool', selected)
  // 先打印
  console.log('选中的绘图工具:', selected);
}
</script>
<style scoped>
.chart-toolbar {
  min-height: 48px;
}
.btn {
  @apply px-3 py-1 rounded bg-blue-500 text-white text-sm hover:bg-blue-600 transition;
}
</style> 