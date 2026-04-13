<template>
  <div class="logs-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <el-button type="success" @click="exportLogs">导出CSV</el-button>
        </div>
      </template>

      <div class="filter-bar">
        <el-form :inline="true" :model="filters">
          <el-form-item label="操作类型">
            <el-select v-model="filters.action" placeholder="选择操作" clearable style="width: 150px;">
              <el-option label="用户登录" value="用户登录" />
              <el-option label="用户注册" value="用户注册" />
              <el-option label="创建视频" value="创建视频" />
              <el-option label="更新视频" value="更新视频" />
              <el-option label="删除视频" value="删除视频" />
              <el-option label="抓取视频元数据" value="抓取视频元数据" />
              <el-option label="更新用户" value="更新用户" />
              <el-option label="删除用户" value="删除用户" />
            </el-select>
          </el-form-item>
          <el-form-item label="模块">
            <el-select v-model="filters.module" placeholder="选择模块" clearable style="width: 120px;">
              <el-option label="认证" value="认证" />
              <el-option label="视频管理" value="视频管理" />
              <el-option label="系统管理" value="系统管理" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
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
            <el-button type="primary" @click="fetchLogs">搜索</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table :data="logs" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="user_id" label="用户ID" width="90" />
        <el-table-column prop="action" label="操作" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.module || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="250" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="130" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

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

    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export error:', error)
    ElMessage.error('导出失败')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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