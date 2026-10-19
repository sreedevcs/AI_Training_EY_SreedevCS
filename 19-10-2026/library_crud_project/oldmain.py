import psycopg2
# from pydantic import BaseModel
# from fastapi import FastAPI, HTTPException
# app=FastAPI()
#
# class Books(BaseModel):
#     book_id:int
#     title:str
#     author:str
#     category:str
#     price:float
#     stock:int

def get_connection():
    conn= psycopg2.connect(host="localhost",user="postgres",password="Admin@123",database="library_store")
    print("Connected to PostgreSQL successfully")
    return conn

# @app.get("/books")
# def get_books():
#     conn=get_connection()
#     cursor=conn.cursor()
#     cursor.execute("select * from books")
#     rows=cursor.fetchall()
#     cursor.close()
#     conn.close()
#     return rows
#
# @app.post("/books")
# def add_book(book:Books):
#     conn=get_connection()
#     cursor=conn.cursor()
#     cursor.execute("""insert into books(book_id,title,author,category,price,stock) values(%s,%s,%s,%s,%s,%s)""",(book.book_id,book.title,book.author,book.category,book.price,book.stock))
#     conn.commit()
#     return {
#         "message":"Book added",
#         "book":book
#     }


conn=get_connection()
cursor=conn.cursor()

# cursor.execute("""
#     INSERT INTO books
#     (book_id, title, author, category, price, stock)
#     VALUES
#     (201, 'Atomic Habits', 'James Clear', 'Self Help', 650, 12),
#     (202, 'Clean Code', 'Robert Martin', 'Technology', 900, 8),
#     (203, 'The Alchemist', 'Paulo Coelho', 'Fiction', 500, 15),
#     (204, 'Deep Work', 'Cal Newport', 'Productivity', 700, 10)
# """)
conn.commit()

print("Books inserted successfully")

print("The books are: ")
cursor.execute("select * from books")
for item in cursor.fetchall():
    print(item)


cursor.execute("select * from books where category='Technology'")
print("Category \'technology\' books: ")
for item in cursor.fetchall():
    print(item)

cursor.execute("""
    SELECT * FROM books
    WHERE price>600
""")
print("\nBooks with price greater than 600:")
for book in cursor.fetchall():
    print(book)

cursor.execute("""update books
               set price=950
               where price=202""")
conn.commit()
print("Price updated from 202 to 950")

cursor.execute("""
    UPDATE books
    SET stock = 14
    WHERE book_id = 204
""")
conn.commit()
print("Stock updated from 204 to 14")


# 9. Display the updated records
cursor.execute("""
    SELECT * FROM books
    WHERE book_id IN (202, 204)
    ORDER BY book_id
""")
print("\nUpdated records:")
for book in cursor.fetchall():
    print(book)


cursor.execute("""
    DELETE FROM books
    WHERE book_id = 203
""")
conn.commit()
print("\nBook 203 deleted successfully")


cursor.execute("SELECT * FROM books ORDER BY book_id")
print("\nRemaining books:")
for book in cursor.fetchall():
    print(book)


cursor.execute("""
    INSERT INTO books
    (book_id, title, author, category, price, stock)
    VALUES
    (205, 'English', 'Sreedev',
     'Technology', 800, 20)
""")
conn.commit()


cursor.execute("""
    SELECT * FROM books
    ORDER BY price DESC
    LIMIT 1
""")
print("\nBook with the highest price:")
print(cursor.fetchone())


cursor.execute("""
    SELECT SUM(stock) FROM books
""")
print("\nTotal stock available:")
print(cursor.fetchone()[0])


cursor.execute("""
    SELECT category, COUNT(*)
    FROM books
    GROUP BY category
    ORDER BY category
""")
print("\nNumber of books in each category:")
for row in cursor.fetchall():
    print(row)


cursor.close()
conn.close()
