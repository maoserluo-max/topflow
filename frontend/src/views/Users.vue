<template>
  <div class="min-h-screen p-8 space-y-8">
    <div class="flex items-center justify-between">
      <div class="space-y-1">
        <h1 class="text-4xl font-bold gradient-text">用户管理</h1>
        <p class="text-sm dark:text-gray-400 text-gray-500">管理系统用户账户、角色权限与从属关系</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="generateInviteCode" class="cyber-button flex items-center gap-2 text-sm font-medium !from-emerald-600 !to-teal-600 hover:!from-emerald-500 hover:!to-teal-500">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          生成邀请码
        </button>
        <button v-if="canCreateUser" @click="showCreateDialog" class="cyber-button flex items-center gap-2 text-sm font-medium">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新增用户
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-5 gap-6 animate-in">
      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div>
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">总用户数</p>
              <p class="text-3xl font-bold mt-1 dark:bg-gradient-to-r dark:from-white dark:to-gray-300 bg-gradient-to-r from-gray-800 to-gray-500 bg-clip-text text-transparent">{{ users.length }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div>
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">管理员</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-purple-400 to-pink-300 bg-clip-text text-transparent">{{ adminCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div>
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">组长</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-amber-400 to-orange-300 bg-clip-text text-transparent">{{ leaderCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div>
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">普通用户</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">{{ userCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="stat-card-glow group cursor-pointer hover:scale-[1.02] transition-transform duration-300">
        <div class="flex items-center justify-between">
          <div class="space-y-3">
            <div>
              <p class="text-xs dark:text-gray-400 text-gray-500 uppercase tracking-wider font-medium">活跃用户</p>
              <p class="text-3xl font-bold mt-1 bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">{{ activeUserCount }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 从属关系树形展示 -->
    <div class="glass-card p-6 animate-in" style="animation-delay: 100ms">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold flex items-center gap-2 dark:text-white text-gray-900">
          <span class="w-2 h-2 rounded-full bg-cyber-blue animate-pulse"></span>
          从属关系
        </h3>
        <div class="flex items-center gap-2">
          <select v-model="viewMode" class="px-3 py-1.5 rounded-lg text-sm dark:bg-white/5 dark:border-white/10 dark:text-white bg-white border border-gray-200 text-gray-700">
            <option value="tree">树形视图</option>
            <option value="table">列表视图</option>
          </select>
        </div>
      </div>

      <!-- 树形视图 -->
      <div v-if="viewMode === 'tree'" class="space-y-1">
        <div v-for="user in rootUsers" :key="user.id">
          <UserTreeNode
            :user="user"
            :all-users="users"
            :level="0"
            :current-user="currentUser"
            @edit="editUser"
            @toggle-status="toggleUserStatus"
            @delete="deleteUser"
          />
        </div>
        <div v-if="rootUsers.length === 0" class="text-center py-12 dark:text-gray-500 text-gray-400">
          <div class="space-y-2">
            <div class="text-4xl">👥</div>
            <p>暂无用户数据</p>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-else class="overflow-x-auto scrollbar-hide">
        <table class="data-table-modern">
          <thead>
            <tr>
              <th>用户名</th>
              <th>姓名</th>
              <th>角色</th>
              <th>上级</th>
              <th>从属链</th>
              <th>下属数</th>
              <th>项目权限</th>
              <th>状态</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="user.id" class="group animate-in" :style="{ animationDelay: `${index * 30}ms` }">
              <td>
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold uppercase dark:bg-gradient-to-br dark:from-primary-500/30 dark:to-cyber-purple/30 dark:text-white bg-gradient-to-br from-primary-100 to-purple-100 text-white">
                    {{ (user.username || 'U').charAt(0) }}
                  </div>
                  <span class="font-medium dark:text-white text-gray-900">{{ user.username }}</span>
                </div>
              </td>
              <td class="dark:text-gray-300 text-gray-700">{{ user.full_name || '-' }}</td>
              <td>
                <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold" :class="getRoleClass(user.role)">
                  {{ getRoleName(user.role) }}
                </span>
              </td>
              <td class="text-sm dark:text-gray-400 text-gray-600">
                <span v-if="user.parent_name">{{ user.parent_name }}</span>
                <span v-else class="dark:text-gray-600 text-gray-400">-</span>
              </td>
              <td class="text-xs">
                <div v-if="user.ancestor_chain && user.ancestor_chain.length > 0" class="flex items-center gap-1 flex-wrap">
                  <template v-for="(ancestor, i) in user.ancestor_chain" :key="ancestor.id">
                    <span class="dark:text-gray-400 text-gray-500">{{ ancestor.full_name || ancestor.username }}</span>
                    <svg v-if="i < user.ancestor_chain.length - 1" class="w-3 h-3 dark:text-gray-600 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
                  </template>
                </div>
                <span v-else class="dark:text-gray-600 text-gray-400">-</span>
              </td>
              <td class="text-center">
                <span v-if="user.children_count > 0" class="inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold dark:bg-cyber-blue/10 dark:text-cyber-blue bg-blue-50 text-blue-600">{{ user.children_count }}</span>
                <span v-else class="dark:text-gray-600 text-gray-400">0</span>
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
                  <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-emerald-400 shadow-lg shadow-emerald-400/50' : 'bg-red-400 shadow-lg shadow-red-400/50'"></span>
                  <span class="text-sm" :class="user.is_active ? 'text-emerald-400' : 'text-red-400'">
                    {{ user.is_active ? '启用' : '禁用' }}
                  </span>
                </div>
              </td>
              <td>
                <div class="flex items-center justify-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button @click="editUser(user)" class="p-1.5 rounded-lg hover:bg-cyber-blue/10 text-cyber-blue transition-colors" title="编辑">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                  </button>
                  <button
                    @click="toggleUserStatus(user)"
                    class="p-1.5 rounded-lg transition-colors"
                    :class="user.is_active ? 'hover:bg-amber-500/10 text-amber-400' : 'hover:bg-emerald-500/10 text-emerald-400'"
                    :title="user.is_active ? '禁用' : '启用'"
                  >
                    <svg v-if="user.is_active" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  </button>
                  <button
                    v-if="canDeleteUser(user)"
                    @click="deleteUser(user)"
                    class="p-1.5 rounded-lg hover:bg-red-500/10 text-red-400 transition-colors"
                    title="删除"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="users.length === 0">
              <td colspan="9" class="text-center py-20">
                <div class="space-y-3">
                  <p class="dark:text-gray-500 text-gray-500 text-sm">暂无用户数据</p>
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
      :all-users="users"
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
              <th>注册角色</th>
              <th>项目</th>
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
                <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold" :class="getRoleClass(code.register_role)">
                  {{ getRoleName(code.register_role) }}
                </span>
              </td>
              <td>
                <div class="flex flex-wrap gap-1">
                  <span v-for="p in getCodeProjects(code)" :key="p" class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium dark:bg-primary-500/10 dark:text-primary-300 bg-primary-50 text-primary-600">{{ p }}</span>
                </div>
              </td>
              <td>
                <span v-if="code.is_used" class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold dark:bg-gray-500/15 dark:text-gray-400 bg-gray-100 text-gray-500">已使用</span>
                <span v-else class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold dark:bg-emerald-500/15 dark:text-emerald-400 bg-emerald-50 text-emerald-600">未使用</span>
              </td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(code.created_at) }}</td>
              <td class="text-sm dark:text-gray-400 text-gray-600">
                <span v-if="code.used_user_info">{{ code.used_user_info.full_name || code.used_user_info.username }}</span>
                <span v-else>-</span>
              </td>
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
              <td colspan="8" class="text-center py-12 dark:text-gray-500 text-gray-400">
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
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import UserFormDialog from '@/components/UserFormDialog.vue'
import UserTreeNode from '@/components/UserTreeNode.vue'

const userStore = useUserStore()
const loading = ref(false)
const users = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingUser = ref(null)
const viewMode = ref('tree')

const ROLE_HIERARCHY = { super_admin: 4, admin: 3, leader: 2, user: 1 }

const currentUser = computed(() => userStore.user)
const canCreateUser = computed(() => userStore.isLeaderOrAbove)

const activeUserCount = computed(() => users.value.filter(u => u.is_active).length)
const adminCount = computed(() => users.value.filter(u => ['super_admin', 'admin'].includes(u.role)).length)
const leaderCount = computed(() => users.value.filter(u => u.role === 'leader').length)
const userCount = computed(() => users.value.filter(u => u.role === 'user').length)

// 邀请码相关
const inviteCodes = ref([])
const inviteTotal = ref(0)
const invitePage = ref(1)
const invitePageSize = ref(10)
const invitePages = ref(0)
const inviteFilter = ref('all')

// 树形视图：找出根用户（没有上级的用户）
const rootUsers = computed(() => {
  return users.value.filter(u => !u.parent_id)
})

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

function canDeleteUser(user) {
  const myRole = currentUser.value?.role || ''
  const myLevel = ROLE_HIERARCHY[myRole] || 1
  const userLevel = ROLE_HIERARCHY[user.role] || 1
  if (user.id === currentUser.value?.id) return false
  if (user.role === 'super_admin') return false
  return myLevel > userLevel
}

async function toggleUserStatus(user) {
  try {
    await api.put(`/auth/users/${user.id}`, {
      is_active: !user.is_active
    })
    ElMessage.success(user.is_active ? '已禁用' : '已启用')
    fetchUsers()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
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
      ElMessage.error(error.response?.data?.detail || '删除失败')
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

function getCodeProjects(code) {
  if (!code.projects) return ['Gamoji', 'Poseme', '内容孵化']
  return code.projects.split(',').map(p => p.trim()).filter(p => p)
}

function getRoleName(role) {
  const names = { super_admin: '系统管理员', admin: '管理员', leader: '组长', user: '普通用户' }
  return names[role] || role
}

function getRoleClass(role) {
  const classes = {
    super_admin: 'dark:bg-purple-500/15 dark:text-purple-400 dark:border-purple-500/25 bg-purple-50 text-purple-600 border border-purple-200',
    admin: 'dark:bg-red-500/15 dark:text-red-400 dark:border-red-500/25 bg-red-50 text-red-600 border border-red-200',
    leader: 'dark:bg-amber-500/15 dark:text-amber-400 dark:border-amber-500/25 bg-amber-50 text-amber-600 border border-amber-200',
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
    const data = { register_role: 'leader' }
    // 组长的邀请码继承自己的项目
    if (currentUser.value?.role === 'leader') {
      data.projects = currentUser.value.projects
    }
    await api.post('/auth/invite-codes', data)
    ElMessage.success('邀请码已生成')
    fetchInviteCodes()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  }
}

async function batchGenerateInviteCodes() {
  try {
    const data = { register_role: 'leader' }
    if (currentUser.value?.role === 'leader') {
      data.projects = currentUser.value.projects
    }
    const res = await api.post('/auth/invite-codes/batch?count=5', data)
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
