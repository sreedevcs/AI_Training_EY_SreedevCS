import { formatPrice } from '../data/products'

function ProductDisplay({ product, onAddToCart }) {
  return (
    <article className="product-display">
      <img src={product.image} alt={product.name} />
      <p>{product.category}</p>
      <h2>{product.name}</h2>
      <strong>{formatPrice(product.price)}</strong>
      {"     "}
      <button type="button" onClick={() => onAddToCart(product)}>
        Add to cart
      </button>
    </article>
  )
}

export default ProductDisplay