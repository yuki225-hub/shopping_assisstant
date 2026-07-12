import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'
import { User, Mail, Save, Shield } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState({ full_name: user?.full_name || '' })
  const [loading, setLoading] = useState(false)

  const save = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await authAPI.updateProfile(form)
      updateUser(data)
      toast.success('Profile updated!')
    } catch {
      toast.error('Update failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <User size={24} className="text-indigo-400" /> My Profile
      </h1>

      {/* Avatar card */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
        className="glass rounded-2xl p-6 flex items-center gap-5"
        style={{ background:'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))' }}>
        <div className="w-20 h-20 rounded-2xl gradient-bg flex items-center justify-center text-white text-3xl font-bold shadow-xl"
          style={{ boxShadow:'0 0 30px rgba(99,102,241,0.4)' }}>
          {user?.username?.[0]?.toUpperCase()}
        </div>
        <div>
          <h2 className="text-white text-xl font-bold">{user?.full_name || user?.username}</h2>
          <p className="text-slate-400 text-sm">@{user?.username}</p>
          <p className="text-slate-500 text-xs mt-1">Member since {new Date(user?.created_at).toLocaleDateString('en-IN', { month:'long', year:'numeric' })}</p>
        </div>
      </motion.div>

      {/* Edit form */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.1 }}
        className="glass rounded-2xl p-6">
        <h3 className="text-white font-semibold mb-5 flex items-center gap-2">
          <Shield size={16} className="text-indigo-400" /> Account Details
        </h3>
        <form onSubmit={save} className="space-y-4">
          <div>
            <label className="text-slate-300 text-sm mb-1.5 block">Full Name</label>
            <div className="relative">
              <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input value={form.full_name} onChange={e => setForm(f => ({...f, full_name: e.target.value}))}
                placeholder="Your full name"
                className="w-full glass rounded-xl py-3 pl-10 pr-4 text-white placeholder-slate-500 outline-none focus:border-indigo-500 border border-transparent transition-all" />
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm mb-1.5 block">Email</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input value={user?.email} disabled
                className="w-full glass rounded-xl py-3 pl-10 pr-4 text-slate-400 outline-none border border-transparent opacity-60 cursor-not-allowed" />
            </div>
          </div>
          <div>
            <label className="text-slate-300 text-sm mb-1.5 block">Username</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">@</span>
              <input value={user?.username} disabled
                className="w-full glass rounded-xl py-3 pl-8 pr-4 text-slate-400 outline-none border border-transparent opacity-60 cursor-not-allowed" />
            </div>
          </div>
          <motion.button type="submit" disabled={loading} whileHover={{ scale:1.02 }} whileTap={{ scale:0.98 }}
            className="flex items-center gap-2 gradient-bg text-white px-6 py-3 rounded-xl font-medium text-sm disabled:opacity-60"
            style={{ boxShadow:'0 8px 20px rgba(99,102,241,0.4)' }}>
            {loading ? '...' : <><Save size={16} /> Save Changes</>}
          </motion.button>
        </form>
      </motion.div>
    </div>
  )
}
