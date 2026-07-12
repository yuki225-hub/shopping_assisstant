import { useState } from 'react'
import { motion } from 'framer-motion'
import { Star, Heart, ExternalLink, Truck } from 'lucide-react'
import { Badge } from './ui/index'
import toast from 'react-hot-toast'
import { shoppingAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useWishlist } from '../context/WishlistContext'
import { useNavigate } from 'react-router-dom'

const PLATFORM_COLORS = {
  Amazon: 'orange', Flipkart: 'indigo', Meesho: 'pink',
  Myntra: 'purple', Ajio: 'red', Croma: 'green', 'Reliance Digital': 'indigo',
}

const PLATFORM_BG = {
  Amazon: '#f97316', Flipkart: '#3b82f6', Meesho: '#ec4899',
  Myntra: '#8b5cf6', Ajio: '#ef4444', Croma: '#22c55e', 'Reliance Digital': '#6366f1',
}

// Generate inline SVG placeholder — no external requests needed
function makePlaceholder(platform) {
  const bg = PLATFORM_BG[platform] || '#6366f1'
  const label = platform || 'Product'
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='300' height='200'>
    <rect width='300' height='200' fill='%231a1a2e'/>
    <rect x='100' y='60' width='100' height='80' rx='12' fill='${bg}' opacity='0.3'/>
    <text x='150' y='108' font-family='system-ui' font-size='14' fill='${bg}' text-anchor='middle' font-weight='600'>${label}</text>
    <text x='150' y='130' font-family='system-ui' font-size='11' fill='%2394a3b8' text-anchor='middle'>No Image</text>
  </svg>`
  return `data:image/svg+xml,${svg}`
}

export default function ProductCard({ product, index, onWishlist }) {
  const { user } = useAuth()
  const { setPendingWishlist } = useWishlist()
  const navigate = useNavigate()
  const [wishlisted, setWishlisted] = useState(false)
  const [imgSrc, setImgSrc] = useState(
    product.image_url || makePlaceholder(product.platform)
  )

  // Open the real platform URL in a new tab
  const handleCardClick = () => {
    if (product.product_url) {
      window.open(product.product_url, '_blank', 'noopener,noreferrer')
    }
  }

  const handleWishlist = async () => {
    // Not logged in — save product_id to localStorage and redirect to login
    if (!user) {
      setPendingWishlist(product.id)
      toast('Please login to save to wishlist', { icon: '🔐' })
      navigate('/login')
      return
    }

    if (wishlisted) {
      toast('Already in wishlist ❤️')
      return
    }

    if (!product.id) {
      toast.error('Product not ready, please try again')
      return
    }

    try {
      await shoppingAPI.addWishlist({ product_id: product.id })
      setWishlisted(true)
      toast.success('Added to wishlist ❤️')
      onWishlist?.()
    } catch (err) {
      const detail = err.response?.data?.detail || ''
      if (detail.toLowerCase().includes('already')) {
        setWishlisted(true)
        toast('Already in wishlist ❤️')
      } else {
        toast.error('Failed to add to wishlist')
      }
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      onClick={handleCardClick}
      className={`glass rounded-2xl overflow-hidden card-hover group ${product.product_url ? 'cursor-pointer' : ''}`}
    >
      {/* Image */}
      <div className="relative h-44 bg-gradient-to-br from-slate-800 to-slate-900 overflow-hidden">
        <img
          src={imgSrc}
          alt={product.title}
          onError={() => setImgSrc(makePlaceholder(product.platform))}
          className="w-full h-full object-cover opacity-90 group-hover:opacity-100 group-hover:scale-105 transition-all duration-300"
          loading="lazy"
        />

        {/* Discount badge */}
        {product.discount > 0 && (
          <div className="absolute top-3 left-3 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-lg shadow">
            -{product.discount?.toFixed(0)}%
          </div>
        )}

        {/* Platform badge */}
        <div className="absolute top-3 right-3">
          <Badge color={PLATFORM_COLORS[product.platform] || 'indigo'}>
            {product.platform}
          </Badge>
        </div>

        {/* Wishlist button — stop propagation so it doesn't trigger card click */}
        <button
          onClick={(e) => { e.stopPropagation(); handleWishlist() }}
          className={`absolute bottom-3 right-3 w-9 h-9 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg
            ${wishlisted
              ? 'bg-pink-500'
              : 'glass hover:bg-pink-500/40'
            }`}
        >
          <Heart
            size={15}
            className={wishlisted ? 'text-white fill-white' : 'text-pink-400'}
          />
        </button>
      </div>

      {/* Content */}
      <div className="p-4">
        <p className="text-white font-medium text-sm leading-tight mb-3 line-clamp-2">
          {product.title}
        </p>

        {/* Price */}
        <div className="flex items-baseline gap-2 mb-3">
          <span className="text-xl font-bold text-white">
            ₹{product.price?.toLocaleString('en-IN')}
          </span>
          {product.original_price > product.price && (
            <span className="text-slate-500 text-sm line-through">
              ₹{product.original_price?.toLocaleString('en-IN')}
            </span>
          )}
        </div>

        {/* Rating */}
        {product.rating && (
          <div className="flex items-center gap-2 mb-3">
            <div className="flex items-center gap-1 bg-yellow-500/20 px-2 py-0.5 rounded-lg">
              <Star size={12} className="text-yellow-400 fill-yellow-400" />
              <span className="text-yellow-300 text-xs font-medium">{product.rating}</span>
            </div>
            <span className="text-slate-500 text-xs">
              ({product.review_count?.toLocaleString()} reviews)
            </span>
          </div>
        )}

        {/* Delivery */}
        {product.delivery_time && (
          <div className="flex items-center gap-1.5 mb-4">
            <Truck size={12} className="text-indigo-400" />
            <span className="text-slate-400 text-xs">{product.delivery_time}</span>
          </div>
        )}

        {/* Availability + Link */}
        <div className="flex items-center justify-between">
          <Badge color={product.availability ? 'green' : 'red'}>
            {product.availability ? '✓ In Stock' : '✗ Out of Stock'}
          </Badge>
          {product.product_url && (
            <a
              href={product.product_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 text-xs transition-colors"
            >
              View <ExternalLink size={10} />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  )
}
