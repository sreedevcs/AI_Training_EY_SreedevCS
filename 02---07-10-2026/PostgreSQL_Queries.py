import psycopg2
conn=psycopg2.connect(host="localhost",database="cinema_demo",user="postgres",password="Admin@123")
cursor=conn.cursor()
print("Connected to PostgreSQL")

# # cursor.execute("""
# # CREATE TABLE IF NOT EXISTS screenings (
# # screening_id SERIAL PRIMARY KEY,
# # movie_name VARCHAR(100),
# # screen_number INT,
# # show_time VARCHAR(20),
# # available_seats INT)
# # """)
#
# conn.commit()
# print("Table created")

# cursor.execute("""
# INSERT INTO screenings(movie_name,screen_number,show_time,available_seats)
# VALUES
# ('Silent Horizon',1,'10:00 AM',65),
# ('Red Planet',2,'01:30 PM',42),
# ('Ocean Signal',3,'04:00 PM',18),
# ('Silent Horizon',1,'07:00 PM',25)
# """)
# conn.commit()
# print("Records inserted")

# cursor.execute("select * from screenings")
# rows=cursor.fetchall()
# for row in rows:
#     print(row)

# cursor.execute("""select movie_name,show_time,available_seats from screenings
#  where available_seats<30""")
# rows=cursor.fetchall()
# for row in rows:
#     print(row)

# cursor.execute("""
# UPDATE screenings
# SET available_seats=available_seats-5
# WHERE screening_id=3""")

# conn.commit()
cursor.execute("select * from screenings")
rows=cursor.fetchall()
for row in rows:
    print(row)
