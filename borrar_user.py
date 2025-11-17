import sqlite3

DB_NAME = "auth.db" 

def borrar_usuario_por_email(email):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()

    filas = cur.rowcount 
    conn.close()

    if filas > 0:
        print(f"✅ Usuario con email '{email}' eliminado ({filas} fila(s)).")
    else:
        print(f"⚠ No se encontró ningún usuario con el email '{email}'.")


if __name__ == "__main__":

    correo = "jhoanortega2022@gmail.com"
    borrar_usuario_por_email(correo)
