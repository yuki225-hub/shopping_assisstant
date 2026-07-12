import { createContext, useContext, useState } from 'react'

const WishlistContext = createContext(null)

const STORAGE_KEY = 'pending_wishlist_product_id'

export function WishlistProvider({ children }) {
  const [pending, setPending] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? { product_id: parseInt(saved) } : null
  })

  const setPendingWishlist = (product_id) => {
    localStorage.setItem(STORAGE_KEY, String(product_id))
    setPending({ product_id })
  }

  const clearPending = () => {
    localStorage.removeItem(STORAGE_KEY)
    setPending(null)
  }

  return (
    <WishlistContext.Provider value={{ pending, setPendingWishlist, clearPending }}>
      {children}
    </WishlistContext.Provider>
  )
}

export const useWishlist = () => useContext(WishlistContext)
