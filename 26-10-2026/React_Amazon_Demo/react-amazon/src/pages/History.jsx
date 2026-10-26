import { Link } from 'react-router-dom'
import { formatPrice } from '../data/products'

function OrderHistory({ orders }) {
  if (orders.length === 0) {
    return (
      <main>
        <h1>Order history</h1>
        <p>You have not placed any orders yet!</p>
        <Link to="/products">Browse products</Link>
      </main>
    )
  }
const paymentMethodLabels = {
  card: 'CARD',
  cod: 'CASH ON DELIVERY',
  upi: 'UPI',
  netbanking: 'NET BANKING',
}
  return (
    <main>
      <h1>Order history</h1>

      {orders.map((order) => (
        <article key={order.id}>
          <h2>Order {order.id}</h2>
          <p>
            Placed: {new Date(order.date).toLocaleString()}
          </p>
          <p>Status: {order.status}</p>
          <p>
            Payment method:{' '}
            {paymentMethodLabels[order.paymentMethod] ?? order.paymentMethod}
            </p>

          <ul>
            {order.items.map((item) => (
              <li key={item.id}>
                {item.name} × {item.quantity} {' : '}
                {formatPrice(item.price * item.quantity)}
              </li>
            ))}
          </ul>

          <strong>Total: {formatPrice(order.total)}</strong>
        </article>
      ))}
    </main>
  )
}

export default OrderHistory