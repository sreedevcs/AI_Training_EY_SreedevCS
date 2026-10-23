from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product model
class Product(BaseModel):
    id: int
    name: str
    price: float
    image: str

import psycopg2
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="product_store",
        user="postgres",
        password="Admin@123"
    )

# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Product API is running"
    }
@app.get("/products")
def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, price, image
        FROM products
        ORDER BY id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    products = []
    for row in rows:
        products.append({
        "id": row[0],
        "name": row[1],
        "price": float(row[2]),
        "image": row[3]
        })
    return products



# GET product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    conn = get_connection()
    cursor=conn.cursor()
    cursor.execute(
                """
                SELECT id, name, price, image
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": row[0],
        "name": row[1],
        "price": float(row[2]),
        "image": row[3],
    }