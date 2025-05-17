import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import AnalysisPanel from './AnalysisPanel.vue';

describe('AnalysisPanel', () => {
  it('渲染标题和静态内容', () => {
    const wrapper = mount(AnalysisPanel);
    expect(wrapper.text()).toContain('分析面板');
    expect(wrapper.text()).toContain('策略回测');
    expect(wrapper.text()).toContain('绩效分析');
  });
}); 