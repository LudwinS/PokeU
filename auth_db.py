import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Tuple

DB_NAME = "auth.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            profile_name TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# --- Utilidades ---

ALLOWED_DOMAINS = ("@clasess.edu.sv", "@ugb.edu.sv")

def is_valid_email(email: str) -> bool:
    email = email.strip().lower()
    if "@" not in email:
        return False
    return email.endswith(ALLOWED_DOMAINS)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def is_valid_profile_name(profile_name: str) -> bool:
    # Puedes poner tus reglas (sin espacios, longitud mínima, etc.)
    profile_name = profile_name.strip()
    return len(profile_name) >= 3

# --- Funciones principales ---

def register_user(email: str, password: str, profile_name: str) -> Tuple[bool, str]:
    """
    Registra un nuevo usuario con email, contraseña y nombre de perfil único.
    Devuelve (ok, mensaje)
    """
    email = email.strip().lower()
    profile_name = profile_name.strip()

    if not is_valid_email(email):
        return False, "Solo se permiten correos @clasess.edu.sv o @ugb.edu.sv"

    if len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres"

    if not is_valid_profile_name(profile_name):
        return False, "El nombre de perfil debe tener al menos 3 caracteres"

    conn = get_connection()
    cur = conn.cursor()

    # Verificar si ya existe ese nombre de perfil
    cur.execute("SELECT id FROM users WHERE profile_name = ?", (profile_name,))
    if cur.fetchone() is not None:
        conn.close()
        return False, "Ese nombre de perfil ya está en uso, elige otro"

    try:
        cur.execute(
            "INSERT INTO users (email, profile_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, profile_name, hash_password(password), datetime.now().isoformat())
        )
        conn.commit()
        return True, "Usuario registrado correctamente"
    except sqlite3.IntegrityError:
        return False, "Ya existe una cuenta con ese correo"
    finally:
        conn.close()

def login_user(email: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Intenta iniciar sesión.
    Devuelve (ok, mensaje, profile_name_o_None).
    Si ok=True, profile_name tendrá el nombre del perfil.
    """
    email = email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT password_hash, profile_name FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "No existe una cuenta con ese correo", None

    stored_hash, profile_name = row
    if stored_hash == hash_password(password):
        return True, "Inicio de sesión exitoso", profile_name
    else:
        return False, "Contraseña incorrecta", None
