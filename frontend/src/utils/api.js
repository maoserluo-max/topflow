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
    }
    return Promise.reject(error)
  }
)

/**
 * 从 axios 错误响应中提取可读的错误信息
 */
export function getErrorMsg(error) {
  const resp = error.response?.data
  if (resp?.detail) {
    if (Array.isArray(resp.detail)) {
      // Pydantic 验证错误
      return resp.detail.map(e => {
        const field = e.loc?.slice(1).join('.') || ''
        return field ? `${field}: ${e.msg}` : e.msg
      }).join('; ')
    }
    if (typeof resp.detail === 'string') {
      return resp.detail
    }
  }
  return error.message || '操作失败'
}

export default api
