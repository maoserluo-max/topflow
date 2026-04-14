<template>
  <div class="videos-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>视频管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="showCreateDialog">新增视频</el-button>
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
            <el-select v-model="filters.region" placeholder="选择地区" clearable style="width: 120px;">
              <el-option v-for="r in regionOptions" :key="r.value" :label="r.label" :value="r.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="达人">
            <el-input v-model="filters.influencer_name" placeholder="输入达人名称" clearable style="width: 150px;" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filters.status" placeholder="选择状态" clearable style="width: 120px;">
              <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
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
        <el-table-column prop="region" label="地区" width="80">
          <template #default="{ row }">{{ getRegionName(row.region) }}</template>
        </el-table-column>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑视频' : '新增视频'" width="750px">
      <el-alert 
        v-if="!isEdit" 
        title="提示：可粘贴视频链接并点击「抓取数据」自动填充信息，也可手动填写所有字段" 
        type="info" 
        :closable="false" 
        show-icon 
        style="margin-bottom: 20px;" 
      />

      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">

        <el-divider content-position="left">视频链接（可选）</el-divider>

        <el-row :gutter="20">
          <el-col :span="18">
            <el-form-item label="视频链接">
              <el-input v-model="form.video_url" placeholder="粘贴TikTok/Instagram/YouTube视频链接" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label=" " :label-width="'20px'">
              <el-button type="success" :loading="fetching" @click="fetchMetadataInDialog" :disabled="!form.video_url">
                抓取数据
              </el-button>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">基本信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="平台" prop="platform">
              <el-select v-model="form.platform" placeholder="选择平台" style="width: 100%;">
                <el-option label="TikTok" value="tiktok" />
                <el-option label="Instagram" value="ins" />
                <el-option label="YouTube" value="youtube" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地区" prop="region">
              <el-select v-model="form.region" placeholder="选择地区" style="width: 100%;">
                <el-option v-for="r in regionOptions" :key="r.value" :label="r.label" :value="r.value" />
              </el-select>
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
            <el-form-item label="内容方向" prop="content_direction">
              <el-select v-model="form.content_direction" placeholder="选择内容方向" style="width: 100%;">
                <el-option v-for="d in directionOptions" :key="d.value" :label="d.label" :value="d.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="合作价格($)" prop="price_usd">
              <el-input-number v-model="form.price_usd" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="对接人" prop="contact_person">
              <el-select 
                v-if="canSelectAllUsers" 
                v-model="form.contact_person" 
                placeholder="选择对接人" 
                filterable 
                style="width: 100%;"
              >
                <el-option v-for="u in userList" :key="u.username" :label="u.full_name || u.username" :value="u.username" />
              </el-select>
              <el-input v-else v-model="form.contact_person" disabled :placeholder-value="currentUser" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" type="textarea" :rows="2" placeholder="输入视频标题" />
        </el-form-item>

        <el-divider content-position="left">发布与状态</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="发布日期" prop="publish_date">
              <el-date-picker 
                v-model="form.publish_date" 
                type="date" 
                placeholder="选择日期" 
                format="YYYY-MM-DD" 
                value-format="YYYY-MM-DD"
                style="width: 100%;" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="选择状态" style="width: 100%;">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">数据统计（自动获取或手动填写）</el-divider>

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
            <el-form-item label="邮箱">
              <el-input v-model="form.contact_email" placeholder="联系邮箱地址" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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
const fetching = ref(false)

const currentUser = computed(() => userStore.user?.username || '')
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

const directionOptions = [
  { value: 'FF', label: 'Free Fire' },
  { value: 'MLBB', label: 'Mobile Legends' }
]

const statusOptions = [
  { value: 'pending_review', label: '待审核' },
  { value: 'pending_publish', label: '待发布' },
  { value: 'published', label: '已发布' },
  { value: 'completed', label: '已完成' }
]

const defaultForm = {
  platform: 'tiktok',
  region: '',
  content_direction: '',
  influencer_name: '',
  price_usd: null,
  title: '',
  publish_date: new Date().toISOString().split('T')[0],
  play_count: 0,
  like_count: 0,
  comment_count: 0,
  share_count: 0,
  video_url: '',
  contact_person: '',
  contact_email: '',
  contact_whatsapp: '',
  status: 'pending_review'
}

const form = reactive({ ...defaultForm })

const rules = {
  platform: [{ required: true, message: '请选择平台', trigger: 'change' }],
  influencer_name: [{ required: true, message: '请输入达人名称', trigger: 'blur' }]
}

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
  editingId.value = null
  Object.assign(form, {
    ...defaultForm,
    publish_date: new Date().toISOString().split('T')[0],
    contact_person: canSelectAllUsers.value ? '' : currentUser.value
  })
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
    publish_date: video.publish_date ? video.publish_date.split('T')[0] : new Date().toISOString().split('T')[0],
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
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

  submitting.value = true

  try {
    const data = { ...form }

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

async function fetchMetadataInDialog() {
  if (!form.video_url?.trim()) {
    ElMessage.warning('请先输入视频链接')
    return
  }

  fetching.value = true

  try {
    const response = await api.post('/videos/fetch-metadata', { url: form.video_url })

    ElMessage.success('抓取成功！已自动填充表单')

    Object.assign(form, {
      platform: response.platform || form.platform,
      influencer_name: response.influencer_name || form.influencer_name,
      title: response.video_title || form.title,
      play_count: response.play_count || 0,
      like_count: response.like_count || 0,
      comment_count: response.comment_count || 0,
      share_count: response.share_count || 0
    })
  } catch (error) {
    console.error('Fetch metadata error:', error)
    ElMessage.warning('抓取失败，请手动填写数据')
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
  const types = { 
    pending_review: 'info', 
    pending_publish: 'warning', 
    published: '', 
    completed: 'success' 
  }
  return types[status] || 'info'
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

function getRegionName(region) {
  const found = regionOptions.find(r => r.value === region)
  return found ? found.label : region || '-'
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