# import required libraries
import psycopg2
import os
from dotenv import load_dotenv
# -------------------------------------------------------------------------
# load dotenv
load_dotenv()
# -------------------------------------------------------------------------
# create a connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()
print("-"*50)
print("Database connected successfully...")
print("-"*50)
# -------------------------------------------------------------------------
# create a table
cursor.execute( 
    """
    CREATE TABLE IF NOT EXISTS users(
    name VARCHAR(20),
    age INT
    );
    """
)
conn.commit()
print("Table created...")
print("-"*50)
# -------------------------------------------------------------------------
# insert data
users_data = [
        ('Bhushan', 22),
        ('Shubham', 20),
        ('Samu', 22),
        ('Shruti', 20)
    ]

cursor.executemany(
        "INSERT INTO users (name, age) VALUES (%s, %s)",
        users_data
    )
conn.commit()
print("Data inserted...")
print("-"*50)
# -------------------------------------------------------------------------
# fetch all data
print("Fetch all data")
cursor.execute("SELECT * FROM users;")
records = cursor.fetchall()
print(records)
print("-"*50)
# -------------------------------------------------------------------------
print("Record updated...")
# update record
cursor.execute(
    "UPDATE users SET age=%s WHERE name=%s", (23, "Bhushan")
)
conn.commit()
print("-"*50)
# -------------------------------------------------------------------------
# fetch all data
cursor.execute("SELECT * FROM users;")
records = cursor.fetchall()
print(records)
print("-"*50)
# -------------------------------------------------------------------------
# delete record
cursor.execute("DELETE FROM users WHERE name=%s", ("Bhushan",))
conn.commit()
print("Record Deleted...")
print("-"*50)
# -------------------------------------------------------------------------
# fetch all data
print("Fetch all data")
cursor.execute("SELECT * FROM users;")
records = cursor.fetchall()
print(records)
print("-"*50)
# -------------------------------------------------------------------------
# terminate connection
cursor.close()
conn.close()
# -------------------------------------------------------------------------



