import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, SlidersHorizontal, X } from 'lucide-react'
import { shoppingAPI } from '../services/api'
import SearchResults from '../components/SearchResults'
import { Spinner } from '../components/ui/index'
import toast from 'react-hot-toast'

const PLATFORMS = ['Amazon', 'Flipkart', 'Meesho', 'Myntra', 'Ajio', 'Croma', 'Reliance Digital']
const SORT_OPTIONS = [
  { value:'relevance', label:'Relevance' },
  { value:'price_asc', label:'Price: Low to High' },
  { value:'price_desc', label:'Price: High to Low' },
  { value:'rating', label:'Best Rating' },
  { value:'discount', label:'Best Discount' },
]

export default function SearchPage() {
  const [params] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') || '')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState({
    platforms: [], min_price: '', max_price: '', min_rating: '', sort_by: 'relevance'
  })

  useEffect(() => {
    const q = params.get('q')
    if (q) { setQuery(q); doSearch(q) }
  }, [params])

  const doSearch = async (q = query, f = filters) => {
    if (!q.trim()) return toast.error('Enter a search query')
    setLoading(true)
    setResults(null)
    try {
      const p = {
        q: q.trim(),
        sort_by: f.sort_by,
        ...(f.platforms.length && { platforms: f.platforms.join(',') }),
        ...(f.min_price && { min_price: f.min_price }),
        ...(f.max_price && { max_price: f.max_price }),
        ...(f.min_rating && { min_rating: f.min_rating }),
      }
      const { data } = await shoppingAPI.search(p)
      setResults(data)
    } catch {
      toast.error('Search failed. Make sure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const togglePlatform = p => setFilters(f => ({
    ...f, platforms: f.platforms.includes(p) ? f.platforms.filter(x => x !== p) : [...f.platforms, p]
  }))

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Search Bar */}
      <motion.div initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }} className="space-y-4">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
            <input value={query} onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && doSearch()}
              placeholder="Search for any product... (e.g. iPhone 15, Nike shoes)"
              className="w-full glass rounded-2xl py-4 pl-12 pr-4 text-white placeholder-slate-500 outline-none focus:border-indigo-500 border border-transparent transition-all text-sm" />
            {query && (
              <button onClick={() => { setQuery(''); setResults(null) }}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                <X size={16} />
              </button>
            )}
          </div>
          <button onClick={() => setShowFilters(!showFilters)}
            className={`px-4 glass rounded-2xl flex items-center gap-2 text-sm font-medium transition-all border
              ${showFilters ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-white'}`}>
            <SlidersHorizontal size={16} /> Filters
          </button>
          <motion.button onClick={() => doSearch()} whileHover={{ scale:1.02 }} whileTap={{ scale:0.98 }}
            className="gradient-bg text-white px-6 rounded-2xl font-medium text-sm"
            style={{ boxShadow:'0 8px 20px rgba(99,102,241,0.4)' }}>
            Search
          </motion.button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <motion.div initial={{ opacity:0, height:0 }} animate={{ opacity:1, height:'auto' }}
            className="glass rounded-2xl p-5 space-y-4">
            {/* Platforms */}
            <div>
              <p className="text-slate-300 text-sm font-medium mb-2">Platforms</p>
              <div className="flex flex-wrap gap-2">
                {PLATFORMS.map(p => (
                  <button key={p} onClick={() => togglePlatform(p)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-all
                      ${filters.platforms.includes(p)
                        ? 'gradient-bg text-white border-transparent'
                        : 'glass text-slate-400 border-white/10 hover:text-white'}`}>
                    {p}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <p className="text-slate-300 text-xs mb-1">Min Price (₹)</p>
                <input type="number" value={filters.min_price} onChange={e => setFilters(f => ({...f, min_price: e.target.value}))}
                  placeholder="0" className="w-full glass rounded-xl py-2 px-3 text-white text-sm outline-none border border-transparent focus:border-indigo-500" />
              </div>
              <div>
                <p className="text-slate-300 text-xs mb-1">Max Price (₹)</p>
                <input type="number" value={filters.max_price} onChange={e => setFilters(f => ({...f, max_price: e.target.value}))}
                  placeholder="100000" className="w-full glass rounded-xl py-2 px-3 text-white text-sm outline-none border border-transparent focus:border-indigo-500" />
              </div>
              <div>
                <p className="text-slate-300 text-xs mb-1">Min Rating</p>
                <input type="number" min="0" max="5" step="0.5" value={filters.min_rating}
                  onChange={e => setFilters(f => ({...f, min_rating: e.target.value}))}
                  placeholder="0" className="w-full glass rounded-xl py-2 px-3 text-white text-sm outline-none border border-transparent focus:border-indigo-500" />
              </div>
              <div>
                <p className="text-slate-300 text-xs mb-1">Sort By</p>
                <select value={filters.sort_by} onChange={e => setFilters(f => ({...f, sort_by: e.target.value}))}
                  className="w-full glass rounded-xl py-2 px-3 text-white text-sm outline-none border border-transparent focus:border-indigo-500 bg-transparent">
                  {SORT_OPTIONS.map(o => <option key={o.value} value={o.value} className="bg-slate-800">{o.label}</option>)}
                </select>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Spinner />
          <div className="text-center">
            <p className="text-white font-medium">AI Agents are working...</p>
            <p className="text-slate-400 text-sm mt-1">Searching across 7 platforms simultaneously</p>
          </div>
          <div className="flex gap-2 mt-2">
            {['🔍 Searching','💰 Comparing','⭐ Analyzing','🎯 Recommending'].map((s,i) => (
              <motion.span key={i} animate={{ opacity:[0.4,1,0.4] }} transition={{ duration:1.5, repeat:Infinity, delay:i*0.3 }}
                className="text-xs text-slate-400 glass px-3 py-1 rounded-full">{s}</motion.span>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {results && !loading && <SearchResults data={results} onWishlistUpdate={() => {}} />}

      {/* Empty state */}
      {!results && !loading && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <motion.div animate={{ y:[0,-10,0] }} transition={{ duration:3, repeat:Infinity }} className="text-7xl mb-6">🛍️</motion.div>
          <h3 className="text-white text-xl font-semibold mb-2">Search Anything</h3>
          <p className="text-slate-400 max-w-md">Our AI agents will search across Amazon, Flipkart, Meesho, Myntra, Ajio, Croma and Reliance Digital simultaneously</p>
        </div>
      )}
    </div>
  )
}
