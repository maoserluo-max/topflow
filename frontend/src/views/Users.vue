<template>
  <div class="users-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showCreateDialog">新增用户</el-button>
        </div>
      </template>

      <el-table :data="users" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">{{ getRoleName(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editUser(row)">编辑</el-button>
            <el-button
              :type="row.is_active ? 'warning' : 'success'"
              link
              size="small"
              @click="toggleUserStatus(row)"
            >
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button
              v-if="row.username !== 'admin'"
              type="danger"
              link
              size="small"
              @click="deleteUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="输入邮箱" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" placeholder="输入姓名（可选）" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="选择角色">
            <el-option label="管理员" value="admin" />
            <el-option label="经理" value="manager" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="输入密码" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref()

const defaultForm = {
  username: '',
  email: '',
  full_name: '',
  role: 'user',
  password: ''
}

const form = reactive({ ...defaultForm })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

onMounted(() => {
  fetchUsers()
})

async function fetchUsers() {
  loading.value = true

  try {
    const response = await api.get('/auth/users', {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    users.value = response || []
    total.value = response.length
  } catch (error) {
    console.error('Fetch users error:', error)
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false
  editingId.value = null
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

function editUser(user) {
  isEdit.value = true
  editingId.value = user.id
  Object.assign(form, {
    username: user.username,
    email: user.email,
    full_name: user.full_name,
    role: user.role
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value?.validate()
  submitting.value = true

  try {
    if (isEdit.value) {
      await api.put(`/auth/users/${editingId.value}`, form)
      ElMessage.success('更新成功')
    } else {
      await api.post('/auth/register', form)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    console.error('Submit error:', error)
  } finally {
    submitting.value = false
  }
}

function toggleUserStatus(user) {
  const action = user.is_active ? '禁用' : '启用'

  ElMessageBox.confirm(`确定要${action}用户"${user.username}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.put(`/auth/users/${user.id}`, { is_active: !user.is_active })
      ElMessage.success(`${action}成功`)
      fetchUsers()
    } catch (error) {
      console.error('Toggle status error:', error)
    }
  }).catch(() => {})
}

function deleteUser(user) {
  ElMessageBox.confirm(`确定要删除用户"${user.username}"吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/auth/users/${user.id}`)
      ElMessage.success('删除成功')
      fetchUsers()
    } catch (error) {
      console.error('Delete error:', error)
    }
  }).catch(() => {})
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getRoleType(role) {
  const types = { admin: 'danger', manager: 'warning', user: 'info' }
  return types[role] || 'info'
}

function getRoleName(role) {
  const names = { admin: '管理员', manager: '经理', user: '用户' }
  return names[role] || role
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>