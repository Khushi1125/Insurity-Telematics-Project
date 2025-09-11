import sqlite3

conn = sqlite3.connect("telematics.db")
cur = conn.cursor()

with open("Schema.sql", "r") as f:
    cur.executescript(f.read())

conn.commit()
conn.close()