<template>
  <div class="dashboard-layout min-h-screen flex flex-col bg-gray-100">
    <!-- 顶部导航 -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <slot name="header">
        <div class="w-full mx-auto py-4 px-2 sm:px-3 lg:px-4 flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">个人量化交易系统</h1>
          <slot name="header-right" />
        </div>
      </slot>
    </header>
    <div class="flex flex-1 w-full">
      <!-- 侧边栏 -->
      <aside class="hidden lg:block w-64 bg-white border-r border-gray-200 min-h-full">
        <slot name="sidebar" />
      </aside>
      <!-- 主内容区 -->
      <main class="flex-1 p-0">
        <slot />
      </main>
    </div>
    <!-- 底部状态栏 -->
    <footer class="bg-white py-2 border-t border-gray-200">
      <slot name="footer">
        <div class="text-center text-xs text-gray-400">© {{ new Date().getFullYear() }} QuantTrade | Powered by Vue3 & Flask</div>
      </slot>
    </footer>
  </div>
</template>

<script setup lang="ts">
// 仅结构，无业务逻辑
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  background: #f3f4f6;
  width: 100vw;
}
</style> 