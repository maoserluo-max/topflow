<template>
  <div class="min-h-screen p-8 space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-bold gradient-text mb-2">数据总览</h1>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2">
          <button
            v-for="p in userProjects"
            :key="p"
            @click="switchProject(p)"
            class="project-btn"
            :class="{ 'project-btn-active': currentProject === p }"
          >
            {{ p }}
          </button>
        </div>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="fetchStats"
          class="!rounded-xl dark:!bg-white/5 dark:!border-white/10 !bg-white !border-gray-200"
        />
      </div>
    </div>

    <div class="flex flex-wrap gap-1.5">
      <button
        v-for="shortcut in dateShortcuts"
        :key="shortcut.label"
        @click="applyDateShortcut(shortcut)"
        class="shortcut-btn"
        :class="{ 'shortcut-btn-active': activeShortcut === shortcut.label }"
      >
        {{ shortcut.label }}
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="(stat, index) in stats"
        :key="stat.title"
        class="stat-card-glow group cursor-pointer animate-in hover:scale-105 transition-transform duration-300"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <div class="flex items-start justify-between">
          <div class="space-y-3">
            <div>
              <p class="text-xs uppercase tracking-wider font-medium dark:text-gray-400 text-gray-500">{{ stat.title }}</p>
              <p class="text-3xl font-bold mt-1 dark:bg-gradient-to-r dark:from-white dark:to-gray-300 bg-gradient-to-r from-gray-800 to-gray-500 bg-clip-text text-transparent">
                {{ stat.format ? stat.format(stat.value) : formatNumber(stat.value) }}
              </p>
            </div>
          </div>
          <div
            class="w-full h-24 opacity-10 absolute right-0 top-0 rounded-r-2xl"
            :style="{ background: `linear-gradient(135deg, transparent, ${stat.color}30)` }"
          />
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 glass-card p-6 animate-in" style="animation-delay: 200ms">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold flex items-center gap-2 dark:text-white text-gray-900">
            <span class="w-2 h-2 rounded-full bg-cyber-blue animate-pulse"></span>
            视频数量趋势
          </h3>
          <div class="flex gap-2">
            <button
              v-for="u in trendUnits"
              :key="u.value"
              @click="trendUnit = u.value; fetchTrend()"
              class="trend-unit-btn"
              :class="{ 'trend-unit-btn-active': trendUnit === u.value }"
            >
              {{ u.label }}
            </button>
          </div>
        </div>
        <div ref="trendChart" style="height: 380px;" class="mt-4" />
      </div>

      <div class="glass-card p-6 animate-in" style="animation-delay: 300ms">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold flex items-center gap-2 dark:text-white text-gray-900">
            <span class="w-2 h-2 rounded-full bg-cyber-purple animate-pulse"></span>
            平台分布
          </h3>
        </div>
        <div ref="platformChart" style="height: 380px;" class="mt-4" />
      </div>
    </div>

    <div class="glass-card p-6 animate-in" style="animation-delay: 400ms">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold flex items-center gap-2 dark:text-white text-gray-900">
          <span class="w-2 h-2 rounded-full bg-cyber-green animate-pulse"></span>
          最近视频记录
        </h3>
        <button
          @click="$router.push('/videos')"
          class="cyber-button text-sm px-4 py-2"
        >
          查看全部 →
        </button>
      </div>

      <div class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>平台</th>
              <th>达人名称</th>
              <th>标题</th>
              <th class="text-right">播放量</th>
              <th class="text-right">点赞数</th>
              <th class="text-right">价格($)</th>
              <th>创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(video, index) in recentVideos" :key="index" class="group">
              <td>
                <span
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium"
                  :class="getPlatformClass(video.platform)"
                >
                  {{ video.platform?.toUpperCase() }}
                </span>
              </td>
              <td class="font-medium dark:text-white text-gray-900">{{ video.influencer_name }}</td>
              <td class="max-w-xs truncate dark:text-gray-400 text-gray-600">{{ video.title || '-' }}</td>
              <td class="text-right font-mono text-cyber-blue">{{ formatNumber(video.play_count) }}</td>
              <td class="text-right font-mono text-pink-400">{{ formatNumber(video.like_count) }}</td>
              <td class="text-right font-mono text-cyber-green">${{ video.price_usd || '0' }}</td>
              <td class="text-sm whitespace-nowrap dark:text-gray-500 text-gray-400">{{ formatDate(video.created_at) }}</td>
            </tr>
            <tr v-if="recentVideos.length === 0">
              <td colspan="7" class="text-center py-12 dark:text-gray-500 text-gray-400">
                <div class="space-y-2">
                  <div class="text-4xl">📊</div>
                  <p>暂无视频数据</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import api from '@/utils/api'
import * as echarts from 'echarts'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'

const themeStore = useThemeStore()
const userStore = useUserStore()

const dateRange = ref([])
const activeShortcut = ref('')
const currentProject = ref('')
const trendUnit = ref('day')

const userProjects = computed(() => userStore.userProjects)

const stats = ref([
  { title: '视频数', value: 0, color: '#00d4ff' },
  { title: '播放量', value: 0, color: '#a855f7' },
  { title: '金额($)', value: 0, color: '#10b981', format: (v) => v ? Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00' },
  { title: 'CPM', value: 0, color: '#ec4899', format: (v) => v.toFixed(2) }
])

const trendUnits = [
  { label: '天', value: 'day' },
  { label: '周', value: 'week' },
  { label: '月', value: 'month' }
]

const recentVideos = ref([])
const cachedPlatformData = ref({})
const cachedRegionData = ref({})
const trendData = ref([])

let trendChartInstance = null
let platformChartInstance = null
const trendChart = ref(null)
const platformChart = ref(null)

const dateShortcuts = [
  { label: '本周', getValue: () => { const now = new Date(); const day = now.getDay() || 7; const mon = new Date(now); mon.setDate(now.getDate() - day + 1); return [fmt(mon), fmt(now)]; } },
  { label: '上周', getValue: () => { const now = new Date(); const day = now.getDay() || 7; const mon = new Date(now); mon.setDate(now.getDate() - day - 6); const sun = new Date(mon); sun.setDate(mon.getDate() + 6); return [fmt(mon), fmt(sun)]; } },
  { label: '本月', getValue: () => { const now = new Date(); const first = new Date(now.getFullYear(), now.getMonth(), 1); return [fmt(first), fmt(now)]; } },
  { label: '上月', getValue: () => { const now = new Date(); const first = new Date(now.getFullYear(), now.getMonth() - 1, 1); const last = new Date(now.getFullYear(), now.getMonth(), 0); return [fmt(first), fmt(last)]; } },
  { label: '本年', getValue: () => { const now = new Date(); const first = new Date(now.getFullYear(), 0, 1); return [fmt(first), fmt(now)]; } }
]

function fmt(d) { return d.toISOString().split('T')[0] }

onMounted(() => {
  if (userProjects.value.length > 0) {
    currentProject.value = userProjects.value[0]
  }
  fetchStats()
  fetchTrend()

  if (trendChart.value) {
    trendChartInstance = echarts.init(trendChart.value)
  }

  if (platformChart.value) {
    platformChartInstance = echarts.init(platformChart.value)
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChartInstance?.dispose()
  platformChartInstance?.dispose()
})

watch(() => themeStore.isDark, () => {
  updateTrendChart()
  updatePlatformChart()
})

function handleResize() {
  trendChartInstance?.resize()
  platformChartInstance?.resize()
}

function switchProject(p) {
  currentProject.value = p
  fetchStats()
  fetchTrend()
}

function applyDateShortcut(shortcut) {
  activeShortcut.value = shortcut.label
  dateRange.value = shortcut.getValue()
  fetchStats()
  fetchTrend()
}

async function fetchStats() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (currentProject.value) {
      params.project = currentProject.value
    }

    const response = await api.get('/videos/dashboard/stats', { params })

    const totalPlays = response.total_plays || 0
    const totalAmount = response.total_amount || 0
    const cpm = totalPlays > 0 ? (totalAmount / totalPlays) * 1000 : 0

    stats.value[0].value = response.total_videos
    stats.value[1].value = response.total_plays
    stats.value[2].value = response.total_amount
    stats.value[3].value = cpm

    recentVideos.value = response.recent_videos || []

    cachedPlatformData.value = response.videos_by_platform
    cachedRegionData.value = response.videos_by_region

    updatePlatformChart()
  } catch (error) {
    console.error('Fetch stats error:', error)
  }
}

async function fetchTrend() {
  try {
    const params = { unit: trendUnit.value }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (currentProject.value) {
      params.project = currentProject.value
    }

    const response = await api.get('/videos/dashboard/trend', { params })
    trendData.value = response || []
    updateTrendChart()
  } catch (error) {
    console.error('Fetch trend error:', error)
  }
}

function getThemeColors() {
  if (themeStore.isDark) {
    return {
      bgColor: 'transparent',
      tooltipBg: 'rgba(15, 23, 42, 0.9)',
      tooltipBorder: 'rgba(99, 102, 241, 0.3)',
      textColor: '#e2e8f0',
      subTextColor: '#94a3b8',
      axisLineColor: 'rgba(148, 163, 184, 0.1)',
      splitLineColor: 'rgba(148, 163, 184, 0.05)',
      pieBorderColor: 'rgba(15, 23, 42, 0.8)',
      emphasisColor: '#fff'
    }
  }
  return {
    bgColor: 'transparent',
    tooltipBg: 'rgba(255, 255, 255, 0.95)',
    tooltipBorder: 'rgba(99, 102, 241, 0.2)',
    textColor: '#1e293b',
    subTextColor: '#64748b',
    axisLineColor: 'rgba(226, 232, 240, 0.8)',
    splitLineColor: 'rgba(226, 232, 240, 0.5)',
    pieBorderColor: 'rgba(255, 255, 255, 0.8)',
    emphasisColor: '#111827'
  }
}

function updateTrendChart() {
  if (!trendChartInstance) return

  const tc = getThemeColors()

  const dates = trendData.value.map(d => d.date)
  const counts = trendData.value.map(d => d.count)

  const option = {
    backgroundColor: tc.bgColor,
    tooltip: {
      trigger: 'axis',
      backgroundColor: tc.tooltipBg,
      borderColor: tc.tooltipBorder,
      borderWidth: 1,
      textStyle: { color: tc.textColor },
      formatter: (params) => {
        const p = params[0]
        return `${p.axisValue}<br/>视频数量: <b>${p.value}</b>`
      }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: tc.axisLineColor } },
      axisLabel: { color: tc.subTextColor, rotate: dates.length > 15 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      name: '视频个数',
      nameTextStyle: { color: tc.subTextColor, fontSize: 12 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: tc.splitLineColor } },
      axisLabel: { color: tc.subTextColor }
    },
    series: [{
      type: 'line',
      data: counts,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 3,
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#00d4ff' },
          { offset: 1, color: '#a855f7' }
        ])
      },
      itemStyle: {
        color: '#00d4ff',
        borderWidth: 2
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 212, 255, 0.25)' },
          { offset: 1, color: 'rgba(0, 212, 255, 0.02)' }
        ])
      }
    }]
  }

  trendChartInstance.setOption(option, true)
}

function updatePlatformChart() {
  if (!platformChartInstance) return

  const platformData = cachedPlatformData.value
  const tc = getThemeColors()

  const option = {
    backgroundColor: tc.bgColor,
    tooltip: {
      trigger: 'item',
      backgroundColor: tc.tooltipBg,
      borderColor: tc.tooltipBorder,
      borderWidth: 1,
      textStyle: { color: tc.textColor },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: tc.subTextColor }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '55%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: tc.pieBorderColor,
        borderWidth: 2
      },
      label: { show: false, position: 'center' },
      emphasis: {
        label: { show: true, fontSize: 18, fontWeight: 'bold', color: tc.emphasisColor }
      },
      labelLine: { show: false },
      data: Object.entries(platformData).map(([name, value], index) => ({
        name: name.toUpperCase(),
        value,
        itemStyle: { color: ['#00d4ff', '#a855f7', '#ec4899', '#10b981', '#f59e0b'][index % 5] }
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowColor: 'rgba(99, 102, 241, 0.5)'
        }
      }
    }]
  }

  platformChartInstance.setOption(option, true)
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 100000000) return (num / 100000000).toFixed(2) + '亿'
  if (num >= 10000) return (num / 10000).toFixed(2) + '万'
  return num.toLocaleString()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function getPlatformClass(platform) {
  const classes = {
    tiktok: 'dark:bg-black/30 dark:text-gray-200 dark:border-white/10 bg-gray-100 text-gray-700 border border-gray-200',
    ins: 'dark:bg-pink-500/10 dark:text-pink-400 dark:border-pink-500/20 bg-pink-50 text-pink-600 border border-pink-200',
    youtube: 'dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20 bg-red-50 text-red-600 border border-red-200'
  }
  return classes[platform] || 'dark:bg-gray-500/10 dark:text-gray-300 dark:border-gray-500/20 bg-gray-100 text-gray-600 border border-gray-200'
}
</script>

<style scoped>
.project-btn {
  padding: 6px 18px;
  border-radius: 10px;
  font-size: 0.8125rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}
.dark .project-btn {
  background: rgba(255,255,255,0.05);
  color: #9ca3af;
  border: 1px solid rgba(255,255,255,0.1);
}
.project-btn {
  background: #f3f4f6;
  color: #6b7280;
  border: 1px solid #e5e7eb;
}
.dark .project-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
  border-color: rgba(255,255,255,0.2);
}
.project-btn:hover {
  background: #e5e7eb;
  color: #111827;
  border-color: #d1d5db;
}
.project-btn-active {
  background: linear-gradient(to right, #4f46e5, #4338ca) !important;
  color: #fff !important;
  border-color: transparent !important;
  box-shadow: 0 4px 14px rgba(79,70,229,0.25);
}

.shortcut-btn {
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.2s;
}
.dark .shortcut-btn {
  background: rgba(255,255,255,0.05);
  color: #9ca3af;
}
.shortcut-btn {
  background: #f3f4f6;
  color: #6b7280;
}
.dark .shortcut-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
.shortcut-btn:hover {
  background: #e5e7eb;
  color: #111827;
}
.shortcut-btn-active {
  background: rgba(59,130,246,0.15) !important;
  color: #3b82f6 !important;
}
.dark .shortcut-btn-active {
  background: rgba(59,130,246,0.2) !important;
  color: #60a5fa !important;
}

.trend-unit-btn {
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 500;
  transition: all 0.2s;
}
.dark .trend-unit-btn {
  background: rgba(255,255,255,0.05);
  color: #9ca3af;
}
.trend-unit-btn {
  background: #f3f4f6;
  color: #6b7280;
}
.dark .trend-unit-btn:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}
.trend-unit-btn:hover {
  background: #e5e7eb;
  color: #111827;
}
.trend-unit-btn-active {
  background: rgba(0, 212, 255, 0.15) !important;
  color: #00d4ff !important;
}
.dark .trend-unit-btn-active {
  background: rgba(0, 212, 255, 0.2) !important;
  color: #00d4ff !important;
}
</style>
