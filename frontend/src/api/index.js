import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const API_BASE_URL = 'http://localhost:8000'

// 创建axios实例，用于JSON请求
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 创建axios实例，用于表单请求
const formApi = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
})

// 请求拦截器，自动加token
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器，处理未登录/过期
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 403) {
      ElMessage.error('请先登录')
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export const chatWithAgent = (message) => {
  return api.post('/api/agent', { content: message }).then(res => res.data)
}

export const learnFromWebpage = (url) => {
  const formData = new FormData()
  formData.append('url', url)
  return formApi.post('/api/add_urls', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then(res => res.data)
}

export const learnFromPdf = (file) => {
  const formData = new FormData()
  formData.append('files', file)
  return formApi.post('/api/add_pdfs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then(res => res.data)
}

export const learnFromTxt = (file) => {
  const formData = new FormData()
  formData.append('files', file)
  return formApi.post('/api/add_texts', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then(res => res.data)
}

export default api