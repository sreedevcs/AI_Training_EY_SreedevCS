export const products = [
  {
    id: 1,
    name: 'Wireless headphones',
    category: 'Electronics',
    price: 1500,
    image:
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 2,
    name: 'Everyday wristwatch',
    category: 'Accessories',
    price: 2300,
    image:
      'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 3,
    name: 'Compact digital camera',
    category: 'Electronics',
    price: 5400,
    image:
      'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 4,
    name: 'Lightweight sneakers',
    category: 'Fashion',
    price: 780,
    image:
      'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80',
  },
  {
  id: 5,
  name: 'Gaming Keyboard',
  category: 'Electronics',
  price: 3200,
  image:
    'https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?auto=format&fit=crop&w=600&q=80',
},
{
  id: 6,
  name: 'Bluetooth Speaker',
  category: 'Electronics',
  price: 1850,
  image:
    'https://images.unsplash.com/photo-1589003077984-894e133dabab?auto=format&fit=crop&w=600&q=80',
},
{
  id: 7,
  name: 'Travel Backpack',
  category: 'Accessories',
  price: 1450,
  image:
    'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80',
},
{
  id: 8,
  name: 'Sunglasses',
  category: 'Accessories',
  price: 950,
  image:
    'https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=600&q=80',
},
{
  id: 9,
  name: 'Laptop Stand',
  category: 'Electronics',
  price: 1100,
  image:
    'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=600&q=80',
},
{
  id: 10,
  name: 'Running Shoes',
  category: 'Fashion',
  price: 2890,
  image:
    'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=600&q=80',
},
{
  id: 11,
  name: 'Leather Wallet',
  category: 'Accessories',
  price: 690,
  image:
    'https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=600&q=80',
},
{
  id: 12,
  name: 'Smartphone',
  category: 'Electronics',
  price: 18999,
  image:
    'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80',
},
{
  id: 13,
  name: 'Denim Jacket',
  category: 'Fashion',
  price: 2499,
  image:
    'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=600&q=80',
},
{
  id: 14,
  name: 'Coffee Mug',
  category: 'Home',
  price: 299,
  image:
    'https://images.unsplash.com/photo-1514228742587-6b1558fcf93a?auto=format&fit=crop&w=600&q=80',
},
{
  id: 15,
  name: 'Office Chair',
  category: 'Furniture',
  price: 7499,
  image:
    'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=600&q=80',
},
{
  id: 16,
  name: 'Mechanical Mouse',
  category: 'Electronics',
  price: 1299,
  image:
    'https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=600&q=80',
},
{
  id: 17,
  name: 'Fitness Tracker',
  category: 'Electronics',
  price: 3499,
  image:
    'https://images.unsplash.com/photo-1575311373937-040b8e1fd4d4?auto=format&fit=crop&w=600&q=80',
},
{
  id: 18,
  name: 'Table Lamp',
  category: 'Home',
  price: 1250,
  image:
    'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=600&q=80',
},
{
  id: 19,
  name: 'Water Bottle',
  category: 'Home',
  price: 499,
  image:
    'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=600&q=80',
},
{
  id: 20,
  name: 'Bean Bag',
  category: 'Furniture',
  price: 2999,
  image:
    'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=600&q=80',
}
]

export function formatPrice(price) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
  }).format(price)
}