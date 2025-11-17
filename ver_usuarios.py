import sqlite3

DB_NAME = "auth.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute("SELECT id, email, profile_name,password_hash, created_at FROM users")

rows = cur.fetchall()

print("Usuarios registrados:\n")
for row in rows:
    user_id, email, profile_name, password_hash, created_at = row
    print(f"ID: {user_id}")
    print(f"Email: {email}")
    print(f"Nombre de perfil: {profile_name}")
    print(f"Hash de contraseña: {password_hash}")
    print(f"Creado: {created_at}")
    print("-" * 40)

conn.close()
