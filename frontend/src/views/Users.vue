<template>
  <div class="min-h-screen p-8 space-y-8">
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h1 class="text-4xl font-bold gradient-text">用户管理</h1>
        <p class="text-sm dark:text-gray-400 text-gray-500">管理系统用户账户、角色权限与状态</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="generateInviteCode" class="cyber-button flex items-center gap-2 text-sm font-medium !from-emerald-600 !to-teal-600 hover:!from-emerald-500 hover:!to-teal-500">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          生成邀请码
        </button>
        <button @click="showCreateDialog" class="cyber-button flex items-center gap-2 text-sm font-medium">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新增用户
        </button>
      </div>
    </div>

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
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">总用户数</p>
              <p class="text-3xl font-bold mt-1 dark:bg-gradient-to-r dark:from-white dark:to-gray-300 bg-gradient-to-r from-gray-800 to-gray-500 bg-clip-text text-transparent">{{ users.length }}</p>
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
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">活跃用户</p>
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
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">管理员</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-primary-400 to-purple-300 bg-clip-text text-transparent">{{ adminCount }}</p>
            </div>
          </div>
          <div class="w-full h-20 opacity-10 absolute right-0 top-0 rounded-r-2xl bg-gradient-to-l from-primary-500 to-transparent"></div>
        </div>
      </div>
    </div>

    <div class="glass-card overflow-hidden animate-in" style="animation-delay: 100ms">
      <div v-if="loading" class="flex items-center justify-center py-20">
        <div class="space-y-4 text-center">
          <div class="w-12 h-12 mx-auto border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <p class="dark:text-gray-400 text-gray-500 text-sm">加载用户数据中...</p>
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
              <th>项目权限</th>
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
                  <div class="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold uppercase dark:bg-gradient-to-br dark:from-primary-500/30 dark:to-cyber-purple/30 dark:text-white bg-gradient-to-br from-primary-100 to-purple-100 text-white">
                    {{ (user.username || 'U').charAt(0) }}
                  </div>
                  <span class="font-medium dark:text-white text-gray-900">{{ user.username }}</span>
                </div>
              </td>
              <td class="dark:text-gray-400 text-gray-600 text-sm">{{ user.email || '-' }}</td>
              <td class="dark:text-gray-300 text-gray-700">{{ user.full_name || '-' }}</td>
              <td>
                <span
                  class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
                  :class="getRoleClass(user.role)"
                >
                  {{ getRoleName(user.role) }}
                </span>
              </td>
              <td>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="p in getUserProjects(user)"
                    :key="p"
                    class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium dark:bg-primary-500/15 dark:text-primary-300 dark:border dark:border-primary-500/25 bg-primary-50 text-primary-600 border border-primary-200"
                  >
                    {{ p }}
                  </span>
                </div>
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
              <td colspan="9" class="text-center py-20">
                <div class="space-y-3">
                  <div class="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary-500/10 to-cyber-purple/10 flex items-center justify-center">
                    <svg class="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p class="dark:text-gray-500 text-gray-500 text-sm">暂无用户数据</p>
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

    <UserFormDialog
      :visible="dialogVisible"
      :is-edit="isEdit"
      :edit-data="editingUser"
      @close="dialogVisible = false"
      @submitted="onDialogSubmitted"
    />

    <!-- 邀请码管理 -->
    <div class="glass-card p-6 animate-in" style="animation-delay: 200ms">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold flex items-center gap-2 dark:text-white text-gray-900">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          邀请码管理
        </h3>
        <div class="flex items-center gap-3">
          <select v-model="inviteFilter" @change="fetchInviteCodes" class="px-3 py-1.5 rounded-lg text-sm dark:bg-white/5 dark:border-white/10 dark:text-white bg-white border border-gray-200 text-gray-700">
            <option value="all">全部</option>
            <option value="unused">未使用</option>
            <option value="used">已使用</option>
          </select>
          <button @click="batchGenerateInviteCodes" class="cyber-button text-xs px-3 py-1.5 !from-emerald-600 !to-teal-600">
            批量生成
          </button>
          <button @click="fetchInviteCodes" class="p-1.5 rounded-lg dark:hover:bg-white/5 hover:bg-gray-100 dark:text-gray-400 text-gray-500 transition-colors" title="刷新">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          </button>
        </div>
      </div>

      <div class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>邀请码</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>使用者</th>
              <th>使用时间</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="code in inviteCodes" :key="code.id" class="group">
              <td>
                <div class="flex items-center gap-2">
                  <code class="px-2.5 py-1 rounded-lg text-sm font-mono font-bold dark:bg-primary-500/10 dark:text-primary-300 bg-primary-50 text-primary-600">{{ code.code }}</code>
                  <button @click="copyCode(code.code)" class="p-1 rounded dark:hover:bg-white/10 hover:bg-gray-100 dark:text-gray-500 text-gray-400 transition-colors" title="复制">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                  </button>
                </div>
              </td>
              <td>
                <span v-if="code.is_used" class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold dark:bg-gray-500/15 dark:text-gray-400 bg-gray-100 text-gray-500">已使用</span>
                <span v-else class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold dark:bg-emerald-500/15 dark:text-emerald-400 bg-emerald-50 text-emerald-600">未使用</span>
              </td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(code.created_at) }}</td>
              <td class="text-sm dark:text-gray-400 text-gray-600">{{ code.used_by ? `用户#${code.used_by}` : '-' }}</td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ code.used_at ? formatDate(code.used_at) : '-' }}</td>
              <td>
                <div class="flex items-center justify-center">
                  <button v-if="!code.is_used" @click="deleteInviteCode(code)" class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors opacity-0 group-hover:opacity-100" title="删除">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="inviteCodes.length === 0">
              <td colspan="6" class="text-center py-12 dark:text-gray-500 text-gray-400">
                <div class="space-y-2">
                  <div class="text-4xl">🎫</div>
                  <p>暂无邀请码</p>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="inviteTotal > invitePageSize" class="flex items-center justify-between mt-4 pt-4 dark:border-white/5 border-t border-gray-200">
        <p class="text-sm dark:text-gray-500 text-gray-400">共 {{ inviteTotal }} 条</p>
        <div class="flex items-center gap-2">
          <button @click="invitePage > 1 && (invitePage--, fetchInviteCodes())" :disabled="invitePage <= 1" class="px-3 py-1.5 rounded-lg text-sm dark:bg-white/5 dark:hover:bg-white/10 dark:disabled:opacity-30 bg-gray-100 hover:bg-gray-200 disabled:opacity-30 transition-colors">上一页</button>
          <span class="text-sm dark:text-gray-400 text-gray-500">{{ invitePage }} / {{ invitePages }}</span>
          <button @click="invitePage < invitePages && (invitePage++, fetchInviteCodes())" :disabled="invitePage >= invitePages" class="px-3 py-1.5 rounded-lg text-sm dark:bg-white/5 dark:hover:bg-white/10 dark:disabled:opacity-30 bg-gray-100 hover:bg-gray-200 disabled:opacity-30 transition-colors">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useThemeStore } from '@/stores/theme'
import UserFormDialog from '@/components/UserFormDialog.vue'

const themeStore = useThemeStore()
const loading = ref(false)
const users = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingUser = ref(null)

// 邀请码相关
const inviteCodes = ref([])
const inviteTotal = ref(0)
const invitePage = ref(1)
const invitePageSize = ref(10)
const invitePages = ref(0)
const inviteFilter = ref('all')

const activeUserCount = computed(() => users.value.filter(u => u.is_active).length)
const adminCount = computed(() => users.value.filter(u => u.role === 'admin').length)

onMounted(() => {
  fetchUsers()
  fetchInviteCodes()
})

async function fetchUsers() {
  loading.value = true
  try {
    const response = await api.get('/auth/users')
    users.value = Array.isArray(response) ? response : (response.items || [])
  } catch (error) {
    console.error('Fetch users error:', error)
  } finally {
    loading.value = false
  }
}

function showCreateDialog() {
  isEdit.value = false
  editingUser.value = null
  dialogVisible.value = true
}

function editUser(user) {
  isEdit.value = true
  editingUser.value = { ...user }
  dialogVisible.value = true
}

function onDialogSubmitted() {
  fetchUsers()
}

async function toggleUserStatus(user) {
  try {
    await api.put(`/auth/users/${user.id}`, {
      is_active: !user.is_active
    })
    ElMessage.success(user.is_active ? '已禁用' : '已启用')
    fetchUsers()
  } catch (error) {
    console.error('Toggle status error:', error)
  }
}

function deleteUser(user) {
  ElMessageBox.confirm(`确定要删除用户"${user.username}"吗？`, '提示', {
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

function getUserProjects(user) {
  if (!user.projects) return ['Gamoji', 'Poseme', '内容孵化']
  return user.projects.split(',').map(p => p.trim()).filter(p => p)
}

function getRoleName(role) {
  const names = { admin: '管理员', manager: '经理', user: '用户' }
  return names[role] || role
}

function getRoleClass(role) {
  const classes = {
    admin: 'dark:bg-red-500/15 dark:text-red-400 dark:border-red-500/25 bg-red-50 text-red-600 border border-red-200',
    manager: 'dark:bg-amber-500/15 dark:text-amber-400 dark:border-amber-500/25 bg-amber-50 text-amber-600 border border-amber-200',
    user: 'dark:bg-blue-500/15 dark:text-blue-400 dark:border-blue-500/25 bg-blue-50 text-blue-600 border border-blue-200'
  }
  return classes[role] || 'dark:bg-gray-500/15 dark:text-gray-400 dark:border-gray-500/25 bg-gray-100 text-gray-600 border border-gray-200'
}

// 邀请码相关函数
async function fetchInviteCodes() {
  try {
    const params = { page: invitePage.value, page_size: invitePageSize.value }
    if (inviteFilter.value === 'unused') params.is_used = false
    else if (inviteFilter.value === 'used') params.is_used = true
    const res = await api.get('/auth/invite-codes', { params })
    inviteCodes.value = res.items || []
    inviteTotal.value = res.total || 0
    invitePages.value = res.pages || 0
  } catch (error) {
    console.error('Fetch invite codes error:', error)
  }
}

async function generateInviteCode() {
  try {
    await api.post('/auth/invite-codes')
    ElMessage.success('邀请码已生成')
    fetchInviteCodes()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  }
}

async function batchGenerateInviteCodes() {
  try {
    const res = await api.post('/auth/invite-codes/batch?count=5')
    ElMessage.success(`已生成 ${res.length} 个邀请码`)
    fetchInviteCodes()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '批量生成失败')
  }
}

async function deleteInviteCode(code) {
  try {
    await api.delete(`/auth/invite-codes/${code.id}`)
    ElMessage.success('邀请码已删除')
    fetchInviteCodes()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

function copyCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('邀请码已复制到剪贴板')
  }).catch(() => {
    ElMessage.warning('复制失败，请手动复制')
  })
}
</script>
