# from cryptography.fernet import Fernet
# import sqlite3

# key = open("secret.key","rb").read()
# f = Fernet(key)
# conn = sqlite3.connect("telematics.db")
# cur = conn.cursor()

# cur.execute("SELECT id, lat_enc, lon_enc FROM telemetry_secure LIMIT 5")
# for row in cur.fetchall():
#     id_, lat_enc, lon_enc = row
#     lat = f.decrypt(lat_enc.encode()).decode()
#     lon = f.decrypt(lon_enc.encode()).decode()
#     print(id_, lat, lon)
# conn.close()
