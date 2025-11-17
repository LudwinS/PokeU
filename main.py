import arcade
import arcade.gui
import random
import smtplib
from email.message import EmailMessage
import os  # Agregado para variables de entorno
from dotenv import load_dotenv  # Agregado para cargar .env

from auth_db import (
    init_db,
    register_user,
    login_user,
    is_valid_email,
    is_valid_profile_name,
    validate_password,
    email_exists,
    profile_name_exists,
)

# ================= CARGAR .env =================
load_dotenv()  # Carga las variables del archivo .env

# ================= CONFIGURACIÓN GENERAL =================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Login UGB - Juego Pokemon Campus"

# ===== CONFIGURACIÓN DE CORREO (GMAIL) =====
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Agregado: faltaba esta línea

if not SMTP_USER or not SMTP_PASSWORD:
    raise ValueError(
        "ERROR: SMTP_USER o SMTP_PASSWORD no están definidos.\n"
        "Crea un archivo .env en la carpeta del proyecto con:\n"
        "SMTP_SERVER=smtp.gmail.com\n"
        "SMTP_PORT=587\n"
        "SMTP_USER=pokeugb@gmail.com\n"
        "SMTP_PASSWORD=TU_APP_PASSWORD_DE_GMAIL\n"
    )
# ==========================================

def send_verification_code(to_email: str, code: str):
    """
    Envía un correo con el código de verificación.
    """
    msg = EmailMessage()
    msg["Subject"] = "Código de verificación - Juego Campus UGB"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.set_content(
        f"Hola!\n\n"
        f"Tu código de verificación para crear la cuenta es: {code}\n\n"
        "Si no solicitaste esto, puedes ignorar este mensaje."
    )

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

# ================= VISTAS =================

class LoginView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Estado para verificación por código
        self.verification_code = None
        self.code_sent = False
        self.pending_email = None
        self.pending_password = None
        self.pending_profile = None

        # ---------- Inputs ----------
        self.email_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 90,
            width=300,
            text="",
        )
        self.password_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 40,
            width=300,
            text="",
        )
        self.profile_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 - 10,
            width=300,
            text="",
        )
        self.code_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 - 60,
            width=300,
            text="",
        )

        # ---------- Labels ----------
        email_label = arcade.gui.UILabel(
            text="Correo Gmail:",  # Cambiado: actualizado para reflejar Gmail
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 125,
        )
        password_label = arcade.gui.UILabel(
            text="Contraseña (Aa1! mínimo 8 caracteres):",
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 75,
        )
        profile_label = arcade.gui.UILabel(
            text="Nombre de perfil (único):",
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 25,
        )
        code_label = arcade.gui.UILabel(
            text="Código de verificación (revisar tu correo):",
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 - 25,
        )

        # ---------- Botones ----------
        send_code_button = arcade.gui.UIFlatButton(
            text="Enviar código",
            width=140,
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 - 110,
        )
        send_code_button.on_click = self.on_click_send_code

        register_button = arcade.gui.UIFlatButton(
            text="Verificar y registrar",
            width=180,
            x=SCREEN_WIDTH // 2 + 10,
            y=SCREEN_HEIGHT // 2 - 110,
        )
        register_button.on_click = self.on_click_register

        login_button = arcade.gui.UIFlatButton(
            text="Iniciar sesión",
            width=200,
            x=SCREEN_WIDTH // 2 - 100,
            y=SCREEN_HEIGHT // 2 - 170,
        )
        login_button.on_click = self.on_click_login

        # ---------- Mensaje de estado ----------
        self.status_label = arcade.gui.UILabel(
            text="",
            x=SCREEN_WIDTH // 2 - 250,
            y=SCREEN_HEIGHT // 2 - 220,
            width=500,
        )

        # ---------- Agregar al UIManager ----------
        self.ui_manager.add(email_label)
        self.ui_manager.add(self.email_input)
        self.ui_manager.add(password_label)
        self.ui_manager.add(self.password_input)
        self.ui_manager.add(profile_label)
        self.ui_manager.add(self.profile_input)
        self.ui_manager.add(code_label)
        self.ui_manager.add(self.code_input)
        self.ui_manager.add(send_code_button)
        self.ui_manager.add(register_button)
        self.ui_manager.add(login_button)
        self.ui_manager.add(self.status_label)

    # ---------- Registro con código ----------

    def on_click_send_code(self, event):
        email = self.email_input.text.strip()
        password = self.password_input.text
        profile_name = self.profile_input.text.strip()

        # Validar email
        if not is_valid_email(email):
            self.status_label.text = "Correo inválido: solo @gmail.com"  # Cambiado: actualizado para Gmail
            return

        # Validar perfil
        if not is_valid_profile_name(profile_name):
            self.status_label.text = "El nombre de perfil debe tener al menos 3 caracteres"
            return

        # Validar contraseña (mayúscula, minúscula, número, símbolo, longitud)
        ok_pass, msg_pass = validate_password(password)
        if not ok_pass:
            self.status_label.text = msg_pass
            return

        # Revisar si ya existen en la BD
        if email_exists(email):
            self.status_label.text = "Ya existe una cuenta con ese correo"
            return

        if profile_name_exists(profile_name):
            self.status_label.text = "Ese nombre de perfil ya está en uso"
            return

        # Generar código de 4 dígitos
        code = f"{random.randint(0, 9999):04d}"

        try:
            send_verification_code(email, code)
            self.verification_code = code
            self.code_sent = True
            self.pending_email = email
            self.pending_password = password
            self.pending_profile = profile_name
            self.status_label.text = "Código enviado. Revisa tu correo e ingrésalo abajo."
        except Exception as e:
            print("Error enviando correo:", e)
            self.status_label.text = "No se pudo enviar el código. Revisa la configuración del correo."

    def on_click_register(self, event):
        if not self.code_sent or not self.verification_code:
            self.status_label.text = "Primero haz clic en 'Enviar código'."
            return

        user_code = self.code_input.text.strip()

        if user_code != self.verification_code:
            self.status_label.text = "Código incorrecto. Intenta de nuevo."
            return

        # Código correcto → registrar en BD
        ok, msg = register_user(self.pending_email, self.pending_password, self.pending_profile)
        self.status_label.text = msg

        if ok:
            # Guardar datos antes de limpiar
            email = self.pending_email
            profile = self.pending_profile

            # Limpiar estado de verificación
            self.verification_code = None
            self.code_sent = False
            self.pending_email = None
            self.pending_password = None
            self.pending_profile = None
            self.code_input.text = ""

            # Iniciar sesión automáticamente
            self.window.current_user_email = email
            self.window.current_profile_name = profile

            game_view = GameView()
            self.window.show_view(game_view)

    # ---------- Login normal ----------

    def on_click_login(self, event):
        email = self.email_input.text
        password = self.password_input.text

        ok, msg, profile_name = login_user(email, password)
        self.status_label.text = msg

        if ok:
            self.window.current_user_email = email
            self.window.current_profile_name = profile_name
            game_view = GameView()
            self.window.show_view(game_view)

    def on_draw(self):
        self.clear()
        arcade.set_background_color((24, 26, 47))

        arcade.draw_text(
            "Juego Campus UGB",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            "Inicia sesión o regístrate con verificación por correo",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 110,
            (200, 200, 220),
            14,
            anchor_x="center"
        )

        self.ui_manager.draw()


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Botón "Comenzar" (sin estilo personalizado)
        start_button = arcade.gui.UIFlatButton(
            text="🐦‍🔥 Comenzar",
            width=230,
            x=SCREEN_WIDTH // 2 - 115,
            y=SCREEN_HEIGHT // 2 - 40,
        )
        start_button.on_click = self.on_click_start

        # Botón "Cerrar sesión" (sin estilo personalizado)
        logout_button = arcade.gui.UIFlatButton(
            text="ಥ_ಥ Cerrar sesión",
            width=200,
            x=SCREEN_WIDTH // 2 - 100,
            y=SCREEN_HEIGHT // 2 - 100,
        )
        logout_button.on_click = self.on_click_logout

        self.ui_manager.add(start_button)
        self.ui_manager.add(logout_button)

    def on_show_view(self):
        arcade.set_background_color((30, 31, 54))  # #1E1F36

    def on_click_start(self, event):
        first_game_view = FirstGameView()
        self.window.show_view(first_game_view)

    def on_click_logout(self, event):
        self.window.current_user_email = None
        self.window.current_profile_name = None
        login_view = LoginView()
        self.window.show_view(login_view)

    def on_draw(self):
        self.clear()

        profile = getattr(self.window, "current_profile_name", "Jugador")

        # Texto principal con sombra para que resalte
        arcade.draw_text(
            f"Bienvenido, {profile}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 150,
            arcade.color.WHITE,
            34,
            anchor_x="center",
            bold=True
        )
        arcade.draw_text(
            f"Bienvenido, {profile}",
            SCREEN_WIDTH // 2 + 2,
            SCREEN_HEIGHT - 152,
            (50, 50, 50),
            34,
            anchor_x="center",
            bold=True
        )

        # Texto secundario
        arcade.draw_text(
            "Pantalla de Inicio - Juego UGB",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 190,
            (199, 199, 209),
            16,
            anchor_x="center"
        )

        arcade.draw_text(
            "Haz clic en “Comenzar” para entrar al juego.",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 220,
            (199, 199, 209),
            14,
            anchor_x="center"
        )

        # Dibujar UI (botones)
        self.ui_manager.draw()

class FirstGameView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Aquí irá el primer mapa / pantalla del juego",
            100,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            18,
        )
        arcade.draw_text(
            "Presiona ESC para volver a la bienvenida",
            100,
            SCREEN_HEIGHT // 2 - 40,
            arcade.color.WHITE,
            14,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            welcome_view = GameView()
            self.window.show_view(welcome_view)


# ================= FUNCIÓN PRINCIPAL =================

def main():
    init_db()  # crea la tabla de usuarios si no existe

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.current_user_email = None
    window.current_profile_name = None
    login_view = LoginView()
    window.show_view(login_view)
    arcade.run()


if __name__ == "__main__":
    main()