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
          // Robust checking mechanisms to fallback on any nested variations
          const userData = r?.data?.user || r?.data?.data || r?.data;
          if (userData && (userData.id || userData.email || userData.username)) {
            setUser(userData);
          } else {
            // If data exists but has nested structure patterns
            setUser(r.data);
          }
        })
        .catch((err) => {
          console.error("Profile check failed, clearing session: ", err);
          localStorage.clear();
          setUser(null);
        })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password })
      // Unwrapping standard object values safely
      const resData = response?.data?.data || response?.data;
      
      if (resData && (resData.access_token || resData.data?.access_token)) {
        const token = resData.access_token || resData.data?.access_token;
        const refresh = resData.refresh_token || resData.data?.refresh_token || '';
        
        localStorage.setItem('access_token', token)
        localStorage.setItem('refresh_token', refresh)
        
        const sessionUser = resData.user || resData.data?.user || resData;
        setUser(sessionUser)
        return sessionUser
      }
      throw new Error("Invalid token structure from backend");
    } catch (error) {
      localStorage.clear();
      setUser(null);
      throw error;
    }
  }

  const register = async (formData) => {
    await authAPI.register(formData)
    return login(formData.email, formData.password)
  }

  const logout = async () => {
    try { await authAPI.logout() } catch {}
    localStorage.clear()
    setUser(null)
  }

  const updateUser = (data) => setUser(prev => ({ ...prev, ...data }))

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)