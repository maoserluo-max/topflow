import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isLeaderOrAbove = computed(() => ['admin', 'leader'].includes(user.value?.role))
  const canManageUsers = computed(() => ['admin', 'leader'].includes(user.value?.role))
  const userProjects = computed(() => {
    if (!user.value?.projects) return ['Gamoji', 'Poseme', '内容孵化']
    return user.value.projects.split(',').map(p => p.trim()).filter(p => p)
  })

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    token.value = response.access_token
    user.value = response.user

    localStorage.setItem('token', response.access_token)
    localStorage.setItem('user', JSON.stringify(response.user))

    return response
  }

  async function register(userData) {
    const response = await api.post('/auth/register', userData)
    return response
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchCurrentUser() {
    try {
      const response = await api.get('/auth/me')
      user.value = response
      localStorage.setItem('user', JSON.stringify(response))
      return response
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    isLeaderOrAbove,
    canManageUsers,
    userProjects,
    login,
    register,
    logout,
    fetchCurrentUser
  }
})