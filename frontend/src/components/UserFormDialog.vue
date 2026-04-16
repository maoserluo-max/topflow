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

              <div class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">角色 *</label>
                <select
                  v-model="form.role"
                  required
                  class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                >
                  <option value="admin" class="dark:bg-gray-900 bg-white">管理员</option>
                  <option value="manager" class="dark:bg-gray-900 bg-white">经理</option>
                  <option value="user" class="dark:bg-gray-900 bg-white">普通用户</option>
                </select>
              </div>

              <div class="space-y-1.5">
                <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">项目权限</label>
                <div class="flex flex-wrap gap-2">
                  <label
                    v-for="p in allProjects"
                    :key="p"
                    class="flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer transition-all dark:bg-white/5 dark:border-white/10 dark:text-gray-300 bg-white border border-gray-200 text-gray-700 dark:hover:bg-white/10 hover:bg-gray-50"
                    :class="{ 'dark:!bg-primary-500/20 !bg-primary-50 dark:!border-primary-500/40 !border-primary-300 dark:!text-primary-300 !text-primary-700': form.selectedProjects.includes(p) }"
                  >
                    <input
                      type="checkbox"
                      :value="p"
                      v-model="form.selectedProjects"
                      class="w-4 h-4 rounded accent-primary-500"
                    />
                    <span class="text-sm font-medium">{{ p }}</span>
                  </label>
                </div>
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
import { ref, reactive, watch } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: Boolean,
  isEdit: Boolean,
  editData: { type: Object, default: null }
})

const emit = defineEmits(['close', 'submitted'])

const submitting = ref(false)

const allProjects = ['Gamoji', 'Poseme', '内容孵化']

const defaultForm = {
  username: '',
  email: '',
  full_name: '',
  role: 'user',
  password: '',
  selectedProjects: ['Gamoji', 'Poseme', '内容孵化']
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
        password: '',
        selectedProjects: props.editData.projects ? props.editData.projects.split(',').map(p => p.trim()).filter(p => p) : ['Gamoji', 'Poseme', '内容孵化']
      })
    } else {
      Object.assign(form, { ...defaultForm })
    }
  }
})

async function handleSubmit() {
  submitting.value = true
  try {
    const data = { ...form }
    data.projects = data.selectedProjects.join(',')
    delete data.selectedProjects
    if (props.isEdit) {
      delete data.password
      if (!data.email) delete data.email
      await api.put(`/auth/users/${props.editData.id}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post('/auth/users', data)
      ElMessage.success('创建成功')
    }
    emit('submitted')
    emit('close')
  } catch (error) {
    console.error('Submit error:', error)
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
