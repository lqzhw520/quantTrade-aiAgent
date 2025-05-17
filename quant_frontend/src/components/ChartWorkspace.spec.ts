import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import ChartWorkspace from './ChartWorkspace.vue';

describe('ChartWorkspace', () => {
  it('渲染默认内容', () => {
    const wrapper = mount(ChartWorkspace);
    expect(wrapper.text()).toContain('主图表区');
  });

  it('渲染 slot 内容', () => {
    const wrapper = mount(ChartWorkspace, { slots: { default: '<div data-cy="custom">自定义内容</div>' } });
    expect(wrapper.find('[data-cy=custom]').exists()).toBe(true);
  });
}); 