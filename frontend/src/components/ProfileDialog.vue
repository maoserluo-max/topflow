<template>
  <el-dialog
    v-model="visible"
    title="账户管理"
    width="480px"
    :close-on-click-modal="false"
    @close="resetForm"
  >
    <div class="space-y-5">
      <!-- 姓名修改 -->
      <div class="space-y-1.5">
        <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">姓名</label>
        <input
          v-model="form.full_name"
          type="text"
          placeholder="输入姓名"
          class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
        />
      </div>

      <!-- 修改密码 -->
      <div class="pt-4 dark:border-t dark:border-white/5 border-t border-gray-200">
        <p class="text-sm font-medium dark:text-gray-300 text-gray-700 mb-4">修改密码</p>
        <div class="space-y-4">
          <div class="space-y-1.5">
            <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">当前密码</label>
            <input
              v-model="form.current_password"
              type="password"
              placeholder="输入当前密码"
              class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
            />
          </div>
          <div class="space-y-1.5">
            <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">新密码</label>
            <input
              v-model="form.new_password"
              type="password"
              placeholder="输入新密码（至少6位）"
              minlength="6"
              class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
            />
          </div>
          <div class="space-y-1.5">
            <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">确认新密码</label>
            <input
              v-model="form.confirm_password"
              type="password"
              placeholder="再次输入新密码"
              class="w-full px-4 py-3 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-gray-300 dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-700 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
            />
          </div>
          <p class="text-xs dark:text-gray-600 text-gray-400">如不修改密码，密码相关字段请留空</p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <button
          @click="visible = false"
          class="px-6 py-2.5 rounded-xl text-sm font-medium dark:text-gray-400 dark:hover:text-white dark:hover:bg-white/5 dark:border-white/10 text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-gray-200 transition-all"
        >
          取消
        </button>
        <button
          @click="handleSave"
          :disabled="saving"
          class="px-6 py-2.5 rounded-xl text-sm font-medium bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white shadow-lg shadow-primary-500/25 disabled:opacity-70 disabled:cursor-not-allowed transition-all flex items-center gap-2"
        >
          <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          保存
        </button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api, { getErrorMsg } from '@/utils/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const visible = ref(false)
const saving = ref(false)

const form = reactive({
  full_name: '',
  current_password: '',
  new_password: '',
  confirm_password: ''
})

function open() {
  form.full_name = userStore.user?.full_name || ''
  form.current_password = ''
  form.new_password = ''
  form.confirm_password = ''
  visible.value = true
}

function resetForm() {
  form.current_password = ''
  form.new_password = ''
  form.confirm_password = ''
}

defineExpose({ open })

async function handleSave() {
  // 如果要修改密码，需要验证
  if (form.new_password) {
    if (!form.current_password) {
      ElMessage.warning('修改密码需要输入当前密码')
      return
    }
    if (form.new_password.length < 6) {
      ElMessage.warning('新密码至少6位')
      return
    }
    if (form.new_password !== form.confirm_password) {
      ElMessage.warning('两次输入的新密码不一致')
      return
    }
  }

  saving.value = true
  try {
    const data = {
      full_name: form.full_name
    }
    if (form.new_password) {
      data.current_password = form.current_password
      data.new_password = form.new_password
    }

    const response = await api.put('/auth/me/profile', data)
    // 更新本地用户信息
    await userStore.fetchCurrentUser()
    ElMessage.success('账户信息更新成功')
    visible.value = false
  } catch (error) {
    ElMessage.error(getErrorMsg(error))
  } finally {
    saving.value = false
  }
}
</script>
