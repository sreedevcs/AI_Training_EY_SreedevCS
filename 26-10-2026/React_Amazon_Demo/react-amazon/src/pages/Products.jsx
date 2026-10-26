import { Link, useSearchParams } from 'react-router-dom'
import { products } from '../data/products'
import ProductDisplay from '../components/ProductDisplay'

function Products({ onAddToCart }) {
  const [searchParams] = useSearchParams()
  const query = (searchParams.get('q') || '').trim().toLowerCase()

  const results = products.filter((product) =>
    `${product.name} ${product.category}`.toLowerCase().includes(query),
  )

  return (
    <main>
      <h1>{query ? `Search results for "${query}"` : 'All products'}</h1>

      {results.length > 0 ? (
        <div className="product-grid">
          {results.map((product) => (
            <ProductDisplay
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
            />
          ))}
        </div>
      ) : (
        <section>
          <p>No matching products found.</p>
          <Link to="/products">Browse all products</Link>
        </section>
      )}
    </main>
  )
}

export default Products