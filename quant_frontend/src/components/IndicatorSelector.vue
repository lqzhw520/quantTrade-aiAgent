<template>
  <el-dialog v-model="visible" title="选择技术指标" width="400px" @close="onCancel" data-cy="indicator-selector-dialog">
    <el-checkbox-group v-model="selected" data-cy="indicator-checkbox-group">
      <el-checkbox v-for="item in indicators" :key="item" :value="item" :data-cy="`indicator-${item}`">
        {{ item }}
      </el-checkbox>
    </el-checkbox-group>
    <template #footer>
      <el-button @click="onCancel" data-cy="indicator-cancel">取消</el-button>
      <el-button type="primary" @click="onConfirm" data-cy="indicator-confirm">确定</el-button>
    </template>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, defineEmits, defineProps } from 'vue';
const props = defineProps<{
  modelValue: boolean;
  value?: string[];
}>();
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);
const visible = ref(props.modelValue);
const indicators = [
  'MA', 'EMA', 'MACD', 'BOLL', 'RSI', 'OBV', 'VMA', 'VR', 'MFI', 'PMA'
];
const selected = ref<string[]>(props.value || []);
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