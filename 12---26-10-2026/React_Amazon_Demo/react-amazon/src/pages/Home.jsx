import { Link } from 'react-router-dom'
import { products } from '../data/products'
import ProductDisplay from '../components/ProductDisplay'

function Home({ onAddToCart }) {
  const suggestedProducts = products.slice(0, 8)

  return (
    <main>
      <section>
        <h1>Welcome to Amazon</h1>
        <p>Discover useful favorites and everyday finds.</p>
        <Link to="/products">Browse all products</Link>
      </section>

      <section>
        <h2>Suggested for you</h2>
        <div className="product-grid">
          {suggestedProducts.map((product) => (
            <ProductDisplay
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
            />
          ))}
        </div>
      </section>
    </main>
  )
}

export default Home