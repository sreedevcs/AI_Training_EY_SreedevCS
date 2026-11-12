// function Product(props)
// {
//   return(
//     <div>
//       <h2>{props.name}</h2>
//       <p>Price: {props.price}</p>
//     </div>
//   )
// }

// import Product from './product'

// function App()
// {
//   const products = [
//     { id:1, name: "Wireless Mouse", price: 1200 },
//     { id:2, name: "Keyboard", price: 2500 },
//     { id:3, name: "Monitor", price: 12000 }
//   ];
//   return (
//     <div>
//       <h1>Product List</h1>
//       {products.map((product) => (
//         <Product
//           key={product.id}
//           name={product.name}
//           price={product.price}
//         />
//       ))}
//     </div>
//   )
// }

// export default App


// function App()
// {
//   return(
//     <div>
//       <h1>Product List</h1>
//       <Product name="Wireless Mouse" price="1200"/>
//       <Product name="Keyboard" price="2500"/>
//       <Product name="Monitor" price="12000"/>
//     </div>
//   )
// }

// export default App




// import { useState } from "react"
// import Product from "./product"

// function App() {

//   const [products, setProducts] = useState([
//     { id: 1, name: "Wireless Mouse", price: 1200 },
//     { id: 2, name: "Keyboard", price: 2500 },
//     { id: 3, name: "Monitor", price: 12000 }
//   ])

//   const [name, setName] = useState("")
//   const [price, setPrice] = useState("")

//   function addProduct() {
//     const newProduct = {
//       id: products.length + 1,
//       name: name,
//       price: price
//     }

//     setProducts([...products, newProduct])

//     setName("")
//     setPrice("")
//   }

//   return (
//     <div>
//       <h1>Product List</h1>

//       <input
//         type="text"
//         placeholder="Product name"
//         value={name}
//         onChange={(e) => setName(e.target.value)}
//       />

//       <input
//         type="number"
//         placeholder="Price"
//         value={price}
//         onChange={(e) => setPrice(e.target.value)}
//       />

//       <button onClick={addProduct}>
//         Add Product
//       </button>

//       {products.map((product) => (
//         <Product
//           key={product.id}
//           name={product.name}
//           price={product.price}
//         />
//       ))}
//     </div>
//   )
// }

// export default App

// import { useState } from "react"
// import Product from "./product"

// function App() {
//   const [products, setProducts] = useState([
//     { id: 1, name: "Wireless Mouse", price: 1200 },
//     { id: 2, name: "Keyboard", price: 2500 }
//   ])

//   const [name, setName] = useState("")
//   const [price, setPrice] = useState("")

//   function addProduct(event) {
//     event.preventDefault()

//     const newProduct = {
//       id: products.length + 1,
//       name: name,
//       price: price
//     }

//     setProducts([...products, newProduct])

//     setName("")
//     setPrice("")
//   }

//   return (
//     <div>
//       <h1>Product List</h1>

//       <form onSubmit={addProduct}>

//         <input
//           type="text"
//           placeholder="Product name"
//           value={name}
//           onChange={(e) => setName(e.target.value)}
//         />

//         <input
//           type="number"
//           placeholder="Price"
//           value={price}
//           onChange={(e) => setPrice(e.target.value)}
//         />

//         <button type="submit">
//           Add Product
//         </button>

//       </form>

//       {products.map((product) => (
//         <Product
//           key={product.id}
//           name={product.name}
//           price={product.price}
//         />
//       ))}

//     </div>
//   )
// }

// export default App

import { useEffect, useState } from "react"

function App() {
  const [products, setProducts] = useState([])

  useEffect(() => {
    fetch("http://127.0.0.1:8000/products")
      .then((response) => response.json())
      .then((data) => {
        setProducts(data)
      })
      .catch((error) => {
        console.error("Error fetching products:", error)
      })
  }, [])

  return (
    <div>
      <h1>Product Store</h1>

      {products.map((product) => (
        <div key={product.id}>
          <img
            src={product.image}
            alt={product.name}
            width="180"
          />

          <h2>{product.name}</h2>

          <p>Price: ₹{product.price}</p>

          <hr />
        </div>
      ))}
    </div>
  )
}

export default App




// import { useState } from 'react'
// import heroImg from './assets/hero.png'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           type="button"
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App
