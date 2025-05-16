import { mount } from '@vue/test-utils';
import IndicatorChart from './IndicatorChart.vue';
import { nextTick } from 'vue';
import { vi, describe, it, expect } from 'vitest';

// mock ECharts
vi.mock('echarts/core', () => ({
  init: () => ({
    setOption: vi.fn(),
    dispose: vi.fn(),
    resize: vi.fn(),
  }),
  use: vi.fn(),
}));

// mock canvas
window.HTMLCanvasElement.prototype.getContext = function () {
  return null;
};

global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

describe('IndicatorChart.vue', () => {
  const mockIndicators = {
    dates: ['20240101', '20240102', '20240103'],
    open: [10, 11, 12],
    close: [11, 12, 13],
    low: [9, 10, 11],
    high: [12, 13, 14],
    volume: [100, 200, 300],
    obv: [100, 200, 300],
    vma_5: [1000, 1100, 1200],
    vr: [1.1, 1.2, 1.3],
    mfi: [50, 60, 70],
    pma_5: [11, 12, 13],
    pma_20: [10.5, 11.5, 12.5]
  };

  it('渲染空数据提示', () => {
    const wrapper = mount(IndicatorChart, { props: { indicators: { dates: [], volume: [], close: [] } } });
    expect(wrapper.find('.chart-area').exists()).toBe(true);
    expect(wrapper.find('.no-data-message').exists()).toBe(true);
    expect(wrapper.text()).toContain('暂无数据');
  });

  it('渲染K线+MA图表', async () => {
    const wrapper = mount(IndicatorChart, { props: { indicators: mockIndicators } });
    await nextTick();
    expect(wrapper.find('.chart-area').exists()).toBe(true);
    expect(wrapper.find('.has-data').exists()).toBe(true);
  });
}); 