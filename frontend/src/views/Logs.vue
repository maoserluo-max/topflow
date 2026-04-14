<template>
  <div class="min-h-screen p-8 space-y-8">
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h1 class="text-4xl font-bold gradient-text">操作日志</h1>
        <p class="text-gray-400 text-sm">记录系统所有操作行为，支持筛选与导出</p>
      </div>
      <button @click="exportLogs" class="cyber-button flex items-center gap-2 text-sm font-medium">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        导出CSV
      </button>
    </div>

    <div class="glass-card p-6 animate-in">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
        <h3 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">筛选条件</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="space-y-1.5">
          <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">操作类型</label>
          <select
            v-model="filters.action"
            class="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
          >
            <option value="" class="bg-gray-900">全部操作</option>
            <option value="用户登录" class="bg-gray-900">用户登录</option>
            <option value="用户注册" class="bg-gray-900">用户注册</option>
            <option value="创建视频" class="bg-gray-900">创建视频</option>
            <option value="更新视频" class="bg-gray-900">更新视频</option>
            <option value="删除视频" class="bg-gray-900">删除视频</option>
            <option value="抓取视频元数据" class="bg-gray-900">抓取视频元数据</option>
            <option value="更新用户" class="bg-gray-900">更新用户</option>
            <option value="删除用户" class="bg-gray-900">删除用户</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">模块</label>
          <select
            v-model="filters.module"
            class="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
          >
            <option value="" class="bg-gray-900">全部模块</option>
            <option value="认证" class="bg-gray-900">认证</option>
            <option value="视频管理" class="bg-gray-900">视频管理</option>
            <option value="系统管理" class="bg-gray-900">系统管理</option>
          </select>
        </div>

        <div class="space-y-1.5 lg:col-span-2">
          <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">时间范围</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="!w-full !bg-white/5 !border-white/10 !rounded-xl"
          />
        </div>

        <div class="space-y-1.5 flex items-end">
          <div class="flex gap-3 w-full">
            <button
              @click="fetchLogs"
              class="flex-1 px-6 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white shadow-lg shadow-primary-500/25 transition-all duration-200"
            >
              搜索
            </button>
            <button
              @click="resetFilters"
              class="px-5 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 border border-white/10 hover:border-white/20 transition-all duration-200"
            >
              重置
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="glass-card overflow-hidden animate-in" style="animation-delay: 100ms">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="space-y-4 text-center">
          <div class="w-12 h-12 mx-auto border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <p class="text-gray-400 text-sm">加载日志数据中...</p>
        </div>
      </div>

      <div v-else class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>ID</th>
              <th>操作类型</th>
              <th>模块</th>
              <th>详情</th>
              <th>IP地址</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(log, index) in logs" :key="log.id" class="group animate-in" :style="{ animationDelay: `${index * 50}ms` }">
              <td class="font-mono text-xs text-gray-500">#{{ log.id }}</td>
              <td>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                  :class="getActionClass(log.action)"
                >
                  {{ log.action }}
                </span>
              </td>
              <td>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium bg-white/5 text-gray-300 border border-white/10"
                >
                  {{ log.module || '-' }}
                </span>
              </td>
              <td class="max-w-[300px] truncate text-gray-400">{{ log.detail || '-' }}</td>
              <td class="font-mono text-xs text-gray-500">{{ log.ip_address || '-' }}</td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(log.created_at) }}</td>
            </tr>
          </tbody>
        </table>

        <div v-if="logs.length === 0 && !loading" class="py-16 text-center">
          <svg class="w-16 h-16 mx-auto text-gray-600 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-500 text-sm">暂无日志数据</p>
        </div>
      </div>

      <div v-if="total > 0" class="px-6 py-4 border-t border-white/5 flex items-center justify-between">
        <p class="text-sm text-gray-500">
          共 <span class="font-medium text-gray-300">{{ total }}</span> 条记录
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="currentPage > 1 && (currentPage--, fetchLogs())"
            :disabled="currentPage <= 1"
            class="px-3 py-1.5 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            上一页
          </button>
          <span class="px-4 py-1.5 rounded-lg bg-primary-500/10 text-primary-400 text-sm font-medium">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button
            @click="currentPage < totalPages && (currentPage++, fetchLogs())"
            :disabled="currentPage >= totalPages"
            class="px-3 py-1.5 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const logs = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])

const filters = reactive({
  action: '',
  module: ''
})

const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

onMounted(() => {
  fetchLogs()
})

async function fetchLogs() {
  loading.value = true

  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await api.get('/admin/logs', { params })
    logs.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    console.error('Fetch logs error:', error)
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { action: '', module: '' })
  dateRange.value = []
  currentPage.value = 1
  fetchLogs()
}

async function exportLogs() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await api.get('/admin/export-logs', { params })

    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `operation_logs_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    alert('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    alert('导出失败')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getActionClass(action) {
  const map = {
    '用户登录': 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25',
    '用户注册': 'bg-blue-500/15 text-blue-400 border border-blue-500/25',
    '创建视频': 'bg-primary-500/15 text-primary-400 border border-primary-500/25',
    '更新视频': 'bg-amber-500/15 text-amber-400 border border-amber-500/25',
    '删除视频': 'bg-red-500/15 text-red-400 border border-red-500/25',
    '抓取视频元数据': 'bg-cyber-purple/15 text-cyber-purple border border-cyber-purple/25',
    '更新用户': 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/25',
    '删除用户': 'bg-red-500/15 text-red-400 border border-red-500/25'
  }
  return map[action] || 'bg-gray-500/15 text-gray-400 border border-gray-500/25'
}
</script>