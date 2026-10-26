import { useEffect, useState } from 'react'
import { Link, Route, Routes, useNavigate } from 'react-router-dom'

import Cart from './pages/Cart'
import Home from './pages/Home'
import Login from './pages/Login'
import OrderHistory from './pages/History'
import Payment from './pages/Payment'
import Products from './pages/Products'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const [cart, setCart] = useState([])
  const [search, setSearch] = useState('')
  const [orders, setOrders] = useState(() => {
    const savedOrders = localStorage.getItem('shopwise-orders')
    return savedOrders ? JSON.parse(savedOrders) : []
  })
  const [isLoggedIn, setIsLoggedIn] = useState(
    () => localStorage.getItem('shopwise-logged-in') === 'true',
  )

  const navigate = useNavigate()

  useEffect(() => {
    localStorage.setItem('shopwise-orders', JSON.stringify(orders))
  }, [orders])

  function handleSearch(event) {
    event.preventDefault()
    navigate(`/products?q=${encodeURIComponent(search.trim())}`)
  }

  function handleLogin() {
    localStorage.setItem('shopwise-logged-in', 'true')
    setIsLoggedIn(true)
  }

  function handleLogout() {
    localStorage.removeItem('shopwise-logged-in')
    setIsLoggedIn(false)
  }

  function addToCart(product) {
    setCart((currentCart) => {
      const existingItem = currentCart.find((item) => item.id === product.id)

      if (existingItem) {
        return currentCart.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        )
      }

      return [...currentCart, { ...product, quantity: 1 }]
    })
  }

  function removeFromCart(productId) {
    setCart((currentCart) =>
      currentCart.filter((item) => item.id !== productId),
    )
  }

  function changeQuantity(productId, quantity) {
    setCart((currentCart) =>
      currentCart.map((item) =>
        item.id === productId ? { ...item, quantity } : item,
      ),
    )
  }

  function completePayment({ paymentMethod }) {
    const order = {
      id: `ORDER-${Date.now()}`,
      date: new Date().toISOString(),
      items: cart.map((item) => ({ ...item })),
      total: cart.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0,
      ),
      paymentMethod,
      status: 'Confirmed',
    }

    setOrders((currentOrders) => [order, ...currentOrders])
    setCart([])
  }

  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <>
      <header>
        <Link to="/">AMAZON</Link>

        <form onSubmit={handleSearch}>
          <input
            type="search"
            placeholder="Search products"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Search products"
          />
          <button type="submit">Search</button>
        </form>

        <nav aria-label="Main navigation">
          <Link to="/">Home</Link>
          {' | '}
          <Link to="/products">Products</Link>
          {' | '}
          <Link to="/cart">Cart ({cartCount})</Link>
          {' | '}
          <Link to="/orders">Order history</Link>
          {'   '}
          {isLoggedIn ? (
            <button type="button" onClick={handleLogout}>
              Log out
            </button>
          ) : (
            <button type="button" onClick={() => navigate('/login')}>
              Log in
            </button>
          )}
        </nav>
      </header>

      <Routes>
        <Route path="/" element={<Home onAddToCart={addToCart} />} />
        <Route
          path="/products"
          element={<Products onAddToCart={addToCart} />}
        />
        <Route
          path="/cart"
          element={
            <Cart
              cart={cart}
              onRemoveFromCart={removeFromCart}
              onQuantityChange={changeQuantity}
            />
          }
        />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />

        <Route element={<ProtectedRoute isLoggedIn={isLoggedIn} />}>
          <Route
            path="/payment"
            element={
              <Payment
                cart={cart}
                onPaymentComplete={completePayment}
              />
            }
          />
          <Route
            path="/orders"
            element={<OrderHistory orders={orders} />}
          />
        </Route>

        <Route
          path="*"
          element={
            <main>
              <h1>The requested page was not found. Try again with the correct URL!</h1>
              <Link to="/">Go home</Link>
            </main>
          }
        />
      </Routes>
    </>
  )
}

export default App

