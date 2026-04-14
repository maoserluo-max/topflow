<template>
  <div class="min-h-screen p-8 space-y-8">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-4xl font-bold gradient-text mb-2">数据总览</h1>
        <p class="text-gray-400 text-sm">实时监控您的达人营销数据</p>
      </div>
      <div class="flex items-center gap-3">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="fetchStats"
          class="!bg-white/5 !border-white/10 !rounded-xl"
        />
      </div>
    </div>

    <!-- 统计卡片 - 现代设计 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="(stat, index) in stats"
        :key="stat.title"
        class="stat-card-glow group cursor-pointer animate-in hover:scale-105 transition-transform duration-300"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <div class="flex items-start justify-between">
          <div class="space-y-3">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl transition-all duration-300 group-hover:scale-110"
              :style="{ background: `linear-gradient(135deg, ${stat.color}20, ${stat.color}10)`, color: stat.color }"
            >
              <component :is="stat.icon" />
            </div>
            <div>
              <p class="text-xs text-gray-400 uppercase tracking-wider font-medium">{{ stat.title }}</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                {{ formatNumber(stat.value) }}
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

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 趋势图 - 大卡片 -->
      <div class="lg:col-span-2 glass-card p-6 animate-in" style="animation-delay: 200ms">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-white flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-cyber-blue animate-pulse"></span>
            视频数据趋势
          </h3>
          <div class="flex gap-2">
            <span class="px-3 py-1 text-xs rounded-full bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/20">实时</span>
          </div>
        </div>
        <div ref="trendChart" style="height: 380px;" class="mt-4" />
      </div>

      <!-- 平台分布 - 玻璃卡片 -->
      <div class="glass-card p-6 animate-in" style="animationDelay: 300ms">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-semibold text-white flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-cyber-purple animate-pulse"></span>
            平台分布
          </h3>
        </div>
        <div ref="platformChart" style="height: 380px;" class="mt-4" />
      </div>
    </div>

    <!-- 最近视频记录 - 高级表格 -->
    <div class="glass-card p-6 animate-in" style="animationDelay: 400ms">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold text-white flex items-center gap-2">
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
              <td class="font-medium text-white">{{ video.influencer_name }}</td>
              <td class="max-w-xs truncate text-gray-400">{{ video.title || '-' }}</td>
              <td class="text-right font-mono text-cyber-blue">{{ formatNumber(video.play_count) }}</td>
              <td class="text-right font-mono text-pink-400">{{ formatNumber(video.like_count) }}</td>
              <td class="text-right font-mono text-cyber-green">${{ video.price_usd || '0' }}</td>
              <td class="text-gray-500 text-sm whitespace-nowrap">{{ formatDate(video.created_at) }}</td>
            </tr>
            <tr v-if="recentVideos.length === 0">
              <td colspan="7" class="text-center py-12 text-gray-500">
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
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api'
import * as echarts from 'echarts'

const dateRange = ref([])
const stats = ref([
  {
    title: '总视频数',
    value: 0,
    icon: 'VideoPlay',
    color: '#00d4ff'
  },
  {
    title: '总播放量',
    value: 0,
    icon: 'View',
    color: '#a855f7'
  },
  {
    title: '总点赞数',
    value: 0,
    icon: 'Star',
    color: '#ec4899'
  },
  {
    title: '总金额($)',
    value: 0,
    icon: 'Money',
    color: '#10b981'
  }
])

const recentVideos = ref([])

let trendChartInstance = null
let platformChartInstance = null
const trendChart = ref(null)
const platformChart = ref(null)

onMounted(() => {
  fetchStats()

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

function handleResize() {
  trendChartInstance?.resize()
  platformChartInstance?.resize()
}

async function fetchStats() {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await api.get('/videos/dashboard/stats', { params })

    stats.value[0].value = response.total_videos
    stats.value[1].value = response.total_plays
    stats.value[2].value = response.total_likes
    stats.value[3].value = response.total_amount

    recentVideos.value = response.recent_videos || []

    updateTrendChart(response.videos_by_platform)
    updatePlatformChart(response.videos_by_platform, response.videos_by_region)
  } catch (error) {
    console.error('Fetch stats error:', error)
  }
}

function updateTrendChart(platformData) {
  if (!trendChartInstance) return

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      }
    },
    legend: {
      data: Object.keys(platformData),
      textStyle: {
        color: '#94a3b8'
      },
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['视频数量'],
      axisLine: {
        lineStyle: { color: 'rgba(148, 163, 184, 0.1)' }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(148, 163, 184, 0.05)'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    series: Object.entries(platformData).map(([name, value], index) => ({
      name,
      type: 'bar',
      data: [value],
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: ['#00d4ff', '#a855f7', '#ec4899', '#10b981'][index % 4] },
          { offset: 1, color: ['rgba(0,212,255,0.2)', 'rgba(168,85,247,0.2)', 'rgba(236,72,153,0.2)', 'rgba(16,185,129,0.2)'][index % 4] }
        ])
      },
      barWidth: '40%'
    }))
  }

  trendChartInstance.setOption(option)
}

function updatePlatformChart(platformData, regionData) {
  if (!platformChartInstance) return

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(99, 102, 241, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#e2e8f0'
      },
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: {
        color: '#94a3b8'
      }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '55%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: 'rgba(15, 23, 42, 0.8)',
        borderWidth: 2
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 18,
          fontWeight: 'bold',
          color: '#fff'
        }
      },
      labelLine: {
        show: false
      },
      data: Object.entries(platformData).map(([name, value], index) => ({
        name: name.toUpperCase(),
        value,
        itemStyle: {
          color: ['#00d4ff', '#a855f7', '#ec4899', '#10b981', '#f59e0b'][index % 5]
        }
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

  platformChartInstance.setOption(option)
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

function getPlatformType(platform) {
  const types = { tiktok: '', ins: 'success', youtube: 'warning' }
  return types[platform] || 'info'
}

function getPlatformClass(platform) {
  const classes = {
    tiktok: 'bg-black/30 text-gray-200 border border-white/10',
    ins: 'bg-pink-500/10 text-pink-400 border border-pink-500/20',
    youtube: 'bg-red-500/10 text-red-400 border border-red-500/20'
  }
  return classes[platform] || 'bg-gray-500/10 text-gray-300 border border-gray-500/20'
}
</script>