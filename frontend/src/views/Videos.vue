<template>
  <div class="videos-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>视频管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showCreateDialog">新增视频</el-button>
            <el-button @click="showFetchDialog">抓取元数据</el-button>
          </div>
        </div>
      </template>

      <div class="filter-bar">
        <el-form :inline="true" :model="filters">
          <el-form-item label="平台">
            <el-select v-model="filters.platform" placeholder="选择平台" clearable style="width: 120px;">
              <el-option label="TikTok" value="tiktok" />
              <el-option label="Instagram" value="ins" />
              <el-option label="YouTube" value="youtube" />
            </el-select>
          </el-form-item>
          <el-form-item label="地区">
            <el-input v-model="filters.region" placeholder="输入地区" clearable style="width: 120px;" />
          </el-form-item>
          <el-form-item label="达人">
            <el-input v-model="filters.influencer_name" placeholder="输入达人名称" clearable style="width: 150px;" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="选择状态" clearable style="width: 120px;">
              <el-option label="待确认" value="pending" />
              <el-option label="已发布" value="published" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="发布日期">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchVideos">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="videos" v-loading="loading" stripe border>
        <el-table-column prop="platform" label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="getPlatformType(row.platform)" size="small">{{ row.platform.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="region" label="地区" width="80" />
        <el-table-column prop="influencer_name" label="达人" width="130" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="price_usd" label="价格($)" width="90" align="right">
          <template #default="{ row }">{{ row.price_usd || '-' }}</template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布日期" width="110">
          <template #default="{ row }">{{ formatDate(row.publish_date) }}</template>
        </el-table-column>
        <el-table-column prop="play_count" label="播放量" width="100" align="right">
          <template #default="{ row }">{{ formatNumber(row.play_count) }}</template>
        </el-table-column>
        <el-table-column prop="like_count" label="点赞数" width="90" align="right">
          <template #default="{ row }">{{ formatNumber(row.like_count) }}</template>
        </el-table-column>
        <el-table-column prop="comment_count" label="评论数" width="90" align="right">
          <template #default="{ row }">{{ formatNumber(row.comment_count) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusName(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editVideo(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteVideo(row)">删除</el-button>
            <el-button v-if="row.video_url" type="success" link size="small" @click="openVideo(row.video_url)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchVideos"
          @current-change="fetchVideos"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑视频' : '新增视频'" width="700px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="平台" prop="platform">
              <el-select v-model="form.platform" placeholder="选择平台">
                <el-option label="TikTok" value="tiktok" />
                <el-option label="Instagram" value="ins" />
                <el-option label="YouTube" value="youtube" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地区" prop="region">
              <el-input v-model="form.region" placeholder="输入地区" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="达人名称" prop="influencer_name">
              <el-input v-model="form.influencer_name" placeholder="输入达人名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合作价格($)" prop="price_usd">
              <el-input-number v-model="form.price_usd" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="内容方向" prop="content_direction">
          <el-input v-model="form.content_direction" placeholder="输入内容方向" />
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" type="textarea" :rows="2" placeholder="输入视频标题" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发布日期" prop="publish_date">
              <el-date-picker v-model="form.publish_date" type="datetime" placeholder="选择日期时间" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="选择状态">
                <el-option label="待确认" value="pending" />
                <el-option label="已发布" value="published" />
                <el-option label="已完成" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>数据统计（自动获取或手动填写）</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="播放量">
              <el-input-number v-model="form.play_count" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="点赞数">
              <el-input-number v-model="form.like_count" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="评论数">
              <el-input-number v-model="form.comment_count" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="分享数">
              <el-input-number v-model="form.share_count" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="视频链接">
              <el-input v-model="form.video_url" placeholder="输入视频链接" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>联系信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="对接人">
              <el-input v-model="form.contact_person" placeholder="对接人姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="邮箱">
              <el-input v-model="form.contact_email" placeholder="邮箱地址" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="WhatsApp">
              <el-input v-model="form.contact_whatsapp" placeholder="WhatsApp号码" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fetchDialogVisible" title="抓取视频元数据" width="500px">
      <el-alert title="粘贴TikTok/Instagram/YouTube视频链接，系统将自动获取视频数据" type="info" :closable="false" show-icon style="margin-bottom: 20px;" />

      <el-form @submit.prevent="fetchMetadata">
        <el-form-item label="视频链接">
          <el-input v-model="videoUrl" placeholder="https://www.tiktok.com/@user/video/xxx" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="fetchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="fetching" @click="fetchMetadata">开始抓取</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
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
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref()

const defaultForm = {
  platform: 'tiktok',
  region: '',
  content_direction: '',
  influencer_name: '',
  price_usd: null,
  title: '',
  publish_date: null,
  play_count: 0,
  like_count: 0,
  comment_count: 0,
  share_count: 0,
  video_url: '',
  contact_person: '',
  contact_email: '',
  contact_whatsapp: '',
  status: 'pending'
}

const form = reactive({ ...defaultForm })

const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  influencer_name: [{ required: true, message: '请输入达人名称', trigger: 'blur' }]
}

const fetchDialogVisible = ref(false)
const videoUrl = ref('')
const fetching = ref(false)

onMounted(() => {
  fetchVideos()
})

async function fetchVideos() {
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

    const response = await api.get('/videos/', { params })
    videos.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    console.error('Fetch videos error:', error)
  } finally {
    loading.value = false
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
  editingId.value = null
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

function editVideo(video) {
  isEdit.value = true
  editingId.value = video.id
  Object.assign(form, {
    platform: video.platform,
    region: video.region,
    content_direction: video.content_direction,
    influencer_name: video.influencer_name,
    price_usd: video.price_usd,
    title: video.title,
    publish_date: video.publish_date ? new Date(video.publish_date) : null,
    play_count: video.play_count,
    like_count: video.like_count,
    comment_count: video.comment_count,
    share_count: video.share_count,
    video_url: video.video_url,
    contact_person: video.contact_person,
    contact_email: video.contact_email,
    contact_whatsapp: video.contact_whatsapp,
    status: video.status
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true

  try {
    const data = { ...form }

    if (data.publish_date instanceof Date) {
      data.publish_date = data.publish_date.toISOString()
    }

    if (isEdit.value) {
      await api.put(`/videos/${editingId.value}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/videos/', data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchVideos()
  } catch (error) {
    console.error('Submit error:', error)
  } finally {
    submitting.value = false
  }
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

function showFetchDialog() {
  videoUrl.value = ''
  fetchDialogVisible.value = true
}

async function fetchMetadata() {
  if (!videoUrl.value.trim()) {
    ElMessage.warning('请输入视频链接')
    return
  }

  fetching.value = true

  try {
    const response = await api.post('/videos/fetch-metadata', { url: videoUrl.value })

    ElMessage.success('抓取成功！已自动填充表单')

    Object.assign(form, {
      platform: response.platform,
      influencer_name: response.influencer_name,
      title: response.video_title,
      publish_date: response.publish_date ? new Date(response.publish_date) : null,
      play_count: response.play_count || 0,
      like_count: response.like_count || 0,
      comment_count: response.comment_count || 0,
      share_count: response.share_count || 0,
      video_url: response.video_url
    })

    fetchDialogVisible.value = false
    showCreateDialog()
  } catch (error) {
    console.error('Fetch metadata error:', error)
  } finally {
    fetching.value = false
  }
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

function getPlatformType(platform) {
  const types = { tiktok: '', ins: 'success', youtube: 'warning' }
  return types[platform] || 'info'
}

function getStatusType(status) {
  const types = { pending: 'warning', published: '', completed: 'success' }
  return types[status] || 'info'
}

function getStatusName(status) {
  const names = { pending: '待确认', published: '已发布', completed: '已完成' }
  return names[status] || status
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-bar {
  margin-bottom: 20px;
  padding: 15px;
  background: #fafafa;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>