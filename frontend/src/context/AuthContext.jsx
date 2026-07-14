import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authAPI.getProfile()
        .then(r => {
          // Robust nested data check parsing layers variables matching lookup setups:
          const userData = r.data?.user || r.data?.data || r.data;
          if (userData) {
            setUser(userData);
          } else {
            // Fallback object fields tracking properties fallback structural properties:
            setUser(r.data);
          }
        })
        .catch(() => {
          // System handles errors safely without hard crashing active valid session tokens
          console.error("Profile recovery session mapping bypassed or format structure mismatch");
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password })
    // Axios handles responses context formatting wrapper layer safe layout mapping lookups:
    const resData = response.data?.data || response.data;
    
    if (resData && resData.access_token) {
      localStorage.setItem('access_token', resData.access_token)
      localStorage.setItem('refresh_token', resData.refresh_token || '')
      
      const sessionUser = resData.user || resData;
      setUser(sessionUser)
      return sessionUser
    }
    return null
  }

  const register = async (formData) => {
    await authAPI.register(formData)
    return login(formData.email, formData.password)
  }

  const logout = async () => {
    try { await authAPI.logout() } catch {}
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const updateUser = (data) => setUser(prev => ({ ...prev, ...data }))

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)