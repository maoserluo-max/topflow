<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden transition-colors duration-300" :class="themeStore.isDark ? 'bg-gray-950' : 'bg-gradient-to-br from-gray-100 to-gray-200'">
    <!-- 背景装饰 -->
    <div v-if="themeStore.isDark" class="absolute inset-0 overflow-hidden">
      <div class="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
      <div class="absolute top-0 left-1/4 w-[600px] h-[600px] rounded-full bg-primary-500/10 blur-[120px] animate-pulse-slow"></div>
      <div class="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full bg-cyber-purple/10 blur-[100px] animate-pulse-slow" style="animation-delay: 2s"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-cyber-blue/5 blur-[80px] animate-float"></div>

      <div class="particles-container absolute inset-0 opacity-30">
        <div v-for="i in 20" :key="i" 
          class="particle absolute w-1 h-1 rounded-full bg-white"
          :style="{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 3}s`,
            animationDuration: `${3 + Math.random() * 4}s`
          }"
        ></div>
      </div>
    </div>

    <div v-else class="absolute inset-0 overflow-hidden">
      <div class="absolute top-0 right-0 w-[500px] h-[500px] rounded-full bg-indigo-200/30 blur-[100px]"></div>
      <div class="absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full bg-purple-200/30 blur-[80px]"></div>
    </div>

    <!-- 主题切换按钮 -->
    <button
      @click="themeStore.toggleTheme()"
      class="absolute top-6 right-6 z-20 p-3 rounded-xl transition-all duration-300 hover:scale-105 shadow-lg"
      :class="themeStore.isDark ? 'bg-white/10 hover:bg-white/20 text-yellow-400' : 'bg-white hover:bg-gray-50 text-indigo-500 shadow-gray-200'"
    >
      <svg v-if="themeStore.isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
    </button>

    <!-- 登录卡片 -->
    <div class="relative z-10 w-full max-w-md mx-4">
      <div class="glass-card p-10 animate-slide-up">
        <!-- Logo 和标题 -->
        <div class="text-center mb-10">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-cyber-purple shadow-lg shadow-primary-500/30 mb-6">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 class="text-3xl font-bold gradient-text mb-2">TopFlow</h1>
          <p class="text-sm" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">达人营销管理系统</p>
        </div>

        <!-- 标签页切换 -->
        <div class="flex gap-2 p-1 mb-8 rounded-xl transition-colors duration-300"
          :class="themeStore.isDark ? 'bg-white/5 border border-white/10' : 'bg-gray-100 border border-gray-200'"
        >
          <button
            @click="activeTab = 'login'"
            class="flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200"
            :class="activeTab === 'login' 
              ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-md shadow-primary-500/25' 
              : (themeStore.isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-700')"
          >
            登录
          </button>
          <button
            @click="activeTab = 'register'"
            class="flex-1 py-2.5 px-4 rounded-lg text-sm font-medium transition-all duration-200"
            :class="activeTab === 'register' 
              ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-md shadow-primary-500/25' 
              : (themeStore.isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-700')"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-5">
          <div class="space-y-1.5">
            <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">用户名</label>
            <div class="relative">
              <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <input
                v-model="loginForm.username"
                type="text"
                required
                placeholder="输入用户名"
                class="w-full pl-12 pr-4 py-3.5 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
                @keyup.enter="handleLogin"
              />
            </div>
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">密码</label>
            <div class="relative">
              <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <input
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                placeholder="输入密码"
                class="w-full pl-12 pr-12 py-3.5 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
                @keyup.enter="handleLogin"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-4 top-1/2 -translate-y-1/2 transition-colors"
                :class="themeStore.isDark ? 'text-gray-500 hover:text-gray-300' : 'text-gray-400 hover:text-gray-600'"
              >
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="cyber-button w-full py-3.5 flex items-center justify-center gap-2 text-base font-semibold disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>

        <!-- 注册表单 -->
        <form v-else @submit.prevent="handleRegister" class="space-y-4">
          <div class="space-y-1.5">
            <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">用户名 *</label>
            <input
              v-model="registerForm.username"
              type="text"
              required
              minlength="3"
              maxlength="20"
              placeholder="3-20个字符"
              class="w-full px-4 py-3 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
              :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
            />
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">邮箱 *</label>
            <input
              v-model="registerForm.email"
              type="email"
              required
              placeholder="your@email.com"
              class="w-full px-4 py-3 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
              :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
            />
          </div>

          <div class="space-y-1.5">
            <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">姓名</label>
            <input
              v-model="registerForm.full_name"
              type="text"
              placeholder="可选"
              class="w-full px-4 py-3 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
              :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1.5">
              <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">密码 *</label>
              <input
                v-model="registerForm.password"
                type="password"
                required
                minlength="6"
                placeholder="至少6位"
                class="w-full px-4 py-3 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
              />
            </div>
            <div class="space-y-1.5">
              <label class="text-xs font-medium uppercase tracking-wide" :class="themeStore.isDark ? 'text-gray-500' : 'text-gray-500'">确认密码 *</label>
              <input
                v-model="registerForm.confirm_password"
                type="password"
                required
                placeholder="再次输入"
                class="w-full px-4 py-3 rounded-xl border focus:border-cyber-blue/50 focus:outline-none focus:ring-2 focus:ring-cyber-blue/20 transition-all"
                :class="themeStore.isDark ? 'bg-white/5 border-white/10 text-white placeholder-gray-600' : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'"
                @keyup.enter="handleRegister"
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="cyber-button w-full py-3.5 flex items-center justify-center gap-2 text-base font-semibold mt-6 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '注册中...' : '注 册' }}
          </button>
        </form>

        <!-- 底部提示 -->
        <div class="mt-8 pt-6 text-center" :class="themeStore.isDark ? 'border-t border-white/5' : 'border-t border-gray-200'">
          <p class="text-xs" :class="themeStore.isDark ? 'text-gray-600' : 'text-gray-400'">
            默认管理员账号：
            <span class="font-mono text-cyber-blue">admin / admin123</span>
          </p>
        </div>
      </div>

      <!-- 底部版权信息 -->
      <div class="mt-8 text-center">
        <p class="text-xs" :class="themeStore.isDark ? 'text-gray-700' : 'text-gray-400'">© 2024 TopFlow. Powered by AI Technology</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useThemeStore } from '@/stores/theme'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const themeStore = useThemeStore()
const activeTab = ref('login')
const loading = ref(false)
const showPassword = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirm_password: ''
})

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请填写完整的登录信息')
    return
  }

  loading.value = true

  try {
    await userStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    ElMessage.warning('请填写完整的注册信息')
    return
  }

  if (registerForm.password !== registerForm.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  loading.value = true

  try {
    await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      full_name: registerForm.full_name,
      password: registerForm.password
    })
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
    loginForm.password = ''
  } catch (error) {
    console.error('Register error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.particle {
  animation: float-particle linear infinite;
}

@keyframes float-particle {
  0%, 100% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) translateX(50px);
    opacity: 0;
  }
}
</style>