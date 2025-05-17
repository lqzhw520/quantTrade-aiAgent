import { shallowMount, flushPromises } from '@vue/test-utils';
import StockSelector from './StockSelector.vue';
import { nextTick } from 'vue';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// mock Element Plus 组件
vi.mock('element-plus', () => ({
  ElSelect: {
    template: '<select><slot /></select>'
  },
  ElOption: {
    template: '<option><slot /></option>'
  },
  ElFormItem: {
    template: '<div><slot /></div>'
  },
  ElAlert: {
    template: '<div><slot /></div>'
  },
  ElDatePicker: {
    template: '<input type="date" />'
  }
}));

// mock apiService
vi.mock('../services/api', () => ({
  apiService: {
    getStockList: vi.fn()
  }
}));

import { apiService } from '../services/api';

describe('StockSelector.vue', () => {
  const mockStocks = [
    { ts_code: '000001.SZ', name: '平安银行' },
    { ts_code: '000002.SZ', name: '万科A' }
  ];

  beforeEach(() => {
    (apiService.getStockList as any).mockReset();
  });

  it('加载后 filteredStocks 包含股票数据', async () => {
    (apiService.getStockList as any).mockResolvedValue(mockStocks);
    const wrapper = shallowMount(StockSelector);
    await flushPromises();
    // 直接断言 filteredStocks
    expect((wrapper.vm as any).filteredStocks.length).toBe(2);
    expect((wrapper.vm as any).filteredStocks[0].name).toBe('平安银行');
    expect((wrapper.vm as any).filteredStocks[1].ts_code).toBe('000002.SZ');
  });

  it('选择股票后 emit 事件', async () => {
    (apiService.getStockList as any).mockResolvedValue(mockStocks);
    const wrapper = shallowMount(StockSelector);
    await flushPromises();
    
    // 设置日期值
    (wrapper.vm as any).startDate = new Date('2025-01-01');
    (wrapper.vm as any).endDate = new Date('2025-01-15');
    
    // 使用 mockStocks[1].ts_code 代替硬编码
    const code = mockStocks[1].ts_code;
    (wrapper.vm as any).handleStockChange(code);
    await nextTick();
    
    expect(wrapper.emitted('select')).toBeTruthy();
    const args = wrapper.emitted('select')![0];
    expect(args[0]).toBe(code);
    expect(Array.isArray(args[1])).toBe(true);
    expect(args[1].length).toBe(2);
  });

  it('日期变更时如果已选择股票则触发更新', async () => {
    (apiService.getStockList as any).mockResolvedValue(mockStocks);
    const wrapper = shallowMount(StockSelector);
    await flushPromises();
    
    // 先选择股票
    const code = mockStocks[1].ts_code;
    (wrapper.vm as any).selectedStock = code;
    
    // 设置日期并触发变更
    (wrapper.vm as any).startDate = new Date('2025-01-01');
    (wrapper.vm as any).endDate = new Date('2025-01-15');
    (wrapper.vm as any).handleDateChange();
    await nextTick();
    
    expect(wrapper.emitted('select')).toBeTruthy();
    const args = wrapper.emitted('select')![0];
    expect(args[0]).toBe(code);
  });

  it('加载失败时 error 响应式数据有值', async () => {
    (apiService.getStockList as any).mockRejectedValue(new Error('网络错误'));
    const wrapper = shallowMount(StockSelector);
    await flushPromises();
    expect((wrapper.vm as any).error).toContain('网络错误');
  });
}); 