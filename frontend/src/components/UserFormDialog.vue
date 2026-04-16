<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity" />

        <div class="relative min-h-screen flex items-center justify-center p-4">
          <div class="relative w-full max-w-lg glass-card p-8 animate-slide-up">
            <button
              @click="$emit('close')"
              class="absolute top-6 right-6 p-2 rounded-xl dark:hover:bg-white/10 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="mb-8">
              <h2 class="text-2xl font-bold gradient-text mb-2">
                {{ isEdit ? '编辑用户' : '新增用户' }}
              </h2>
              <p class="text-sm dark:text-gray-400 text-gray-500">{{ isEdit ? '修改用户信息与权限' : '创建新的系统用户账户' }}</p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-5">
              <div class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">用户名 *</label>
                <input
                  v-model="form.username"
                  type="text"
                  required
                  placeholder="输入用户名"
                  :disabled="isEdit"
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>

              <div class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">邮箱 *</label>
                <input
                  v-model="form.email"
                  type="email"
                  required
                  placeholder="输入邮箱地址"
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                />
              </div>

              <div class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">姓名</label>
                <input
                  v-model="form.full_name"
                  type="text"
                  placeholder="输入姓名（可选）"
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                />
              </div>

              <div v-if="canChangeRole" class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">角色 *</label>
                <select
                  v-model="form.role"
                  required
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                >
                  <option v-for="r in availableRoles" :key="r.value" :value="r.value" class="dark:bg-gray-900 bg-white">{{ r.label }}</option>
                </select>
              </div>

              <div class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">上级</label>
                <select
                  v-model="form.parent_id"
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                >
                  <option :value="0" class="dark:bg-gray-900 bg-white">无</option>
                  <option v-for="p in parentCandidates" :key="p.id" :value="p.id" class="dark:bg-gray-900 bg-white">
                    {{ p.full_name || p.username }}（{{ getRoleName(p.role) }}）
                  </option>
                </select>
                <p class="text-xs dark:text-gray-600 text-gray-400 mt-1">上级角色必须高于当前用户角色</p>
              </div>

              <div v-if="canChangeProjects" class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">项目权限</label>
                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="p in availableProjects"
                    :key="p"
                    class="flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer transition-all dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 dark:hover:bg-white/10 hover:bg-gray-50"
                    :class="{ 'dark:!bg-primary-500/20 !bg-primary-50 dark:!border-primary-500/40 !border-primary-300 dark:!text-primary-300 !text-primary-700': form.selectedProjects.includes(p), 'opacity-50 cursor-not-allowed': isAdminRole }"
                  >
                    <input
                      type="checkbox"
                      :value="p"
                      v-model="form.selectedProjects"
                      :disabled="isAdminRole"
                      class="w-4 h-4 rounded accent-primary-500"
                    />
                    <span class="text-sm font-medium">{{ p }}</span>
                  </label>
                </div>
                <p v-if="isAdminRole" class="text-xs dark:text-gray-600 text-gray-400 mt-1">管理员默认拥有所有项目权限</p>
              </div>

              <div v-if="!isEdit" class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">密码 *</label>
                <input
                  v-model="form.password"
                  type="password"
                  required
                  placeholder="输入密码（至少6位）"
                  minlength="6"
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                />
              </div>

              <div v-if="isEdit" class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">重置密码</label>
                <input
                  v-model="form.password"
                  type="password"
                  placeholder="留空则不修改密码"
                  minlength="6"
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                />
              </div>

              <div class="flex justify-end gap-4 pt-6 mt-6 dark:border-t dark:border-white/5 border-t border-gray-200">
                <button
                  type="button"
                  @click="$emit('close')"
                  class="px-8 py-3 rounded-xl text-sm font-medium dark:text-gray-400 dark:hover:text-white dark:hover:bg-white/5 dark:border-white/10 dark:hover:border-white/20 text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 hover:border-gray-300 transition-all duration-200"
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
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import api, { getErrorMsg } from '@/utils/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const props = defineProps({
  visible: Boolean,
  isEdit: Boolean,
  editData: { type: Object, default: null },
  allUsers: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'submitted'])

const userStore = useUserStore()
const submitting = ref(false)

const ROLE_HIERARCHY = { admin: 3, leader: 2, user: 1 }

const allRoles = [
  { value: 'admin', label: '管理员' },
  { value: 'leader', label: '组长' },
  { value: 'user', label: '普通用户' }
]

// 当前用户可以创建的角色：管理员可创建同级及以下，组长只能创建低于自身的角色
const availableRoles = computed(() => {
  const currentRole = userStore.user?.role || 'user'
  const currentLevel = ROLE_HIERARCHY[currentRole] || 1
  // 管理员可以创建同级（admin）及以下角色，组长只能创建低于自身的角色
  if (currentRole === 'admin') {
    return allRoles.filter(r => ROLE_HIERARCHY[r.value] <= currentLevel)
  }
  return allRoles.filter(r => ROLE_HIERARCHY[r.value] < currentLevel)
})

// 当前用户可以选择的项目（管理员默认所有，组长只能分配自己拥有的项目）
const availableProjects = computed(() => {
  const currentRole = userStore.user?.role || 'user'
  if (['admin'].includes(currentRole)) {
    return ['Gamoji', 'Poseme', '内容孵化']
  }
  // 组长只能分配自己拥有的项目
  return userStore.userProjects
})

// 是否可以修改角色（组长及以上可修改）
const canChangeRole = computed(() => {
  const currentRole = userStore.user?.role || 'user'
  return ['admin', 'leader'].includes(currentRole)
})

// 是否可以修改项目权限（管理员和组长可修改）
const canChangeProjects = computed(() => {
  const currentRole = userStore.user?.role || 'user'
  return ['admin', 'leader'].includes(currentRole)
})

const isAdminRole = computed(() => form.role === 'admin')

// 可选的上级候选人：角色级别高于或等于当前选择的角色（管理员可以选管理员作为上级）
const parentCandidates = computed(() => {
  const selectedLevel = ROLE_HIERARCHY[form.role] || 1
  const currentRole = userStore.user?.role || 'user'
  return props.allUsers.filter(u => {
    const level = ROLE_HIERARCHY[u.role] || 1
    // 管理员创建管理员时，同级别的管理员也可以作为上级
    if (currentRole === 'admin' && form.role === 'admin') {
      return level >= selectedLevel && u.id !== props.editData?.id
    }
    return level > selectedLevel && u.id !== props.editData?.id
  })
})

function getRoleName(role) {
  const names = { admin: '管理员', leader: '组长', user: '普通用户' }
  return names[role] || role
}

// 新角色体系下，默认创建普通用户
const defaultForm = {
  username: '',
  email: '',
  full_name: '',
  role: 'user',
  parent_id: 0,
  password: '',
  selectedProjects: [...userStore.userProjects]
}

const form = reactive({ ...defaultForm })

watch(() => props.visible, (val) => {
  if (val) {
    if (props.isEdit && props.editData) {
      Object.assign(form, {
        username: props.editData.username,
        email: props.editData.email || '',
        full_name: props.editData.full_name || '',
        role: props.editData.role,
        parent_id: props.editData.parent_id || 0,
        password: '',
        selectedProjects: props.editData.projects ? props.editData.projects.split(',').map(p => p.trim()).filter(p => p) : ['Gamoji', 'Poseme', '内容孵化']
      })
    } else {
      Object.assign(form, { ...defaultForm })
      // 新建时，默认上级为当前用户
      form.parent_id = userStore.user?.id || 0
    }
  }
})

// 当角色为管理员及以上时，自动选中所有项目
watch(() => form.role, (val) => {
  if (val === 'admin') {
    form.selectedProjects = ['Gamoji', 'Poseme', '内容孵化']
  }
})

async function handleSubmit() {
  submitting.value = true
  try {
    const data = { ...form }
    data.projects = data.selectedProjects.join(',')
    delete data.selectedProjects
    // 处理 parent_id：0或空值时不传（让后端自动设为当前用户）
    if (!data.parent_id || data.parent_id === 0) {
      delete data.parent_id
    }
    // 处理 full_name：空字符串不传
    if (!data.full_name) {
      delete data.full_name
    }
    if (props.isEdit) {
      if (!data.email) delete data.email
      // 密码为空则不传
      if (!data.password) delete data.password
      await api.put(`/auth/users/${props.editData.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/auth/users', data)
      ElMessage.success('创建成功')
    }
    emit('submitted')
    emit('close')
  } catch (error) {
    ElMessage.error(getErrorMsg(error))
  } finally {
    submitting.value = false
  }
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
