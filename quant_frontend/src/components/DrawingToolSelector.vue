<template>
  <el-dialog v-model="visible" title="选择绘图工具" width="350px" @close="onCancel" data-cy="drawing-tool-selector-dialog">
    <el-radio-group v-model="selected" data-cy="drawing-tool-radio-group">
      <el-radio v-for="item in tools" :key="item.value" :value="item.value" :data-cy="`drawing-tool-${item.value}`">
        {{ item.label }}
      </el-radio>
    </el-radio-group>
    <template #footer>
      <el-button @click="onCancel" data-cy="drawing-tool-cancel">取消</el-button>
      <el-button type="primary" @click="onConfirm" data-cy="drawing-tool-confirm">确定</el-button>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, defineEmits, defineProps } from 'vue';
const props = defineProps<{
  modelValue: boolean;
  value?: string;
}>();
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);
const visible = ref(props.modelValue);
const tools = [
  { label: '趋势线', value: 'trendline' },
  { label: '水平线', value: 'horizontalline' },
  { label: '价格标记', value: 'pricetag' },
  { label: '文本', value: 'text' }
];
const selected = ref<string>(props.value || 'trendline');
watch(() => props.modelValue, v => visible.value = v);
function onConfirm() {
  emit('confirm', selected.value);
  emit('update:modelValue', false);
}
function onCancel() {
  emit('cancel');
  emit('update:modelValue', false);
}
</script> 