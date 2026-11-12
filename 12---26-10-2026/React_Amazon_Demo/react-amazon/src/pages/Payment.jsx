import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { formatPrice } from '../data/products'

function Payment({ cart, onPaymentComplete }) {
  const [method, setMethod] = useState('card')
  const [isComplete, setIsComplete] = useState(false)
  const navigate = useNavigate()

  const total = cart.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0,
  )

  function handleSubmit(event) {
    event.preventDefault()

    if (cart.length === 0) {
      return
    }

    onPaymentComplete({ paymentMethod: method })
    setIsComplete(true)
  }

  // Check this before the empty-cart branch because completing the order
  // clears the cart.
  if (isComplete) {
    return (
      <main>
        <h1>Congratulations! Your order has been placed.</h1>
        
        <button type="button" onClick={() => navigate('/')}>
          Back to home
        </button>

        <button type="button" onClick={() => navigate('/orders')}>
          View order history
        </button>
      </main>
    )
  }

  if (cart.length === 0) {
    return (
      <main>
        <h1>EMPTY CART!</h1>
        <Link to="/products">Continue shopping</Link>
      </main>
    )
  }

  // Keep the existing payment form here.

  return (
    <main>
      <h1>Payment</h1>
      <p>Order total: {formatPrice(total)}</p>
      <p>
        Please select the preferred payment method and enter the required details to proceed with your order.
      </p>

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Choose a payment method</legend>

          <label>
            <input
              type="radio"
              name="paymentMethod"
              value="card"
              checked={method === 'card'}
              onChange={() => setMethod('card')}
            />
            Credit or debit card
          </label>

          <label>
            <input
              type="radio"
              name="paymentMethod"
              value="upi"
              checked={method === 'upi'}
              onChange={() => setMethod('upi')}
            />
            UPI
          </label>

          <label>
            <input
              type="radio"
              name="paymentMethod"
              value="netbanking"
              checked={method === 'netbanking'}
              onChange={() => setMethod('netbanking')}
            />
            Net banking
          </label>

          <label>
            <input
              type="radio"
              name="paymentMethod"
              value="cod"
              checked={method === 'cod'}
              onChange={() => setMethod('cod')}
            />
            Cash on delivery
          </label>
        </fieldset>

        {method === 'card' && (
          <section>
            <h2>Card details</h2>

            <label>
              Name on card
              <input name="cardName" autoComplete="off" required />
            </label>

            <label>
              Card number
              <input
                name="cardNumber"
                inputMode="numeric"
                autoComplete="off"
                required
              />
            </label>

            <label>
              Expiry date
              <input
                name="expiry"
                placeholder="MM/YY"
                autoComplete="off"
                required
              />
            </label>

            <label>
              CVV
              <input
                name="securityCode"
                inputMode="numeric"
                autoComplete="off"
                required
              />
            </label>
          </section>
        )}

        {method === 'upi' && (
          <label>
            UPI ID
            <input name="upiId" placeholder="name@example" required />
          </label>
        )}

        {method === 'netbanking' && (
          <label>
            Select your bank
            <select name="bank" required defaultValue="">
              <option value="" disabled>
                Choose a bank
              </option>
               <option value="demo-bank-a">State Bank of India</option>
               <option value="demo-bank-b">Bank of Baroda</option>
               <option value="demo-bank-c">HDFC Bank</option>
            </select>
          </label>
        )}

        <button type="submit">Confirm payment: {formatPrice(total)}</button>
      </form>
    </main>
  )
}

export default Payment

// import { useState } from 'react'
// import { Link, useNavigate } from 'react-router-dom'
// import { formatPrice } from '../data/products'

// function Payment({ cart, onPaymentComplete }) {
//   const [method, setMethod] = useState('card')
//   const [isComplete, setIsComplete] = useState(false)
//   const navigate = useNavigate()

//   const total = cart.reduce(
//     (sum, item) => sum + item.price * item.quantity,
//     0,
//   )

//   function handleSubmit(event) {
//     event.preventDefault()

//     // Demo only: no card details are sent or saved.
//     onPaymentComplete()
//     setIsComplete(true)
//   }

//   if (cart.length === 0 && !isComplete) {
//     return (
//       <main>
//         <h1>Empty Cart!</h1>
//         <Link to="/products">Continue shopping</Link>
//       </main>
//     )
//   }

//   if (isComplete) {
//     return (
//       <main>
//         <h1>Congratulations! Your order has been placed.</h1>
//         <p>Payment processed successfully.</p>
//         <button type="button" onClick={() => navigate('/')}>
//           Continue shopping
//         </button>
//       </main>
//     )
//   }

//   return (
//     <main>
//       <h1>Payment</h1>
//       <p>Order total: {formatPrice(total)}</p>
//       <p>
//         Please select the preferred payment method and enter the required details to proceed with your order.
//       </p>

//       <form onSubmit={handleSubmit}>
//         <fieldset>
//           <legend>Choose a payment method</legend>

//           <label>
//             <input
//               type="radio"
//               name="paymentMethod"
//               value="card"
//               checked={method === 'card'}
//               onChange={() => setMethod('card')}
//             />
//             Credit or debit card
//           </label>

//           <label>
//             <input
//               type="radio"
//               name="paymentMethod"
//               value="upi"
//               checked={method === 'upi'}
//               onChange={() => setMethod('upi')}
//             />
//             UPI
//           </label>

//           <label>
//             <input
//               type="radio"
//               name="paymentMethod"
//               value="netbanking"
//               checked={method === 'netbanking'}
//               onChange={() => setMethod('netbanking')}
//             />
//             Net banking
//           </label>

//           <label>
//             <input
//               type="radio"
//               name="paymentMethod"
//               value="cod"
//               checked={method === 'cod'}
//               onChange={() => setMethod('cod')}
//             />
//             Cash on delivery
//           </label>
//         </fieldset>

//         {method === 'card' && (
//           <section>
//             <h2>Card details</h2>

//             <label>
//               Name on card
//               <input name="cardName" autoComplete="off" required />
//             </label>

//             <label>
//               Card number
//               <input
//                 name="cardNumber"
//                 inputMode="numeric"
//                 autoComplete="off"
//                 required
//               />
//             </label>

//             <label>
//               Expiry date
//               <input
//                 name="expiry"
//                 placeholder="MM/YY"
//                 autoComplete="off"
//                 required
//               />
//             </label>

//             <label>
//               Security code
//               <input
//                 name="securityCode"
//                 inputMode="numeric"
//                 autoComplete="off"
//                 required
//               />
//             </label>
//           </section>
//         )}

//         {method === 'upi' && (
//           <label>
//             UPI ID
//             <input name="upiId" placeholder="name@example" required />
//           </label>
//         )}

//         {method === 'netbanking' && (
//           <label>
//             Select your bank
//             <select name="bank" required defaultValue="">
//               <option value="" disabled>
//                 Choose a bank
//               </option>
//               <option value="demo-bank-a">State Bank of India</option>
//               <option value="demo-bank-b">Bank of Baroda</option>
//               <option value="demo-bank-c">HDFC Bank</option>
//             </select>
//           </label>
//         )}

//         <button type="submit">Pay {formatPrice(total)}</button>
//       </form>
//     </main>
//   )
// }

// export default Payment