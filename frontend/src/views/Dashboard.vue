<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-title">{{ stat.title }}</p>
              <p class="stat-value">{{ formatNumber(stat.value) }}</p>
            </div>
            <el-icon :size="48" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>视频数据趋势</span>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="fetchStats"
              />
            </div>
          </template>
          <div ref="trendChart" style="height: 400px;"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span>平台分布</span></template>
          <div ref="platformChart" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近视频记录</span>
              <el-button type="primary" size="small" @click="$router.push('/videos')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentVideos" stripe>
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }">
                <el-tag :type="getPlatformType(row.platform)">{{ row.platform.toUpperCase() }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="influencer_name" label="达人" width="150" />
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="play_count" label="播放量" width="120">
              <template #default="{ row }">{{ formatNumber(row.play_count) }}</template>
            </el-table-column>
            <el-table-column prop="like_count" label="点赞数" width="100">
              <template #default="{ row }">{{ formatNumber(row.like_count) }}</template>
            </el-table-column>
            <el-table-column prop="price_usd" label="价格($)" width="100">
              <template #default="{ row }">{{ row.price_usd || '-' }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/utils/api'
import * as echarts from 'echarts'

const dateRange = ref([])
const stats = ref([
  { title: '总视频数', value: 0, icon: 'VideoPlay', color: '#1890ff' },
  { title: '总播放量', value: 0, icon: 'View', color: '#52c41a' },
  { title: '总点赞数', value: 0, icon: 'Star', color: '#faad14' },
  { title: '总金额($)', value: 0, icon: 'Money', color: '#f5222d' }
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
    tooltip: { trigger: 'axis' },
    legend: { data: Object.keys(platformData) },
    xAxis: { type: 'category', data: ['视频数量'] },
    yAxis: { type: 'value' },
    series: Object.entries(platformData).map(([name, value]) => ({
      name,
      type: 'bar',
      data: [value]
    }))
  }

  trendChartInstance.setOption(option)
}

function updatePlatformChart(platformData, regionData) {
  if (!platformChartInstance) return

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: { label: { show: true, fontSize: 18, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: Object.entries(platformData).map(([name, value]) => ({
        name: name.toUpperCase(),
        value
      }))
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
</script>

<style scoped>
.stat-cards .stat-card {
  margin-bottom: 10px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-title {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>