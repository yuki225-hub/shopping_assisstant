import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import { Menu, Bell, Search, Sun, Moon } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user } = useAuth()
  const { isDark, toggle } = useTheme()
  const navigate = useNavigate()

  return (
    <div className="flex h-screen overflow-hidden" style={{ background: 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%)' }}>
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="glass-dark border-b border-theme px-6 py-4 flex items-center gap-4 shrink-0">
          <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-slate-400 hover:text-white">
            <Menu size={22} />
          </button>

          {/* Quick search */}
          <button onClick={() => navigate('/search')}
            className="flex-1 max-w-md flex items-center gap-3 glass rounded-xl px-4 py-2.5 text-slate-400 hover:text-white hover:border-indigo-500/50 border border-transparent transition-all text-sm">
            <Search size={16} />
            <span>Search products across 7 platforms...</span>
          </button>

          <div className="ml-auto flex items-center gap-3">
            {/* Theme toggle */}
            <motion.button
              onClick={toggle}
              whileTap={{ scale: 0.9 }}
              className="relative w-9 h-9 glass rounded-xl flex items-center justify-center text-slate-400 hover:text-white transition-colors overflow-hidden"
              title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              <motion.div
                key={isDark ? 'moon' : 'sun'}
                initial={{ rotate: -90, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                exit={{ rotate: 90, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                {isDark ? <Sun size={16} className="text-yellow-400" /> : <Moon size={16} className="text-indigo-400" />}
              </motion.div>
            </motion.button>

            <button className="relative w-9 h-9 glass rounded-xl flex items-center justify-center text-slate-400 hover:text-white transition-colors">
              <Bell size={16} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full" />
            </button>
            <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center text-white font-bold text-sm cursor-pointer"
              onClick={() => navigate('/profile')}>
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
