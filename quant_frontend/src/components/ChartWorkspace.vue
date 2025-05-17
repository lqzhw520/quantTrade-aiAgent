<template>
  <div class="chart-workspace bg-white rounded-lg shadow min-h-[500px] flex items-center justify-center">
    <slot>
      <span class="text-gray-400 text-lg">主图表区</span>
    </slot>
  </div>
</template>
<script setup lang="ts">
// 仅结构
</script>
<style scoped>
.chart-workspace {
  width: 100%;
  min-height: 500px;
  height: calc(100% - 48px); /* 减去工具栏高度 */
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  overflow: hidden;
}
</style> 