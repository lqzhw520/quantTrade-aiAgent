import { beforeAll } from 'vitest';
import ElementPlus from 'element-plus';
import { config } from '@vue/test-utils';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';

beforeAll(() => {
  config.global.plugins = config.global.plugins || [];
  config.global.plugins.push(ElementPlus);

  // 注册所有 Element Plus 图标组件
  config.global.components = config.global.components || {};
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    config.global.components[key] = component;
  }

  // mock/stub 关键 Element Plus 组件，消除警告
  const elComponents = [
    'el-select', 'el-option', 'el-form-item', 'el-date-picker', 'el-alert'
  ];
  config.global.stubs = config.global.stubs || {};
  elComponents.forEach(name => {
    config.global.stubs[name] = true;
  });
}); 