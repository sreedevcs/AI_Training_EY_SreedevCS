import psycopg2
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
app=FastAPI()

class Books(BaseModel):
    book_id:int
    title:str
    author:str
    category:str
    price:float
    stock:int

def get_connection():
    conn= psycopg2.connect(host="localhost",user="postgres",password="Admin@123",database="library_store")
    print("Connected to PostgreSQL successfully")
    return conn

@app.get("/")
def home():
    conn=get_connection()
    conn.close()
    return {"message" : "Successfully Connected to PostgreSQL"}

@app.post("/books/insert")
def insert_books():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        INSERT INTO books
        (book_id, title, author, category, price, stock)
        VALUES
        (201, 'Atomic Habits', 'James Clear', 'Self Help', 650, 12),
        (202, 'Clean Code', 'Robert Martin', 'Technology', 900, 8),
        (203, 'The Alchemist', 'Paulo Coelho', 'Fiction', 500, 15),
        (204, 'Deep Work', 'Cal Newport', 'Productivity', 700, 10)
    """)
    conn.commit()
    return {
        "message" : "Successfully Inserted Books"
    }

@app.get("/books")
def get_books():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""select * from books""")
    books=cursor.fetchall()
    return books


@app.get("/books/category/{category}")
def get_books_category(category):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""select * from books where category = %s""",(category,))
    return cursor.fetchall()

@app.get("/books/price/{price}")
def get_books_price(price):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""select * from books where price > %s""",(price,))
    return cursor.fetchall()


@app.put("/books/202/price")
def update_price():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""UPDATE books SET price=950 where book_id=202""")
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Book not found")
    conn.commit()
    return {"message" : "Successfully Updated Price"}

@app.put("/books/204/stock")
def update_price():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""UPDATE books SET stock=14 where book_id=204""")
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Book not found")
    conn.commit()
    return {"message" : "Successfully Updated Stock"}

@app.get("/books/updatedrecords")
def get_updated_records():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM BOOKS WHERE book_id IN (202,204)""")
    return cursor.fetchall()

@app.delete("/books/203")
def delete_book():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("DELETE FROM books WHERE book_id = 203")
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Book not found")
    conn.commit()
    return {"message": "Book 203 deleted successfully"}

@app.get("/books/remaining")
def get_remaining_books():
    return get_books()


@app.post("/books")
def add_book(book:Books):
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""
        INSERT INTO books
        (book_id, title, author, category, price, stock)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (book.book_id,book.title,book.author,book.category,book.price,book.stock))
    conn.commit()
    return {"message": "Book added successfully", "book": book}

@app.get("/books/highest-price")
def highest_price():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM books
            ORDER BY price DESC
            LIMIT 1
        """)
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="No books found")
    return row

@app.get("/books/total-stock")
def total_stock():
    conn=get_connection()
    cursor=conn.cursor()
    cursor.execute("SELECT SUM(stock) FROM books")
    return {"total_stock": cursor.fetchone()}

@app.get("/books/category-count")
def category_count():
    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute("""
        SELECT category, COUNT(*)
        FROM books
        GROUP BY category
    """)
    return cursor.fetchall()