<template>
  <el-dialog
    v-model="visible"
    title="邀请码管理"
    width="800px"
    :close-on-click-modal="false"
    @open="loadInviteCodes"
  >
    <!-- 生成邀请码 -->
    <div class="mb-6 p-4 rounded-xl dark:bg-white/[0.02] bg-gray-50 border dark:border-white/5 border-gray-200">
      <h4 class="text-sm font-semibold dark:text-gray-300 text-gray-700 mb-4">生成新邀请码</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">注册角色</label>
          <select v-model="newCode.register_role" class="w-full px-3 py-2 rounded-lg text-sm dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-primary-500/50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all">
            <option v-for="r in allowedRegisterRoles" :key="r.value" :value="r.value" class="dark:bg-gray-900">{{ r.label }}</option>
          </select>
        </div>
        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">项目权限</label>
          <div class="flex flex-wrap gap-2 mt-1">
            <label v-for="p in availableProjects" :key="p" class="inline-flex items-center gap-1.5 cursor-pointer">
              <input type="checkbox" :value="p" v-model="selectedProjects" :disabled="isAdminRole" class="rounded dark:bg-white/5 dark:border-white/20 border-gray-300 text-primary-600 focus:ring-primary-500" />
              <span class="text-sm dark:text-gray-300 text-gray-700">{{ p }}</span>
            </label>
            <p v-if="isAdminRole" class="text-xs dark:text-gray-600 text-gray-400 w-full mt-1">管理员默认拥有所有项目</p>
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium">批量生成数量</label>
          <el-input-number v-model="newCode.count" :min="1" :max="20" size="default" class="!w-full" />
        </div>
      </div>
      <div class="mt-4 flex justify-end">
        <el-button type="primary" @click="generateCodes" :loading="generating">
          {{ newCode.count > 1 ? `生成 ${newCode.count} 个邀请码` : '生成邀请码' }}
        </el-button>
      </div>
    </div>

    <!-- 邀请码列表 -->
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-sm font-semibold dark:text-gray-300 text-gray-700">我的邀请码</h4>
        <div class="flex gap-2">
          <el-select v-model="filterUsed" placeholder="筛选" size="small" style="width: 120px">
            <el-option label="全部" :value="null" />
            <el-option label="未使用" :value="false" />
            <el-option label="已使用" :value="true" />
          </el-select>
        </div>
      </div>

      <div v-if="loadingCodes" class="text-center py-8">
        <div class="w-8 h-8 mx-auto border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
      </div>

      <div v-else-if="inviteCodes.length === 0" class="text-center py-8 dark:text-gray-500 text-gray-400 text-sm">
        暂无邀请码
      </div>

      <div v-else class="space-y-2">
        <div
          v-for="code in inviteCodes"
          :key="code.id"
          class="p-4 rounded-xl border transition-colors"
          :class="code.is_used ? 'dark:border-white/5 border-gray-200 opacity-60' : 'dark:border-primary-500/20 border-primary-200 dark:bg-primary-500/[0.02] bg-primary-50/50'"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-3">
              <code class="px-3 py-1 rounded-lg text-sm font-mono font-bold dark:bg-white/5 bg-white border dark:border-white/10 border-gray-200 tracking-widest">{{ code.code }}</code>
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium"
                :class="code.is_used
                  ? 'dark:bg-gray-500/10 dark:text-gray-400 bg-gray-100 text-gray-500'
                  : 'dark:bg-emerald-500/10 dark:text-emerald-400 bg-emerald-50 text-emerald-600'"
              >
                {{ code.is_used ? '已使用' : '未使用' }}
              </span>
              <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium dark:bg-blue-500/10 dark:text-blue-400 bg-blue-50 text-blue-600">
                {{ getRoleName(code.register_role) }}
              </span>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-if="!code.is_used"
                @click="copyCode(code.code)"
                class="px-3 py-1.5 rounded-lg text-xs font-medium dark:bg-white/5 dark:text-gray-300 dark:hover:bg-white/10 bg-white text-gray-600 hover:bg-gray-100 border dark:border-white/10 border-gray-200 transition-colors"
              >
                复制
              </button>
              <button
                v-if="!code.is_used"
                @click="deleteCode(code.id)"
                class="px-3 py-1.5 rounded-lg text-xs font-medium text-red-400 hover:bg-red-500/10 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
          <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs dark:text-gray-500 text-gray-400">
            <span>项目: {{ code.projects || '默认' }}</span>
            <span>创建时间: {{ formatDate(code.created_at) }}</span>
            <span v-if="code.is_used && code.used_user_info">
              注册用户: <strong class="dark:text-gray-300 text-gray-600">{{ code.used_user_info.full_name || code.used_user_info.username }}</strong>
              ({{ code.used_user_info.email }})
            </span>
            <span v-if="code.is_used && code.used_at">使用时间: {{ formatDate(code.used_at) }}</span>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="flex items-center justify-between pt-4">
        <span class="text-xs dark:text-gray-500 text-gray-400">共 {{ total }} 条</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          small
          @current-change="loadInviteCodes"
        />
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const visible = ref(false)
const loadingCodes = ref(false)
const generating = ref(false)
const inviteCodes = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 20
const filterUsed = ref(null)

const ROLE_HIERARCHY = { admin: 3, leader: 2, user: 1 }

// 根据当前用户角色确定可选的注册角色（管理员和组长可生成邀请码）
const allowedRegisterRoles = computed(() => {
  const role = userStore.user?.role || 'user'
  if (role === 'admin') {
    return [
      { value: 'leader', label: '组长' },
      { value: 'user', label: '普通用户' }
    ]
  } else if (role === 'leader') {
    return [
      { value: 'user', label: '普通用户' }
    ]
  }
  return []
})

// 当前用户可选择的项目（管理员默认所有，组长只能选自己的项目）
const availableProjects = computed(() => {
  const role = userStore.user?.role || 'user'
  if (role === 'admin') {
    return ['Gamoji', 'Poseme', '内容孵化']
  }
  return userStore.userProjects
})

const isAdminRole = computed(() => newCode.register_role === 'admin')

const selectedProjects = ref(['Gamoji', 'Poseme', '内容孵化'])

const newCode = reactive({
  register_role: 'user',
  count: 1,
})

// 管理员及以上角色自动选中所有项目
watch(() => newCode.register_role, (val) => {
  if (val === 'admin') {
    selectedProjects.value = ['Gamoji', 'Poseme', '内容孵化']
  }
})

function open() {
  selectedProjects.value = [...userStore.userProjects]
  newCode.register_role = 'user'
  visible.value = true
}

defineExpose({ open })

async function loadInviteCodes() {
  loadingCodes.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
    }
    if (filterUsed.value !== null) {
      params.is_used = filterUsed.value
    }
    const res = await api.get('/auth/invite-codes', { params })
    inviteCodes.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('Load invite codes error:', error)
  } finally {
    loadingCodes.value = false
  }
}

async function generateCodes() {
  generating.value = true
  try {
    const data = {
      register_role: newCode.register_role,
      projects: selectedProjects.value.join(','),
    }
    if (newCode.count > 1) {
      await api.post(`/auth/invite-codes/batch?count=${newCode.count}`, data)
      ElMessage.success(`成功生成 ${newCode.count} 个邀请码`)
    } else {
      await api.post('/auth/invite-codes', data)
      ElMessage.success('邀请码生成成功')
    }
    await loadInviteCodes()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '生成失败')
  } finally {
    generating.value = false
  }
}

async function deleteCode(id) {
  try {
    await ElMessageBox.confirm('确定要删除该邀请码吗？', '确认', { type: 'warning' })
    await api.delete(`/auth/invite-codes/${id}`)
    ElMessage.success('删除成功')
    await loadInviteCodes()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function copyCode(code) {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('邀请码已复制到剪贴板')
  }).catch(() => {
    ElMessage.warning('复制失败，请手动复制')
  })
}

function getRoleName(role) {
  const names = { admin: '管理员', leader: '组长', user: '普通用户' }
  return names[role] || role || '普通用户'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>
