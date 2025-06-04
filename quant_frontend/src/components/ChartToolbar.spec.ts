import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import ChartToolbar from './ChartToolbar.vue';

describe('ChartToolbar', () => {
  it('渲染所有按钮和下拉菜单', () => {
    const wrapper = mount(ChartToolbar);
    expect(wrapper.find('[data-cy=add-indicator]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=drawing-tool]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=chart-type-select]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=fullscreen]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=reset]').exists()).toBe(true);
  });

  it('点击技术指标按钮弹出 IndicatorSelector', async () => {
    const wrapper = mount(ChartToolbar);
    await wrapper.find('[data-cy=add-indicator]').trigger('click');
    expect(wrapper.find('[data-cy=indicator-selector-dialog]').exists()).toBe(true);
  });

  it('点击绘图工具按钮弹出 DrawingToolSelector', async () => {
    const wrapper = mount(ChartToolbar);
    await wrapper.find('[data-cy=drawing-tool]').trigger('click');
    expect(wrapper.find('[data-cy=drawing-tool-selector-dialog]').exists()).toBe(true);
  });
}); 