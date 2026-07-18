import axios from 'axios'


const BACKEND_URL = 'https://shopping-agent-backend-xabi.onrender.com/api/v1'

const api = axios.create({ 
  baseURL: BACKEND_URL 
})

// Attach token to every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('access_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto refresh on 401
api.interceptors.response.use(
  res => res,
  async err => {
    if (err.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
        
          const { data } = await axios.post(`${BACKEND_URL}/auth/refresh`, { refresh_token: refresh })
          localStorage.setItem('access_token', data.access_token)
          err.config.headers.Authorization = `Bearer ${data.access_token}`
          return api(err.config)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(err)
  }
)

export const authAPI = {
  register: d => api.post('/auth/register', d),
  login: d => api.post('/auth/login', d),
  googleLogin: token => api.post('/auth/google', { token }), 
  logout: () => api.post('/auth/logout'),
  forgotPassword: d => api.post('/auth/forgot-password', d),
  resetPassword: d => api.post('/auth/reset-password', d),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: d => api.put('/auth/profile', d),
}

export const shoppingAPI = {
  search: params => api.get('/search', { params }),
  getProduct: id => api.get(`/product/${id}`),
  compare: data => api.post('/compare', data),
  analyzeReviews: data => api.post('/analyze-reviews', data),
  getWishlist: () => api.get('/wishlist'),
  addWishlist: data => api.post('/wishlist', data),
  removeWishlist: id => api.delete(`/wishlist/${id}`),
  getHistory: () => api.get('/history'),
  clearHistory: () => api.delete('/history'),
  getDashboard: () => api.get('/dashboard'),
}

export default api