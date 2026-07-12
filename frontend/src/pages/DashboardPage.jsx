import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { shoppingAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { StatCard, Spinner, EmptyState } from '../components/ui/index'
import { Search, TrendingUp, Clock, Heart, Zap, ArrowRight } from 'lucide-react'

const TRENDING = ['iPhone 15', 'Samsung TV', 'Nike Shoes', 'MacBook Air', 'Sony Headphones', 'OnePlus 12']

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [dash, setDash] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    shoppingAPI.getDashboard()
      .then(r => setDash(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Hero greeting */}
      <motion.div initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }}
        className="glass rounded-2xl p-6 relative overflow-hidden"
        style={{ background:'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.1))' }}>
        <div className="absolute right-6 top-1/2 -translate-y-1/2 text-8xl opacity-10 select-none">🛍️</div>
        <h2 className="text-2xl font-bold text-white mb-1">
          {greeting}, {user?.full_name || user?.username}! 👋
        </h2>
        <p className="text-slate-400 mb-4">Find the best deals with AI-powered shopping intelligence</p>
        <button onClick={() => navigate('/search')}
          className="flex items-center gap-2 gradient-bg text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:opacity-90 transition-opacity"
          style={{ boxShadow:'0 8px 20px rgba(99,102,241,0.4)' }}>
          <Search size={16} /> Start Searching <ArrowRight size={14} />
        </button>
      </motion.div>

      {/* Stats */}
      {loading ? (
        <div className="flex justify-center py-8"><Spinner /></div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon="🔍" label="Total Searches" value={dash?.total_searches || 0} color="indigo" delay={0.1} />
          <StatCard icon="❤️" label="Wishlist Items" value={dash?.wishlist_count || 0} color="pink" delay={0.2} />
          <StatCard icon="🏪" label="Platforms" value="7" color="purple" delay={0.3} />
          <StatCard icon="🤖" label="AI Agents" value="4" color="green" delay={0.4} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Searches */}
        <motion.div initial={{ opacity:0, x:-20 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.3 }}
          className="glass rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold flex items-center gap-2">
              <Clock size={16} className="text-indigo-400" /> Recent Searches
            </h3>
            <button onClick={() => navigate('/history')} className="text-indigo-400 text-xs hover:text-indigo-300">View all</button>
          </div>
          {dash?.recent_searches?.length > 0 ? (
            <div className="space-y-2">
              {dash.recent_searches.map((q, i) => (
                <button key={i} onClick={() => navigate(`/search?q=${encodeURIComponent(q)}`)}
                  className="w-full flex items-center gap-3 p-3 glass rounded-xl hover:border-indigo-500/30 border border-transparent transition-all text-left group">
                  <Search size={14} className="text-slate-400 group-hover:text-indigo-400 transition-colors" />
                  <span className="text-slate-300 text-sm flex-1">{q}</span>
                  <ArrowRight size={12} className="text-slate-600 group-hover:text-indigo-400 transition-colors" />
                </button>
              ))}
            </div>
          ) : (
            <EmptyState icon="🔍" title="No searches yet" desc="Start searching to see your history here" />
          )}
        </motion.div>

        {/* Trending */}
        <motion.div initial={{ opacity:0, x:20 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.4 }}
          className="glass rounded-2xl p-5">
          <h3 className="text-white font-semibold flex items-center gap-2 mb-4">
            <TrendingUp size={16} className="text-pink-400" /> Trending Now
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {TRENDING.map((item, i) => (
              <button key={i} onClick={() => navigate(`/search?q=${encodeURIComponent(item)}`)}
                className="flex items-center gap-2 p-3 glass rounded-xl hover:border-indigo-500/30 border border-transparent transition-all text-left group">
                <span className="text-lg">{['📱','📺','👟','💻','🎧','📱'][i]}</span>
                <span className="text-slate-300 text-sm group-hover:text-white transition-colors">{item}</span>
              </button>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Platform badges */}
      <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.5 }}
        className="glass rounded-2xl p-5">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Zap size={16} className="text-yellow-400" /> Supported Platforms
        </h3>
        <div className="flex flex-wrap gap-3">
          {[
            { name:'Amazon', emoji:'📦', color:'from-orange-500/20 to-orange-600/10 border-orange-500/20' },
            { name:'Flipkart', emoji:'🛒', color:'from-blue-500/20 to-blue-600/10 border-blue-500/20' },
            { name:'Meesho', emoji:'🎀', color:'from-pink-500/20 to-pink-600/10 border-pink-500/20' },
            { name:'Myntra', emoji:'👗', color:'from-purple-500/20 to-purple-600/10 border-purple-500/20' },
            { name:'Ajio', emoji:'✨', color:'from-red-500/20 to-red-600/10 border-red-500/20' },
            { name:'Croma', emoji:'💻', color:'from-green-500/20 to-green-600/10 border-green-500/20' },
            { name:'Reliance Digital', emoji:'📡', color:'from-indigo-500/20 to-indigo-600/10 border-indigo-500/20' },
          ].map((p, i) => (
            <motion.div key={i} initial={{ opacity:0, scale:0.8 }} animate={{ opacity:1, scale:1 }} transition={{ delay: 0.5 + i*0.05 }}
              className={`flex items-center gap-2 px-4 py-2 bg-gradient-to-br ${p.color} border rounded-xl`}>
              <span>{p.emoji}</span>
              <span className="text-white text-sm font-medium">{p.name}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
