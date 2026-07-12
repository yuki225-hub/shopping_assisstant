import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { shoppingAPI } from '../services/api'
import { Heart, Trash2, ExternalLink, Star } from 'lucide-react'
import { Spinner, EmptyState, Badge } from '../components/ui/index'
import toast from 'react-hot-toast'

export default function WishlistPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    shoppingAPI.getWishlist()
      .then(r => setItems(r.data))
      .catch(() => toast.error('Failed to load wishlist'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const remove = async (id) => {
    try {
      await shoppingAPI.removeWishlist(id)
      setItems(prev => prev.filter(i => i.id !== id))
      toast.success('Removed from wishlist')
    } catch {
      toast.error('Failed to remove')
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Heart size={24} className="text-pink-400 fill-pink-400" /> My Wishlist
          </h1>
          <p className="text-slate-400 text-sm mt-1">{items.length} saved items</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><Spinner /></div>
      ) : items.length === 0 ? (
        <EmptyState icon="❤️" title="Your wishlist is empty" desc="Search for products and add them to your wishlist" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {items.map((item, i) => (
            <motion.div key={item.id} initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay: i*0.05 }}
              className="glass rounded-2xl p-4 flex gap-4 card-hover">
              <div className="w-20 h-20 rounded-xl bg-slate-800 flex items-center justify-center shrink-0 overflow-hidden">
                {item.product?.image_url
                  ? <img src={item.product.image_url} alt="" className="w-full h-full object-cover" />
                  : <span className="text-3xl">🛍️</span>}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-white font-medium text-sm line-clamp-2 mb-2">{item.product?.title}</p>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-indigo-400 font-bold">₹{item.product?.price?.toLocaleString('en-IN')}</span>
                  {item.product?.discount > 0 && (
                    <Badge color="green">-{item.product.discount?.toFixed(0)}%</Badge>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <Badge color="indigo">{item.product?.platform}</Badge>
                  {item.product?.rating && (
                    <span className="flex items-center gap-1 text-yellow-400 text-xs">
                      <Star size={10} className="fill-yellow-400" />{item.product.rating}
                    </span>
                  )}
                </div>
                {item.note && <p className="text-slate-500 text-xs mt-2 italic">"{item.note}"</p>}
              </div>
              <div className="flex flex-col gap-2 shrink-0">
                {item.product?.product_url && (
                  <a href={item.product.product_url} target="_blank" rel="noreferrer"
                    className="w-8 h-8 glass rounded-lg flex items-center justify-center text-slate-400 hover:text-indigo-400 transition-colors">
                    <ExternalLink size={14} />
                  </a>
                )}
                <button onClick={() => remove(item.id)}
                  className="w-8 h-8 glass rounded-lg flex items-center justify-center text-slate-400 hover:text-red-400 transition-colors">
                  <Trash2 size={14} />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
