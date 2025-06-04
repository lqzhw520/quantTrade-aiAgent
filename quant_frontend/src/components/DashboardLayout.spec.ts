import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import DashboardLayout from './DashboardLayout.vue';

describe('DashboardLayout', () => {
  it('渲染主布局和插槽内容', () => {
    const wrapper = mount(DashboardLayout, {
      slots: {
        header: '<div data-cy="header">Header</div>',
        sidebar: '<div data-cy="sidebar">Sidebar</div>',
        default: '<div data-cy="main">MainContent</div>',
        footer: '<div data-cy="footer">Footer</div>'
      }
    });
    expect(wrapper.find('[data-cy=header]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=sidebar]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=main]').exists()).toBe(true);
    expect(wrapper.find('[data-cy=footer]').exists()).toBe(true);
  });
}); 