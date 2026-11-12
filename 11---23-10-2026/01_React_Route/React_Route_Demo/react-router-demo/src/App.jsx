// // import { BrowserRouter, Routes, Route, Link } from "react-router-dom"

// // import Home from "./Home"
// // import Products from "./Products"
// // import About from "./About"

// // function App() {
// //   return (
// //     <BrowserRouter>

// //       <nav>
// //         <Link to="/">Home</Link>
// //         {" | "}
// //         <Link to="/products">Products</Link>
// //         { " | " }
// //         <Link to="/about">About</Link>
// //       </nav>

// //       <Routes>

// //         <Route
// //           path="/"
// //           element={<Home />}
// //         />

// //         <Route
// //           path="/products"
// //           element={<Products />}
// //         />

// //         <Route
// //           path="/about"
// //           element={<About />}
// //         />

// //       </Routes>

// //     </BrowserRouter>
// //   )
// // }

// // export default App

// import {
//   BrowserRouter,
//   Routes,
//   Route,
//   Link,
//   useParams
// } from "react-router-dom"

// function Home() {
//   return <h1>Home</h1>
// }

// function Products() {
//   const products = [
//     { id: 1, name: "Wireless Mouse" },
//     { id: 2, name: "Keyboard" },
//     { id: 3, name: "Monitor" }
//   ]

//   return (
//     <div>
//       <h1>Products</h1>

//       {products.map((product) => (
//         <div key={product.id}>
//           <Link to={`/products/${product.id}`}>
//             {product.name}
//           </Link>
//         </div>
//       ))}
//     </div>
//   )
// }

// function ProductDetails() {
//   const { id } = useParams()

//   return (
//     <div>
//       <h1>Product Details</h1>
//       <p>Product ID: {id}</p>
//     </div>
//   )
// }

// function About() {
//   return <h1>About</h1>
// }

// function App() {
//   return (
//     <BrowserRouter>
//       <nav>
//         <Link to="/">Home</Link>
//         {" | "}
//         <Link to="/products">Products</Link>
//         {" | "}
//         <Link to="/about">About</Link>
//       </nav>

//       <Routes>
//         <Route path="/" element={<Home />} />
//         <Route path="/products" element={<Products />} />
//         <Route path="/products/:id" element={<ProductDetails />} />
//         <Route path="/about" element={<About />} />
//       </Routes>
//     </BrowserRouter>
//   )
// }

// export default App


// import {
//   BrowserRouter,
//   Routes,
//   Route,
//   Link,
//   useParams,
//   useNavigate
// } from "react-router-dom"

// function Home() {
//   const navigate = useNavigate()

//   return (
//     <div>
//       <h1>Home</h1>

//       <button onClick={() => navigate("/products")}>
//         View Products
//       </button>
//     </div>
//   )
// }

// function Products() {
//   const products = [
//     { id: 1, name: "Wireless Mouse" },
//     { id: 2, name: "Keyboard" },
//     { id: 3, name: "Monitor" }
//   ]

//   return (
//     <div>
//       <h1>Products</h1>

//       {products.map((product) => (
//         <div key={product.id}>
//           <Link to={`/products/${product.id}`}>
//             {product.name}
//           </Link>
//         </div>
//       ))}
//     </div>
//   )
// }

// function ProductDetails() {
//   const { id } = useParams()
//   const navigate = useNavigate()

//   return (
//     <div>
//       <h1>Product Details</h1>

//       <p>Product ID: {id}</p>

//       <button onClick={() => navigate("/products")}>
//         Back to Products
//       </button>
//     </div>
//   )
// }

// function About() {
//   return <h1>About</h1>
// }

// function App() {
//   return (
//     <BrowserRouter>
//       <nav>
//         <Link to="/">Home</Link>
//         {" | "}
//         <Link to="/products">Products</Link>
//         {" | "}
//         <Link to="/about">About</Link>
//       </nav>

//       <Routes>
//         <Route path="/" element={<Home />} />
//         <Route path="/products" element={<Products />} />
//         <Route path="/products/:id" element={<ProductDetails />} />
//         <Route path="/about" element={<About />} />
//       </Routes>
//     </BrowserRouter>
//   )
// }

// export default App


import { useState, useEffect } from "react"
import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useParams,
  useNavigate
} from "react-router-dom"

function Home() {
  const navigate = useNavigate()

  return (
    <div>
      <h1>Home</h1>

      <button onClick={() => navigate("/products")}>
        View Products
      </button>
    </div>
  )
}

function Products() {
  // const products = [
  //   { id: 1, name: "Wireless Mouse" },
  //   { id: 2, name: "Keyboard" },
  //   { id: 3, name: "Monitor" }
  // ]
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
      <h1>Products</h1>

      {products.map((product) => (
        <div key={product.id}>
          <Link to={`/products/${product.id}`}>
            {product.name}
          </Link>
        </div>
      ))}
    </div>
  )
}

function ProductDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState([])
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/products/${id}`)
      .then((response) => response.json())
      .then((data) => setProduct(data))
      .catch((error) => {
        console.error("Error fetching product:", error)
      })
  }, [id])

  if (!product) return <p>Loading product...</p>

  return (
    <div>
      <h1>{product.id}</h1>
      <h1>{product.name}</h1>
      <img src={product.image} alt={product.name} width="200" />
      <p>Price: ₹{product.price}</p>

      <button onClick={() => navigate("/products")}>
        Back to Products
      </button>
    </div>
  )
}

function AddProduct() {
  const navigate = useNavigate()

  const [id, setId] = useState("")
  const [name, setName] = useState("")
  const [price, setPrice] = useState("")
  const [image, setImage] = useState("")

  function saveProduct(event) {
    event.preventDefault()

    const product = {
      id: Number(id),
      name: name,
      price: Number(price),
      image: image
    }

    fetch("http://127.0.0.1:8000/products", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(product)
    })
      .then((response) => response.json())
      .then(() => {
        navigate("/products")
      })
  }

  return (
    <div>
      <h1>Add Product</h1>

      <form onSubmit={saveProduct}>
        <input
          type="number"
          placeholder="Product ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />

        <br />

        <input
          type="text"
          placeholder="Product Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <br />

        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />

        <br />

        <input
          type="text"
          placeholder="Image URL"
          value={image}
          onChange={(e) => setImage(e.target.value)}
        />

        <br />

        <button type="submit">
          Save Product
        </button>
      </form>
    </div>
  )
}

function EditProduct() {
  const navigate = useNavigate()

  const [id, setId] = useState("")
  const [name, setName] = useState("")
  const [price, setPrice] = useState("")
  const [image, setImage] = useState("")

  function saveProduct(event) {
    event.preventDefault()

    const product = {
      id: Number(id),
      name: name,
      price: Number(price),
      image: image
    }

    fetch(`http://127.0.0.1:8000/products/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(product)
    })
      .then((response) => response.json())
      .then(() => {
        navigate("/products")
      })
  }

  return (
    <div>
      <h1>Edit Product</h1>

      <form onSubmit={saveProduct}>
        <input
          type="number"
          placeholder="Product ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />

        <br />

        <input
          type="text"
          placeholder="Product Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <br />

        <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />

        <br />

        <input
          type="text"
          placeholder="Image URL"
          value={image}
          onChange={(e) => setImage(e.target.value)}
        />

        <br />

        <button type="submit">
          Save Product
        </button>
      </form>
    </div>
  )
}

function DeleteProduct() {
  const navigate = useNavigate()

  const [id, setId] = useState("")
  const [name, setName] = useState("")
  const [price, setPrice] = useState("")
  const [image, setImage] = useState("")

  function saveProduct(event) {
    event.preventDefault()

    const product = {
      id: Number(id),
      name: name,
      price: Number(price),
      image: image
    }

    fetch(`http://127.0.0.1:8000/products/${id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(product)
    })
      .then((response) => response.json())
      .then(() => {
        navigate("/products")
      })
  }

  return (
    <div>
      <h1>Delete Product</h1>

      <form onSubmit={saveProduct}>
        <input
          type="number"
          placeholder="Product ID"
          value={id}
          onChange={(e) => setId(e.target.value)}
        />

        {/* <br /> */}

        {/* <input
          type="text"
          placeholder="Product Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <br /> */}

        {/* <input
          type="number"
          placeholder="Price"
          value={price}
          onChange={(e) => setPrice(e.target.value)}
        />

        <br /> */}

        {/* <input
          type="text"
          placeholder="Image URL"
          value={image}
          onChange={(e) => setImage(e.target.value)}
        /> */}

        <br />

        <button type="submit">
          Delete Product
        </button>
      </form>
    </div>
  )
}


function About() {
  return <h1>About</h1>
}

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        {" | "}
        <Link to="/products">Products</Link>
        {" | "}
        <Link to="/add-product">Add Product</Link>
        {" | "}
        <Link to="/about">About</Link>
        {" | "}
        <Link to="/edit-product">Edit Product</Link>
        {" | "}
        <Link to="/delete-product">Delete Product</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetails />} />
        <Route path="/add-product" element={<AddProduct />} />
        <Route path="/about" element={<About />} />
        <Route path="/edit-product" element={<EditProduct/>} />
        <Route path="/delete-product" element={<DeleteProduct/>} />
      </Routes>
    </BrowserRouter>
  )
}
  

export default App