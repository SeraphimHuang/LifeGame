import axios from 'axios'

const base =
  (import.meta as any).env?.VITE_API_BASE ||
  'http://localhost:8000/api/v1'

const api = axios.create({ baseURL: base, withCredentials: false })

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers = config.headers ?? {}
    config.headers['Authorization'] = `Token ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      sessionStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api


