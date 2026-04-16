<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden dark:bg-gray-950 bg-gray-50">
    <div class="absolute inset-0 bg-grid-pattern opacity-[0.03]"></div>
    <div v-if="themeStore.isDark" class="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-primary-500/20 rounded-full blur-[120px] animate-pulse"></div>
    <div v-if="themeStore.isDark" class="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-cyber-purple/20 rounded-full blur-[120px] animate-pulse" style="animation-delay: 1s"></div>

    <div class="relative z-10 w-full max-w-md mx-4 animate-in">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-primary-500 to-cyber-purple shadow-2xl shadow-primary-500/30 mb-6">
          <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
        </div>
        <h1 class="text-4xl font-bold gradient-text mb-2">TopFlow</h1>
        <p class="dark:text-gray-400 text-gray-500 text-sm">注册新账号</p>
      </div>

      <div class="glass-card p-8 space-y-5">
        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">邀请码</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 dark:text-gray-500 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" /></svg>
            </div>
            <input v-model="form.invite_code" type="text" placeholder="请输入邀请码" class="w-full pl-12 pr-4 py-3.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-white dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-900 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all" @keyup.enter="handleRegister" />
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">用户名</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 dark:text-gray-500 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            </div>
            <input v-model="form.username" type="text" placeholder="请输入用户名" class="w-full pl-12 pr-4 py-3.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-white dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-900 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all" @keyup.enter="handleRegister" />
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">邮箱</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 dark:text-gray-500 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            </div>
            <input v-model="form.email" type="email" placeholder="请输入邮箱" class="w-full pl-12 pr-4 py-3.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-white dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-900 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all" @keyup.enter="handleRegister" />
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">姓名（选填）</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 dark:text-gray-500 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <input v-model="form.full_name" type="text" placeholder="请输入真实姓名" class="w-full pl-12 pr-4 py-3.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-white dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-900 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all" @keyup.enter="handleRegister" />
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs dark:text-gray-500 text-gray-600 font-medium uppercase tracking-wide">密码</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="w-5 h-5 dark:text-gray-500 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
            </div>
            <input v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="请输入密码（至少6位）" class="w-full pl-12 pr-12 py-3.5 rounded-xl dark:bg-white/5 dark:border-white/10 dark:text-white dark:placeholder-gray-600 bg-white border border-gray-200 text-gray-900 placeholder-gray-400 focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all" @keyup.enter="handleRegister" />
            <button @click="showPassword = !showPassword" class="absolute inset-y-0 right-0 pr-4 flex items-center dark:text-gray-500 dark:hover:text-gray-300 text-gray-400 hover:text-gray-600 transition-colors">
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
            </button>
          </div>
        </div>

        <div v-if="errorMsg" class="flex items-center gap-2 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          {{ errorMsg }}
        </div>

        <div v-if="successMsg" class="flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          {{ successMsg }}
        </div>

        <button @click="handleRegister" :disabled="loading" class="w-full py-3.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-primary-600 to-cyber-purple hover:from-primary-500 hover:to-cyber-purple/90 text-white shadow-lg shadow-primary-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
          <div v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          <span>{{ loading ? '注册中...' : '注 册' }}</span>
        </button>
      </div>

      <div class="mt-6 text-center">
        <router-link to="/login" class="text-sm dark:text-gray-400 text-gray-500 hover:text-cyber-blue dark:hover:text-cyber-blue transition-colors">
          已有账号？返回登录
        </router-link>
      </div>

      <div class="mt-4 text-center">
        <p class="dark:text-gray-600 text-gray-400 text-xs">&copy; 2024 TopFlow. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()

const form = reactive({ username: '', email: '', password: '', full_name: '', invite_code: '' })
const loading = ref(false)
const showPassword = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

async function handleRegister() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!form.invite_code) { errorMsg.value = '请输入邀请码'; return }
  if (!form.username) { errorMsg.value = '请输入用户名'; return }
  if (!form.email) { errorMsg.value = '请输入邮箱'; return }
  if (!form.password || form.password.length < 6) { errorMsg.value = '密码至少6位'; return }

  loading.value = true
  try {
    await userStore.register(form)
    successMsg.value = '注册成功！正在跳转登录页...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (error) {
    errorMsg.value = error.response?.data?.detail || '注册失败，请检查信息'
  } finally {
    loading.value = false
  }
}
</script>
