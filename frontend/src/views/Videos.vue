<template>
  <div class="min-h-screen p-8 space-y-8">
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h1 class="text-4xl font-bold gradient-text">视频管理</h1>
        <p class="text-sm dark:text-gray-400 text-gray-500">管理所有达人视频数据，支持自动抓取元数据</p>
      </div>
      <button @click="showCreateDialog" class="cyber-button flex items-center gap-2 text-sm font-medium">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新增视频
      </button>
    </div>

    <div class="glass-card p-6 animate-in">
      <div class="flex items-center gap-3 mb-4">
        <span class="w-1.5 h-5 rounded-full bg-gradient-to-b from-cyber-blue to-cyber-purple"></span>
        <h3 class="text-sm font-semibold dark:text-gray-300 text-gray-600 uppercase tracking-wider">筛选条件</h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">平台</label>
          <select
            v-model="filters.platform"
            class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部平台</option>
            <option value="tiktok" class="dark:bg-gray-900 bg-white">TikTok</option>
            <option value="ins" class="dark:bg-gray-900 bg-white">Instagram</option>
            <option value="youtube" class="dark:bg-gray-900 bg-white">YouTube</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">地区</label>
          <select
            v-model="filters.region"
            class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部地区</option>
            <option v-for="r in regionOptions" :key="r.value" :value="r.value" class="dark:bg-gray-900 bg-white">{{ r.label }}</option>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">达人</label>
          <input
            v-model="filters.influencer_name"
            type="text"
            placeholder="搜索达人..."
            class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">状态</label>
          <select
            v-model="filters.status"
            class="w-full px-4 py-2.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
          >
            <option value="" class="dark:bg-gray-900 bg-white">全部状态</option>
            <option v-for="s in statusOptions" :key="s.value" :value="s.value" class="dark:bg-gray-900 bg-white">{{ s.label }}</option>
          </select>
        </div>

        <div class="space-y-1.5 lg:col-span-2">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">发布日期</label>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="!w-full !rounded-xl dark:!bg-white/5 dark:!border-white/10 !bg-white !border-gray-200"
          />
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-6 pt-4 dark:border-t dark:border-white/5 border-t border-gray-200">
        <button
          @click="resetFilters"
          class="px-5 py-2 rounded-xl text-sm font-medium dark:text-gray-400 dark:hover:text-white dark:hover:bg-white/5 dark:border-white/10 dark:hover:border-white/20 text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 transition-all duration-200"
        >
          重置筛选
        </button>
        <button
          @click="fetchVideos"
          class="px-6 py-2 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 transition-all duration-200"
        >
          搜索数据
        </button>
      </div>
    </div>

    <div class="glass-card overflow-hidden animate-in" style="animation-delay: 100ms">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="space-y-4 text-center">
          <div class="w-12 h-12 mx-auto border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <p class="dark:text-gray-400 text-gray-500 text-sm">加载数据中...</p>
        </div>
      </div>

      <div v-else class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>平台</th>
              <th>地区</th>
              <th>达人</th>
              <th>标题</th>
              <th class="text-right">价格($)</th>
              <th>发布日期</th>
              <th class="text-right">播放量</th>
              <th class="text-right">点赞数</th>
              <th>状态</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(video, index) in videos" :key="video.id" class="group animate-in" :style="{ animationDelay: `${index * 50}ms` }">
              <td>
                <span
                  class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold tracking-wide"
                  :class="getPlatformClass(video.platform)"
                >
                  {{ video.platform?.toUpperCase() }}
                </span>
              </td>
              <td class="font-mono text-xs dark:text-gray-400 text-gray-500">{{ getRegionName(video.region) }}</td>
              <td class="font-medium dark:text-white text-gray-900">{{ video.influencer_name }}</td>
              <td class="max-w-[200px] truncate dark:text-gray-400 text-gray-600">{{ video.title || '-' }}</td>
              <td class="text-right font-mono text-cyber-green font-semibold">${{ video.price_usd || '0' }}</td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(video.publish_date) }}</td>
              <td class="text-right font-mono text-cyber-blue">{{ formatNumber(video.play_count) }}</td>
              <td class="text-right font-mono text-pink-400">{{ formatNumber(video.like_count) }}</td>
              <td>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
                  :class="getStatusClass(video.status)"
                >
                  {{ getStatusName(video.status) }}
                </span>
              </td>
              <td>
                <div class="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    @click="editVideo(video)"
                    class="p-1.5 rounded-lg hover:bg-cyber-blue/10 text-cyber-blue transition-colors"
                    title="编辑"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="deleteVideo(video)"
                    class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
                    title="删除"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                  <button
                    v-if="video.video_url"
                    @click="openVideo(video.video_url)"
                    class="p-1.5 rounded-lg hover:bg-cyber-purple/10 text-cyber-purple transition-colors"
                    title="查看"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="videos.length === 0">
              <td colspan="10" class="text-center py-20">
                <div class="space-y-3">
                  <div class="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary-500/10 to-cyber-purple/10 flex items-center justify-center">
                    <svg class="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p class="dark:text-gray-500 text-gray-500 text-sm">暂无视频数据</p>
                  <button @click="showCreateDialog" class="cyber-button text-sm px-4 py-2">
                    添加第一条视频
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <Pagination
        v-model="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        show-page-size
        @change="fetchVideos"
      />
    </div>

    <VideoFormDialog
      :visible="dialogVisible"
      :is-edit="isEdit"
      :edit-data="editingVideo"
      :user-list="userList"
      @close="dialogVisible = false"
      @submitted="onDialogSubmitted"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import Pagination from '@/components/Pagination.vue'
import VideoFormDialog from '@/components/VideoFormDialog.vue'

const userStore = useUserStore()
const themeStore = useThemeStore()
const loading = ref(false)
const videos = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])

const filters = reactive({
  platform: '',
  region: '',
  influencer_name: '',
  status: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingVideo = ref(null)

const userRole = computed(() => userStore.user?.role || '')

const canSelectAllUsers = computed(() => {
  return ['admin', 'manager'].includes(userRole.value)
})

const userList = ref([])

const regionOptions = [
  { value: 'ID', label: '印尼 (ID)' },
  { value: 'MY', label: '马来西亚 (MY)' },
  { value: 'TH', label: '泰国 (TH)' },
  { value: 'TW', label: '台湾 (TW)' },
  { value: 'KR', label: '韩国 (KR)' },
  { value: 'JP', label: '日本 (JP)' }
]

const statusOptions = [
  { value: 'pending_review', label: '待审核' },
  { value: 'pending_publish', label: '待发布' },
  { value: 'published', label: '已发布' },
  { value: 'completed', label: '已完成' }
]

onMounted(async () => {
  fetchVideos()
  if (canSelectAllUsers.value) {
    await fetchUsers()
  }
})

async function fetchVideos() {
  loading.value = true

  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      sort_by: 'publish_date',
      sort_order: 'desc',
      ...filters
    }

    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const response = await api.get('/videos/', { params })
    videos.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    console.error('Fetch videos error:', error)
  } finally {
    loading.value = false
  }
}

async function fetchUsers() {
  try {
    const response = await api.get('/auth/users')
    userList.value = Array.isArray(response) ? response : (response.items || [])
  } catch (error) {
    console.warn('获取用户列表失败（非管理员无法查看用户列表）:', error.message)
    userList.value = []
  }
}

function resetFilters() {
  Object.assign(filters, {
    platform: '',
    region: '',
    influencer_name: '',
    status: ''
  })
  dateRange.value = []
  currentPage.value = 1
  fetchVideos()
}

function showCreateDialog() {
  isEdit.value = false
  editingVideo.value = null
  dialogVisible.value = true
}

function editVideo(video) {
  isEdit.value = true
  editingVideo.value = { ...video }
  dialogVisible.value = true
}

function onDialogSubmitted() {
  fetchVideos()
}

function deleteVideo(video) {
  ElMessageBox.confirm(`确定要删除视频"${video.title || video.influencer_name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/videos/${video.id}`)
      ElMessage.success('删除成功')
      fetchVideos()
    } catch (error) {
      console.error('Delete error:', error)
    }
  }).catch(() => {})
}

function openVideo(url) {
  window.open(url, '_blank')
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toLocaleString()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function getRegionName(region) {
  const found = regionOptions.find(r => r.value === region)
  return found ? found.label : region || '-'
}

function getPlatformClass(platform) {
  const classes = {
    tiktok: 'dark:bg-black/40 dark:text-gray-200 dark:border-white/20 bg-gray-100 text-gray-700 border border-gray-200',
    ins: 'dark:bg-pink-500/10 dark:text-pink-400 dark:border-pink-500/30 bg-pink-50 text-pink-600 border border-pink-200',
    youtube: 'dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/30 bg-red-50 text-red-600 border border-red-200'
  }
  return classes[platform] || 'dark:bg-gray-500/10 dark:text-gray-300 dark:border-gray-500/30 bg-gray-100 text-gray-600 border border-gray-200'
}

function getStatusClass(status) {
  const classes = {
    pending_review: 'dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/30 bg-blue-50 text-blue-600 border border-blue-200',
    pending_publish: 'dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/30 bg-amber-50 text-amber-600 border border-amber-200',
    published: 'dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/30 bg-emerald-50 text-emerald-600 border border-emerald-200',
    completed: 'dark:bg-purple-500/10 dark:text-purple-400 dark:border-purple-500/30 bg-purple-50 text-purple-600 border border-purple-200'
  }
  return classes[status] || 'dark:bg-gray-500/10 dark:text-gray-400 dark:border-gray-500/30 bg-gray-100 text-gray-600 border border-gray-200'
}

function getStatusName(status) {
  const names = {
    pending_review: '待审核',
    pending_publish: '待发布',
    published: '已发布',
    completed: '已完成'
  }
  return names[status] || status
}
</script>
