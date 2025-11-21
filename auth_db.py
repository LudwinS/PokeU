# auth_db.py
import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, Tuple
import re

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

ALLOWED_DOMAINS = ("@gmail.com",)

def is_valid_email(email: str) -> bool:
    email = email.strip().lower()
    if "@" not in email:
        return False
    return email.endswith(ALLOWED_DOMAINS)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def is_valid_profile_name(profile_name: str) -> bool:
    profile_name = profile_name.strip()
    return len(profile_name) >= 3

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Reglas:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un caracter especial !\"#$%&/()
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe incluir al menos una letra mayúscula"

    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe incluir al menos una letra minúscula"

    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe incluir al menos un número"

    if not re.search(r"[!\"#$%&/()]", password):
        return False, "La contraseña debe incluir al menos un caracter especial (!\"#$%&/())"

    return True, "Contraseña válida"

def email_exists(email: str) -> bool:
    email = email.strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def profile_name_exists(profile_name: str) -> bool:
    profile_name = profile_name.strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE profile_name = ?", (profile_name,))
    row = cur.fetchone()
    conn.close()
    return row is not None

# --- Funciones principales ---

def register_user(email: str, password: str, profile_name: str) -> Tuple[bool, str]:
    """
    Registra un nuevo usuario con email, contraseña y nombre de perfil único.
    Devuelve (ok, mensaje)
    """
    email = email.strip().lower()
    profile_name = profile_name.strip()

    if not is_valid_email(email):
        return False, "Solo se permiten correos @gmail.com"

    ok_pass, msg_pass = validate_password(password)
    if not ok_pass:
        return False, msg_pass

    if not is_valid_profile_name(profile_name):
        return False, "El nombre de perfil debe tener al menos 3 caracteres"

    conn = get_connection()
    cur = conn.cursor()

    # Verificar email y perfil por si acaso (aunque ya debimos comprobar antes)
    if email_exists(email):
        conn.close()
        return False, "Ya existe una cuenta con ese correo"

    if profile_name_exists(profile_name):
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
        return False, "Error al registrar usuario (correo o perfil ya en uso)"
    finally:
        conn.close()

def login_user(profile_name: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Intenta iniciar sesión usando NOMBRE DE PERFIL (usuario) y contraseña.
    Devuelve (ok, mensaje, profile_name_o_None).
    Si ok=True, profile_name tendrá el nombre del perfil.
    """
    profile_name = profile_name.strip()
    conn = get_connection()
    cur = conn.cursor()

    # Ahora buscamos por profile_name, NO por email
    cur.execute(
        "SELECT password_hash, profile_name FROM users WHERE profile_name = ?",
        (profile_name,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, "No existe una cuenta con ese usuario", None

    stored_hash, stored_profile = row
    if stored_hash == hash_password(password):
        return True, "Inicio de sesión exitoso", stored_profile
    else:
        return False, "Contraseña incorrecta", None
