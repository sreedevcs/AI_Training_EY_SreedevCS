import { Link, useNavigate } from 'react-router-dom'
import { formatPrice } from '../data/products'

function Cart({ cart, onRemoveFromCart, onQuantityChange }) {
  const navigate = useNavigate()

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  )

  if (cart.length === 0) {
    return (
      <main>
        <h1>Your cart is empty</h1>
        <Link to="/products">Continue shopping</Link>
      </main>
    )
  }

  return (
    <main>
      <h1>Your cart</h1>

      {cart.map((item) => (
        <article key={item.id}>
          <img src={item.image} alt={item.name} />
          <div>
            <h2>{item.name}</h2>
            <p>{formatPrice(item.price)}</p>

            <label>
              Quantity
              <select
                value={item.quantity}
                onChange={(event) =>
                  onQuantityChange(item.id, Number(event.target.value))
                }
              >
                {[1, 2, 3, 4, 5].map((quantity) => (
                  <option key={quantity} value={quantity}>
                    {quantity}
                  </option>
                ))}
              </select>
            </label>

            <button type="button" onClick={() => onRemoveFromCart(item.id)}>
              Remove
            </button>
          </div>
        </article>
      ))}

      <h2>Total: {formatPrice(total)}</h2>

      <button type="button" onClick={() => navigate('/payment')}>
      Confirm buy
      </button>

      <p>
        <Link to="/products">Continue shopping</Link>
      </p>
    </main>
  )
}

export default Cart