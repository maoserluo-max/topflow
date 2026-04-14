<template>
  <div class="h-screen flex overflow-hidden transition-colors duration-300 dark:bg-gray-950 bg-gray-100">
    <aside
      class="flex-shrink-0 flex flex-col backdrop-blur-xl relative transition-all duration-300 dark:border-r dark:border-white/5 dark:bg-gray-950/95 border-r border-gray-200/80 bg-white/95"
      :class="sidebarCollapsed ? 'w-[72px]' : 'w-64'"
    >
      <div class="p-6 dark:border-b dark:border-white/5 border-b border-gray-200">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 flex-shrink-0 rounded-xl bg-gradient-to-br from-primary-500 to-cyber-purple flex items-center justify-center shadow-lg shadow-primary-500/30">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div v-show="!sidebarCollapsed" class="overflow-hidden">
            <h1 class="text-lg font-bold gradient-text whitespace-nowrap">TopFlow</h1>
            <p class="text-[10px] uppercase tracking-widest dark:text-gray-500 text-gray-400 whitespace-nowrap">达人营销管理</p>
          </div>
        </div>
      </div>

      <nav class="flex-1 py-6 px-4 space-y-1 overflow-y-auto scrollbar-hide">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item group"
          :class="{ 'active': $route.path === item.path, 'justify-center': sidebarCollapsed }"
          :title="sidebarCollapsed ? item.label : ''"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0 transition-transform duration-200 group-hover:scale-110" />
          <span v-show="!sidebarCollapsed">{{ item.label }}</span>
          <span
            v-if="$route.path === item.path && !sidebarCollapsed"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-full bg-gradient-to-b from-cyber-blue to-cyber-purple"
          ></span>
        </router-link>
      </nav>

      <div v-show="!sidebarCollapsed" class="p-4 dark:border-t dark:border-white/5 border-t border-gray-200">
        <div class="flex items-center gap-3 px-3 py-2.5 rounded-xl dark:bg-white/[0.02] bg-gray-100">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center">
            <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-medium truncate dark:text-gray-300 text-gray-700">系统运行中</p>
            <p class="text-[10px] dark:text-gray-600 text-gray-400">v2.0.0</p>
          </div>
        </div>
      </div>

      <div v-if="themeStore.isDark" class="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-primary-500/5 to-transparent pointer-events-none"></div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-16 px-8 flex items-center justify-between backdrop-blur-xl sticky top-0 z-40 transition-colors duration-300 dark:border-b dark:border-white/5 dark:bg-gray-950/80 border-b border-gray-200 bg-white/90">
        <div class="flex items-center gap-4">
          <button
            @click="sidebarCollapsed = !sidebarCollapsed"
            class="p-2 rounded-xl transition-all duration-200 dark:hover:bg-white/5 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white text-gray-400 hover:text-gray-700"
            :title="sidebarCollapsed ? '展开菜单' : '收起菜单'"
          >
            <svg class="w-5 h-5 transition-transform duration-300" :class="sidebarCollapsed ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
          </button>
          <div class="flex items-center gap-2 text-sm">
            <router-link to="/" class="dark:text-gray-500 text-gray-400 hover:dark:text-gray-300 hover:text-gray-600 transition-colors">首页</router-link>
            <svg class="w-4 h-4 dark:text-gray-600 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
            <span class="font-medium dark:text-white text-gray-900">{{ currentTitle }}</span>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <button
            @click="themeStore.toggleTheme()"
            class="relative p-2.5 rounded-xl transition-all duration-300 hover:scale-105 dark:bg-white/5 dark:hover:bg-white/10 dark:text-yellow-400 bg-gray-100 hover:bg-gray-200 text-indigo-500"
            title="切换主题"
          >
            <svg v-if="themeStore.isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          </button>

          <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg dark:bg-emerald-500/10 dark:border dark:border-emerald-500/20 bg-emerald-50 border border-emerald-200">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span class="text-xs text-emerald-600 font-medium">在线</span>
          </div>

          <div class="relative group">
            <button class="flex items-center gap-3 px-4 py-2 rounded-xl transition-all duration-200 dark:hover:bg-white/5 hover:bg-gray-100">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-cyber-purple flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-primary-500/20">
                {{ (userStore.user?.full_name || userStore.user?.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div class="text-left hidden sm:block">
                <p class="text-sm font-medium dark:text-white text-gray-900">{{ userStore.user?.full_name || userStore.user?.username }}</p>
              </div>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider"
                :class="getRoleClass(userStore.user?.role)"
              >
                {{ getRoleName(userStore.user?.role) }}
              </span>
              <svg class="w-4 h-4 transition-colors dark:text-gray-400 dark:group-hover:text-white text-gray-400 group-hover:text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

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

      <main class="flex-1 overflow-auto transition-colors duration-300 dark:bg-transparent bg-gray-50">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const userStore = useUserStore()
const themeStore = useThemeStore()
const sidebarCollapsed = ref(false)

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
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.dark .nav-item {
  color: #9ca3af;
}

.dark .nav-item:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.05);
}

.light .nav-item {
  color: #6b7280;
}

.light .nav-item:hover {
  color: #111827;
  background-color: #f3f4f6;
}

.nav-item.active {
  color: white;
  background-color: rgba(255, 255, 255, 0.05);
}

.light .nav-item.active {
  color: #4f46e5;
  background-color: #eef2ff;
}
</style>
