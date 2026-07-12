import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useWishlist } from '../context/WishlistContext'
import { authAPI, shoppingAPI } from '../services/api'
import { ShoppingBag, Mail, Lock, User, Eye, EyeOff, ArrowRight, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AuthPage() {
  const [mode, setMode] = useState('login') // 'login' | 'register' | 'forgot'
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ username: '', email: '', password: '', full_name: '' })
  const { login, register } = useAuth()
  const { clearPending } = useWishlist()
  const navigate = useNavigate()

  const set = k => e => setForm(p => ({ ...p, [k]: e.target.value }))

  const handlePendingWishlist = async () => {
    const savedId = localStorage.getItem('pending_wishlist_product_id')
    if (!savedId) return
    try {
      await shoppingAPI.addWishlist({ product_id: parseInt(savedId) })
      toast.success('Product added to wishlist! ❤️')
    } catch (err) {
      const detail = err.response?.data?.detail || ''
      if (!detail.toLowerCase().includes('already')) {
        toast.error('Could not add pending wishlist item')
      }
    }
    clearPending()
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(form.email, form.password)
        await handlePendingWishlist()
        toast.success('Welcome back! 🎉')
        navigate('/dashboard')
      } else if (mode === 'register') {
        await register(form)
        await handlePendingWishlist()
        toast.success('Account created! 🚀')
        navigate('/dashboard')
      } else if (mode === 'forgot') {
        await authAPI.forgotPassword({ email: form.email })
        toast.success('Reset instructions sent to your email')
        setMode('login')
      }
    } catch (err) {
      const msg = err.response?.data?.detail
      if (typeof msg === 'string') {
        toast.error(msg)
      } else if (Array.isArray(msg)) {
        toast.error(msg[0]?.msg || 'Validation error')
      } else {
        toast.error('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  const submitLabel = mode === 'login' ? 'Sign In' : mode === 'register' ? 'Create Account' : 'Send Reset Link'

  return (
    <div className="min-h-screen flex" style={{ background: 'linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%)' }}>
      {/* Left Panel */}
      <div className="hidden lg:flex flex-1 flex-col items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0">
          <motion.div animate={{ scale: [1,1.3,1], opacity:[0.2,0.4,0.2] }} transition={{ duration:4, repeat:Infinity }}
            className="absolute top-20 left-20 w-72 h-72 rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.4) 0%, transparent 70%)' }} />
          <motion.div animate={{ scale: [1.3,1,1.3], opacity:[0.15,0.3,0.15] }} transition={{ duration:5, repeat:Infinity }}
            className="absolute bottom-20 right-20 w-96 h-96 rounded-full"
            style={{ background: 'radial-gradient(circle, rgba(139,92,246,0.3) 0%, transparent 70%)' }} />
        </div>
        <motion.div initial={{ opacity:0, x:-50 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.3 }} className="relative z-10 text-center">
          <div className="w-20 h-20 rounded-2xl gradient-bg flex items-center justify-center mx-auto mb-6 shadow-2xl"
            style={{ boxShadow:'0 0 40px rgba(99,102,241,0.5)' }}>
            <ShoppingBag size={40} className="text-white" />
          </div>
          <h1 className="text-5xl font-bold gradient-text mb-4">ShopMind AI</h1>
          <p className="text-slate-400 text-lg mb-12">Your intelligent shopping companion</p>
          {[
            { icon: '🔍', title: 'Smart Search', desc: 'Search across 7 platforms instantly' },
            { icon: '💰', title: 'Best Prices', desc: 'AI finds the lowest price for you' },
            { icon: '⭐', title: 'Review Analysis', desc: 'NLP-powered sentiment analysis' },
            { icon: '🎯', title: 'Recommendations', desc: 'Personalized product suggestions' },
          ].map((f, i) => (
            <motion.div key={i} initial={{ opacity:0, x:-30 }} animate={{ opacity:1, x:0 }} transition={{ delay: 0.5 + i*0.1 }}
              className="flex items-center gap-4 mb-4 glass rounded-xl p-4 text-left">
              <span className="text-2xl">{f.icon}</span>
              <div>
                <p className="font-semibold text-white">{f.title}</p>
                <p className="text-slate-400 text-sm">{f.desc}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Right Panel */}
      <div className="flex-1 flex items-center justify-center p-6">
        <motion.div initial={{ opacity:0, y:30 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.5 }}
          className="w-full max-w-md">
          <div className="glass-dark rounded-3xl p-8 shadow-2xl">
            {/* Logo mobile */}
            <div className="lg:hidden flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
                <ShoppingBag size={20} className="text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">ShopMind AI</span>
            </div>

            {/* Tabs — only show for login/register */}
            {mode !== 'forgot' && (
              <div className="flex gap-1 glass rounded-xl p-1 mb-8">
                {['login', 'register'].map(m => (
                  <button key={m} onClick={() => setMode(m)}
                    className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 capitalize
                      ${mode === m ? 'gradient-bg text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}>
                    {m === 'login' ? 'Sign In' : 'Sign Up'}
                  </button>
                ))}
              </div>
            )}

            <AnimatePresence mode="wait">
              <motion.form key={mode} initial={{ opacity:0, x:20 }} animate={{ opacity:1, x:0 }}
                exit={{ opacity:0, x:-20 }} transition={{ duration:0.2 }} onSubmit={handleSubmit}>

                {mode === 'forgot' && (
                  <button type="button" onClick={() => setMode('login')}
                    className="flex items-center gap-1 text-slate-400 hover:text-white text-sm mb-6 transition-colors">
                    <ArrowLeft size={14} /> Back to Sign In
                  </button>
                )}

                <h2 className="text-2xl font-bold text-white mb-1">
                  {mode === 'login' ? 'Welcome back 👋' : mode === 'register' ? 'Create account ✨' : 'Reset password 🔑'}
                </h2>
                <p className="text-slate-400 text-sm mb-6">
                  {mode === 'login' ? 'Sign in to your ShopMind account'
                    : mode === 'register' ? 'Join thousands of smart shoppers'
                    : 'Enter your email to receive reset instructions'}
                </p>

                {mode === 'register' && (
                  <>
                    <div className="mb-4">
                      <label className="text-slate-300 text-sm mb-1.5 block">Full Name</label>
                      <div className="relative">
                        <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                        <input value={form.full_name} onChange={set('full_name')} placeholder="John Doe"
                          className="w-full glass rounded-xl py-3 pl-10 pr-4 text-white placeholder-slate-500 outline-none focus:border-indigo-500 border border-transparent transition-all" />
                      </div>
                    </div>
                    <div className="mb-4">
                      <label className="text-slate-300 text-sm mb-1.5 block">Username</label>
                      <div className="relative">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">@</span>
                        <input value={form.username} onChange={set('username')} placeholder="johndoe" required
                          className="w-full glass rounded-xl py-3 pl-8 pr-4 text-white placeholder-slate-500 outline-none focus:border-indigo-500 border border-transparent transition-all" />
                      </div>
                    </div>
                  </>
                )}

                <div className="mb-4">
                  <label className="text-slate-300 text-sm mb-1.5 block">Email</label>
                  <div className="relative">
                    <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input type="email" value={form.email} onChange={set('email')} placeholder="you@example.com" required
                      className="w-full glass rounded-xl py-3 pl-10 pr-4 text-white placeholder-slate-500 outline-none focus:border-indigo-500 border border-transparent transition-all" />
                  </div>
                </div>

                {mode !== 'forgot' && (
                  <div className="mb-6">
                    <label className="text-slate-300 text-sm mb-1.5 block">Password</label>
                    <div className="relative">
                      <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input type={show ? 'text' : 'password'} value={form.password} onChange={set('password')}
                        placeholder="••••••••" required minLength={8}
                        className="w-full glass rounded-xl py-3 pl-10 pr-10 text-white placeholder-slate-500 outline-none focus:border-indigo-500 border border-transparent transition-all" />
                      <button type="button" onClick={() => setShow(!show)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                        {show ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                    {mode === 'login' && (
                      <button type="button" onClick={() => setMode('forgot')}
                        className="text-indigo-400 text-xs mt-1.5 hover:text-indigo-300 float-right">
                        Forgot password?
                      </button>
                    )}
                  </div>
                )}

                {mode === 'forgot' && <div className="mb-6" />}

                <motion.button type="submit" disabled={loading} whileHover={{ scale:1.02 }} whileTap={{ scale:0.98 }}
                  className="w-full gradient-bg text-white py-3.5 rounded-xl font-semibold flex items-center justify-center gap-2 shadow-lg disabled:opacity-60 transition-all"
                  style={{ boxShadow:'0 8px 25px rgba(99,102,241,0.4)' }}>
                  {loading
                    ? <motion.div animate={{ rotate:360 }} transition={{ duration:1, repeat:Infinity, ease:'linear' }}
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full" />
                    : <>{submitLabel} <ArrowRight size={18} /></>
                  }
                </motion.button>

                {mode !== 'forgot' && (
                  <p className="text-center text-slate-400 text-sm mt-4">
                    {mode === 'login' ? "Don't have an account? " : "Already have an account? "}
                    <button type="button" onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                      className="text-indigo-400 hover:text-indigo-300 font-medium">
                      {mode === 'login' ? 'Sign up' : 'Sign in'}
                    </button>
                  </p>
                )}
              </motion.form>
            </AnimatePresence>
          </div>
          <p className="text-center text-slate-600 text-xs mt-6">
            Powered by AI Agents • 7 Platforms • Real-time Analysis
          </p>
        </motion.div>
      </div>
    </div>
  )
}
