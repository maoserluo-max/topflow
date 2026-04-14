<template>
  <div class="h-screen flex bg-gray-950 overflow-hidden">
    <!-- 侧边栏 -->
    <aside class="w-64 flex-shrink-0 flex flex-col border-r border-white/5 bg-gray-950/95 backdrop-blur-xl relative">
      <!-- Logo 区域 -->
      <div class="p-6 border-b border-white/5">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-cyber-purple flex items-center justify-center shadow-lg shadow-primary-500/30">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-bold gradient-text">TopFlow</h1>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest">达人营销管理</p>
          </div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 py-6 px-4 space-y-1 overflow-y-auto scrollbar-hide">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item group"
          :class="{ 'active': $route.path === item.path }"
        >
          <component :is="item.icon" class="w-5 h-5 transition-transform duration-200 group-hover:scale-110" />
          <span>{{ item.label }}</span>
          <span
            v-if="$route.path === item.path"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-full bg-gradient-to-b from-cyber-blue to-cyber-purple"
          ></span>
        </router-link>
      </nav>

      <!-- 底部信息 -->
      <div class="p-4 border-t border-white/5">
        <div class="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.02]">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-medium text-gray-300 truncate">系统运行中</p>
            <p class="text-[10px] text-gray-600">v2.0.0</p>
          </div>
        </div>
      </div>

      <!-- 装饰性光晕 -->
      <div class="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-primary-500/5 to-transparent pointer-events-none"></div>
    </aside>

    <!-- 主内容区 -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- 顶部导航栏 -->
      <header class="h-16 px-8 flex items-center justify-between border-b border-white/5 bg-gray-950/80 backdrop-blur-xl sticky top-0 z-40">
        <!-- 左侧：面包屑导航 -->
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 text-sm">
            <router-link to="/" class="text-gray-500 hover:text-gray-300 transition-colors">首页</router-link>
            <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="text-white font-medium">{{ currentTitle }}</span>
          </div>
        </div>

        <!-- 右侧：用户信息 -->
        <div class="flex items-center gap-4">
          <!-- 状态指示器 -->
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-xs text-emerald-400 font-medium">在线</span>
          </div>

          <!-- 用户下拉菜单 -->
          <div class="relative group">
            <button class="flex items-center gap-3 px-4 py-2 rounded-xl hover:bg-white/5 transition-all duration-200">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-cyber-purple flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-primary-500/20">
                {{ (userStore.user?.full_name || userStore.user?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div class="text-left hidden sm:block">
                <p class="text-sm font-medium text-white">{{ userStore.user?.full_name || userStore.user?.username }}</p>
              </div>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider"
                :class="getRoleClass(userStore.user?.role)"
              >
                {{ getRoleName(userStore.user?.role) }}
              </span>
              <svg class="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- 下拉菜单内容 -->
            <div class="absolute right-0 mt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 translate-y-2 group-hover:translate-y-0">
              <div class="glass-card p-2 space-y-1">
                <button
                  @click="handleLogout"
                  class="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- 页面内容区域 -->
      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()

const currentTitle = computed(() => route.meta.title || '仪表盘')

const DashboardIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
])

const VideoIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
])

const UserIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' })
])

const LogsIcon = () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' })
])

const menuItems = computed(() => {
  const baseItems = [
    { path: '/dashboard', label: '数据总览', icon: DashboardIcon },
    { path: '/videos', label: '视频管理', icon: VideoIcon },
  ]

  if (userStore.isAdmin) {
    baseItems.push(
      { path: '/users', label: '用户管理', icon: UserIcon },
      { path: '/logs', label: '操作日志', icon: LogsIcon }
    )
  }

  return baseItems
})

function getRoleType(role) {
  const types = { admin: 'danger', manager: 'warning', user: 'info' }
  return types[role] || 'info'
}

function getRoleName(role) {
  const names = { admin: '管理员', manager: '经理', user: '用户' }
  return names[role] || role
}

function getRoleClass(role) {
  const classes = {
    admin: 'bg-red-500/10 text-red-400',
    manager: 'bg-amber-500/10 text-amber-400',
    user: 'bg-blue-500/10 text-blue-400'
  }
  return classes[role] || 'bg-gray-500/10 text-gray-400'
}

function handleLogout() {
  userStore.logout()
  window.location.href = '/login'
}
</script>

<style scoped>
.nav-item {
  @apply relative flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-200 cursor-pointer;
}

.nav-item.active {
  @apply text-white bg-white/5;
}
</style>