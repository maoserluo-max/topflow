<template>
  <div class="min-h-screen p-8 space-y-8">
    <!-- 页面标题区 -->
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h1 class="text-4xl font-bold gradient-text">用户管理</h1>
        <p class="text-gray-400 text-sm">管理系统用户账户、角色权限与状态</p>
      </div>
      <button @click="showCreateDialog" class="cyber-button flex items-center gap-2 text-sm font-medium">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新增用户
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in">
      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl bg-gradient-to-br from-cyber-blue/20 to-cyber-blue/5 text-cyber-blue">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-400 uppercase tracking-wider font-medium">总用户数</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">{{ users.length }}</p>
            </div>
          </div>
          <div class="w-full h-20 opacity-10 absolute right-0 top-0 rounded-r-2xl bg-gradient-to-l from-cyber-blue to-transparent"></div>
        </div>
      </div>

      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl bg-gradient-to-br from-emerald-500/20 to-emerald-500/5 text-emerald-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-400 uppercase tracking-wider font-medium">活跃用户</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">{{ activeUserCount }}</p>
            </div>
          </div>
          <div class="w-full h-20 opacity-10 absolute right-0 top-0 rounded-r-2xl bg-gradient-to-l from-emerald-500 to-transparent"></div>
        </div>
      </div>

      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl bg-gradient-to-br from-primary-500/20 to-primary-500/5 text-primary-400">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-400 uppercase tracking-wider font-medium">管理员</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-primary-400 to-purple-300 bg-clip-text text-transparent">{{ adminCount }}</p>
            </div>
          </div>
          <div class="w-full h-20 opacity-10 absolute right-0 top-0 rounded-r-2xl bg-gradient-to-l from-primary-500 to-transparent"></div>
        </div>
      </div>
    </div>

    <!-- 用户表格 - 现代设计 -->
    <div class="glass-card overflow-hidden animate-in" style="animation-delay: 100ms">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="space-y-4 text-center">
          <div class="w-12 h-12 mx-auto border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <p class="text-gray-400 text-sm">加载用户数据中...</p>
        </div>
      </div>

      <div v-else class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>姓名</th>
              <th>角色</th>
              <th>状态</th>
              <th>注册时间</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="user.id" class="group animate-in" :style="{ animationDelay: `${index * 50}ms` }">
              <td class="font-mono text-xs text-gray-500">#{{ user.id }}</td>
              <td>
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500/30 to-cyber-purple/30 flex items-center justify-center text-sm font-bold text-white uppercase">
                    {{ (user.username || 'U').charAt(0) }}
                  </div>
                  <span class="font-medium text-white">{{ user.username }}</span>
                </div>
              </td>
              <td class="text-gray-400 text-sm">{{ user.email || '-' }}</td>
              <td class="text-gray-300">{{ user.full_name || '-' }}</td>
              <td>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                  :class="getRoleClass(user.role)"
                >
                  {{ getRoleName(user.role) }}
                </span>
              </td>
              <td>
                <div class="flex items-center gap-2">
                  <span
                    class="w-2 h-2 rounded-full"
                    :class="user.is_active ? 'bg-emerald-400 shadow-lg shadow-emerald-400/50' : 'bg-red-400 shadow-lg shadow-red-400/50'"
                  ></span>
                  <span class="text-sm" :class="user.is_active ? 'text-emerald-400' : 'text-red-400'">
                    {{ user.is_active ? '启用' : '禁用' }}
                  </span>
                </div>
              </td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(user.created_at) }}</td>
              <td>
                <div class="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    @click="editUser(user)"
                    class="p-1.5 rounded-lg hover:bg-cyber-blue/10 text-cyber-blue transition-colors"
                    title="编辑"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click="toggleUserStatus(user)"
                    class="p-1.5 rounded-lg transition-colors"
                    :class="user.is_active ? 'hover:bg-amber-500/10 text-amber-400' : 'hover:bg-emerald-500/10 text-emerald-400'"
                    :title="user.is_active ? '禁用' : '启用'"
                  >
                    <svg v-if="user.is_active" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </button>
                  <button
                    v-if="user.username !== 'admin'"
                    @click="deleteUser(user)"
                    class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
                    title="删除"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="8" class="text-center py-20">
                <div class="space-y-3">
                  <div class="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary-500/10 to-cyber-purple/10 flex items-center justify-center">
                    <svg class="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p class="text-gray-500 text-sm">暂无用户数据</p>
                  <button @click="showCreateDialog" class="cyber-button text-sm px-4 py-2">
                    添加第一个用户
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="dialogVisible" class="fixed inset-0 z-50 overflow-y-auto" @click.self="dialogVisible = false">
          <!-- 背景遮罩 -->
          <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" />

          <!-- 对话框内容 -->
          <div class="relative min-h-screen flex items-center justify-center p-4">
            <div class="relative w-full max-w-lg glass-card p-8 animate-slide-up">
              <!-- 关闭按钮 -->
              <button
                @click="dialogVisible = false"
                class="absolute top-6 right-6 p-2 rounded-xl hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <!-- 标题 -->
              <div class="mb-8">
                <h2 class="text-2xl font-bold gradient-text mb-2">
                  {{ isEdit ? '编辑用户' : '新增用户' }}
                </h2>
                <p class="text-sm text-gray-400">{{ isEdit ? '修改用户信息与权限' : '创建新的系统用户账户' }}</p>
              </div>

              <!-- 表单 -->
              <form @submit.prevent="handleSubmit" class="space-y-5">
                <div class="space-y-1.5">
                  <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">用户名 *</label>
                  <input
                    v-model="form.username"
                    type="text"
                    required
                    placeholder="输入用户名"
                    :disabled="isEdit"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>

                <div class="space-y-1.5">
                  <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">邮箱 *</label>
                  <input
                    v-model="form.email"
                    type="email"
                    required
                    placeholder="输入邮箱地址"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                  />
                </div>

                <div class="space-y-1.5">
                  <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">姓名</label>
                  <input
                    v-model="form.full_name"
                    type="text"
                    placeholder="输入姓名（可选）"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                  />
                </div>

                <div class="space-y-1.5">
                  <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">角色 *</label>
                  <select
                    v-model="form.role"
                    required
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                  >
                    <option value="admin" class="bg-gray-900">管理员</option>
                    <option value="manager" class="bg-gray-900">经理</option>
                    <option value="user" class="bg-gray-900">普通用户</option>
                  </select>
                </div>

                <div v-if="!isEdit" class="space-y-1.5">
                  <label class="text-xs text-gray-500 font-medium uppercase tracking-wide">密码 *</label>
                  <input
                    v-model="form.password"
                    type="password"
                    required
                    placeholder="输入密码（至少6位）"
                    minlength="6"
                    class="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-gray-300 placeholder-gray-600 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                  />
                </div>

                <!-- 提交按钮 -->
                <div class="flex justify-end gap-4 pt-6 mt-6 border-t border-white/5">
                  <button
                    type="button"
                    @click="dialogVisible = false"
                    class="px-8 py-3 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-white/5 border border-white/10 hover:border-white/20 transition-all duration-200"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    :disabled="submitting"
                    class="px-8 py-3 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 disabled:opacity-70 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
                  >
                    <svg v-if="submitting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ submitting ? '提交中...' : (isEdit ? '保存修改' : '创建用户') }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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

const activeUserCount = computed(() => users.value.filter(u => u.is_active).length)
const adminCount = computed(() => users.value.filter(u => u.role === 'admin').length)

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
  try {
    await formRef.value?.validate()
  } catch {
    return
  }

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

function getRoleClass(role) {
  const classes = {
    admin: 'bg-red-500/10 text-red-400 border border-red-500/30 font-semibold',
    manager: 'bg-amber-500/10 text-amber-400 border border-amber-500/30 font-semibold',
    user: 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
  }
  return classes[role] || 'bg-gray-500/10 text-gray-400 border border-gray-500/30'
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .glass-card,
.modal-leave-active .glass-card {
  transition: all 0.3s ease;
}

.modal-enter-from .glass-card {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}

.modal-leave-to .glass-card {
  transform: scale(0.95) translateY(20px);
  opacity: 0;
}
</style>