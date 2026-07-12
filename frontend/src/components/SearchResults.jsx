import { motion } from 'framer-motion'
import { TrendingDown, TrendingUp, BarChart3, Star, Trophy, Zap, Shield } from 'lucide-react'
import { ScoreRing, Badge } from './ui/index'
import ProductCard from './ProductCard'
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'

export default function SearchResults({ data, onWishlistUpdate }) {
  if (!data) return null
  const { products, price_comparison: pc, review_analysis: ra, recommendation: rec } = data

  const sentimentData = [
    { name: 'Positive', value: ra.positive_percent, color: '#22c55e' },
    { name: 'Neutral', value: ra.neutral_percent, color: '#f59e0b' },
    { name: 'Negative', value: ra.negative_percent, color: '#ef4444' },
  ]

  const priceData = products
    .filter(p => p.price != null)
    .map(p => ({
      name: p.platform,
      price: Math.round(p.price),
      title: p.title,
      rating: p.rating,
    }))
    .sort((a, b) => a.price - b.price)
    .slice(0, 10)

  return (
    <div className="space-y-6">
      {/* Recommendation Banner */}
      <motion.div initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }}
        className="glass rounded-2xl p-6 border border-indigo-500/30"
        style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))' }}>
        <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
          <div className="flex items-center gap-4">
            <ScoreRing score={Math.round(rec.score)} size={80} />
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Trophy size={16} className="text-yellow-400" />
                <span className="text-yellow-400 text-sm font-medium">AI Recommendation</span>
              </div>
              <h3 className="text-white font-bold text-lg leading-tight">{rec.best_overall}</h3>
              <p className="text-slate-400 text-sm mt-1">{rec.reason}</p>
            </div>
          </div>
          <div className="md:ml-auto flex flex-wrap gap-2">
            {rec.pros?.slice(0,3).map((p,i) => <Badge key={i} color="green">✓ {p}</Badge>)}
            {rec.cons?.slice(0,2).map((c,i) => <Badge key={i} color="red">✗ {c}</Badge>)}
          </div>
        </div>

        {/* Best picks row */}
        <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-white/10">
          {[
            { label: '🏆 Best Overall', title: rec.best_overall, price: rec.best_overall_price, rating: rec.best_overall_rating },
            { label: '💰 Best Budget',  title: rec.best_budget,  price: rec.best_budget_price,  rating: rec.best_budget_rating  },
            { label: '👑 Best Premium', title: rec.best_premium, price: rec.best_premium_price, rating: rec.best_premium_rating },
          ].map((item, i) => (
            <div key={i} className="glass rounded-xl p-3">
              <p className="text-xs text-slate-400 mb-1">{item.label}</p>
              <p className="text-white text-xs font-medium line-clamp-2 mb-1">{item.title || 'N/A'}</p>
              {item.price != null && (
                <p className="text-indigo-400 text-xs font-bold">₹{Math.round(item.price).toLocaleString('en-IN')}</p>
              )}
              {item.rating != null && (
                <p className="text-yellow-400 text-xs">★ {item.rating}</p>
              )}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { icon: <TrendingDown size={18} className="text-green-400" />, label: 'Lowest Price', value: `₹${pc.lowest_price?.toLocaleString('en-IN') || 'N/A'}`, color: 'green' },
          { icon: <TrendingUp size={18} className="text-red-400" />, label: 'Highest Price', value: `₹${pc.highest_price?.toLocaleString('en-IN') || 'N/A'}`, color: 'red' },
          { icon: <BarChart3 size={18} className="text-indigo-400" />, label: 'Avg Price', value: `₹${pc.average_price?.toLocaleString('en-IN') || 'N/A'}`, color: 'indigo' },
          { icon: <Star size={18} className="text-yellow-400" />, label: 'Sentiment', value: `${ra.positive_percent?.toFixed(0)}% Positive`, color: 'yellow' },
        ].map((s, i) => (
          <motion.div key={i} initial={{ opacity:0, scale:0.9 }} animate={{ opacity:1, scale:1 }} transition={{ delay: i*0.1 }}
            className="glass rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">{s.icon}<span className="text-slate-400 text-xs">{s.label}</span></div>
            <p className="text-white font-bold text-lg">{s.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Price Chart */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <BarChart3 size={16} className="text-indigo-400" /> Price by Platform
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={priceData}>
              <XAxis dataKey="name" tick={{ fill:'#94a3b8', fontSize:11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill:'#94a3b8', fontSize:11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background:'#1e1e2e', border:'1px solid rgba(255,255,255,0.1)', borderRadius:'12px', color:'#fff' }} />
              <Bar dataKey="price" radius={[6,6,0,0]}>
                {priceData.map((_, i) => (
                  <Cell key={i} fill={`hsl(${240 + i*20}, 70%, 60%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <Zap size={16} className="text-yellow-400" /> Review Sentiment
          </h3>
          <p className="text-slate-400 text-sm mb-4">{ra.summary}</p>
          <div className="space-y-3">
            {sentimentData.map(s => (
              <div key={s.name}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400">{s.name}</span>
                  <span className="text-white font-medium">{s.value?.toFixed(1)}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <motion.div initial={{ width:0 }} animate={{ width:`${s.value}%` }} transition={{ duration:1, delay:0.3 }}
                    className="h-full rounded-full" style={{ background: s.color }} />
                </div>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            {ra.common_pros?.slice(0,3).map((p,i) => <Badge key={i} color="green">{p}</Badge>)}
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-white font-semibold text-lg">
            {products.length} Products Found
          </h3>
          <Badge color="indigo">{data.total_results} total across all platforms</Badge>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {products.map((p, i) => (
            <ProductCard key={`${p.platform}-${i}`} product={p} index={i} onWishlist={onWishlistUpdate} />
          ))}
        </div>
      </div>
    </div>
  )
}
