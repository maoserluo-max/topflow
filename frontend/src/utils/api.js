import axios from 'axios'
import router from '@/router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

api.interceptors.request.use(
  config => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => {
    if (response.config.responseType === 'blob') {
      return response.data
    }
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    }
    return Promise.reject(error)
  }
)

export default api
