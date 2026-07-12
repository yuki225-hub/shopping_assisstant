import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { shoppingAPI } from '../services/api'
import { History, Search, Trash2, Clock } from 'lucide-react'
import { Spinner, EmptyState } from '../components/ui/index'
import toast from 'react-hot-toast'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const load = () => {
    shoppingAPI.getHistory()
      .then(r => setHistory(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const clearAll = async () => {
    try {
      await shoppingAPI.clearHistory()
      setHistory([])
      toast.success('History cleared')
    } catch {
      toast.error('Failed to clear history')
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <History size={24} className="text-indigo-400" /> Search History
          </h1>
          <p className="text-slate-400 text-sm mt-1">{history.length} searches</p>
        </div>
        {history.length > 0 && (
          <button onClick={clearAll}
            className="flex items-center gap-2 text-red-400 hover:text-red-300 text-sm glass px-4 py-2 rounded-xl transition-all">
            <Trash2 size={14} /> Clear All
          </button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Spinner /></div>
      ) : history.length === 0 ? (
        <EmptyState icon="🔍" title="No search history" desc="Your searches will appear here" />
      ) : (
        <div className="space-y-2">
          {history.map((item, i) => (
            <motion.button key={item.id} initial={{ opacity:0, x:-20 }} animate={{ opacity:1, x:0 }} transition={{ delay: i*0.04 }}
              onClick={() => navigate(`/search?q=${encodeURIComponent(item.query)}`)}
              className="w-full flex items-center gap-4 glass rounded-xl p-4 hover:border-indigo-500/30 border border-transparent transition-all group text-left">
              <div className="w-9 h-9 glass rounded-xl flex items-center justify-center shrink-0">
                <Search size={14} className="text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm">{item.query}</p>
                <div className="flex items-center gap-3 mt-0.5">
                  <span className="text-slate-500 text-xs flex items-center gap-1">
                    <Clock size={10} />{new Date(item.created_at).toLocaleDateString('en-IN', { day:'numeric', month:'short', hour:'2-digit', minute:'2-digit' })}
                  </span>
                  <span className="text-slate-500 text-xs">{item.result_count} results</span>
                </div>
              </div>
              <Search size={14} className="text-slate-600 group-hover:text-indigo-400 transition-colors shrink-0" />
            </motion.button>
          ))}
        </div>
      )}
    </div>
  )
}
