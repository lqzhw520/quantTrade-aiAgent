# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).

## 端到端（E2E）测试

本项目推荐使用 [Cypress](https://www.cypress.io/) 进行前后端联调的自动化端到端测试。

### 安装 Cypress

```bash
cd quant_frontend
npm install cypress --save-dev
```

### 运行 Cypress 测试

```bash
npx cypress open
# 或
npx cypress run
```

### 测试用例建议
- 选股后自动选择日期区间（最大为今天），点击查询，断言后端返回数据并渲染图表。
- 日期选择器禁止未来日期，手动输入未来日期会被自动修正。
- 切换不同股票和日期区间，断言数据和图表联动。

测试脚本建议放在 `cypress/e2e/` 目录下。
