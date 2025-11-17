import arcade
import arcade.gui
import random
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

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
load_dotenv()

# ================= CONFIGURACIÓN GENERAL =================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Login UGB - Juego Pokemon Campus"

# Paleta de colores temática (no Pokemon oficial, solo estilo gamer)
COLOR_BG_TOP = (10, 20, 40)
COLOR_BG_BOTTOM = (30, 40, 90)
COLOR_PANEL = (26, 32, 70)
COLOR_PANEL_BORDER = (140, 200, 255)
COLOR_ACCENT = (255, 220, 120)
COLOR_ACCENT_SOFT = (130, 220, 200)
COLOR_TEXT_SOFT = (210, 220, 245)

# ===== CONFIGURACIÓN DE CORREO (GMAIL) =====
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not SMTP_USER or not SMTP_PASSWORD:
    raise ValueError(
        "ERROR: SMTP_USER o SMTP_PASSWORD no están definidos.\n"
        "Crea un archivo .env en la carpeta del proyecto con:\n"
        "SMTP_SERVER=smtp.gmail.com\n"
        "SMTP_PORT=587\n"
        "SMTP_USER=pokeugb@gmail.com\n"
        "SMTP_PASSWORD=TU_APP_PASSWORD_DE_GMAIL\n"
    )


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


# ================= HELPERS DE DIBUJO =================

def draw_centered_rect_filled(cx, cy, width, height, color):
    """Atajo para dibujar rectángulos centrados usando draw_lrbt_rectangle_filled."""
    half_w = width / 2
    half_h = height / 2
    left = cx - half_w
    right = cx + half_w
    bottom = cy - half_h
    top = cy + half_h
    arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)


def draw_gradient_background():
    """Fondo con degradado vertical y cuadritos tipo 'pixel'."""
    steps = 16
    for i in range(steps):
        t = i / (steps - 1)
        r = int(COLOR_BG_TOP[0] + (COLOR_BG_BOTTOM[0] - COLOR_BG_TOP[0]) * t)
        g = int(COLOR_BG_TOP[1] + (COLOR_BG_BOTTOM[1] - COLOR_BG_TOP[1]) * t)
        b = int(COLOR_BG_TOP[2] + (COLOR_BG_BOTTOM[2] - COLOR_BG_TOP[2]) * t)
        y_bottom = (SCREEN_HEIGHT / steps) * i
        y_top = y_bottom + (SCREEN_HEIGHT / steps)

        # lrbt = left, right, bottom, top
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, y_bottom, y_top, (r, g, b)
        )

    # Cuadritos decorativos (HUD gamer)
    for x in range(0, SCREEN_WIDTH, 80):
        # Cuadro inferior
        draw_centered_rect_filled(
            x + 10, 40, 18, 18, COLOR_ACCENT_SOFT
        )
        # Cuadro superior
        draw_centered_rect_filled(
            x + 30, SCREEN_HEIGHT - 40, 12, 12, COLOR_ACCENT_SOFT
        )


def draw_pokeball_like(x, y, radius=40):
    """No es un pokeball oficial, solo un círculo temático gamer."""
    # Parte superior
    arcade.draw_arc_filled(
        x, y, radius * 2, radius * 2, (220, 60, 90), 0, 180
    )
    # Parte inferior
    arcade.draw_arc_filled(
        x, y, radius * 2, radius * 2, (245, 245, 245), 180, 360
    )
    # Línea central
    draw_centered_rect_filled(
        x, y, radius * 2, radius * 0.18, (15, 15, 25)
    )
    # Centro
    arcade.draw_circle_filled(x, y, radius * 0.38, (245, 245, 245))
    arcade.draw_circle_filled(x, y, radius * 0.2, (180, 210, 255))


def draw_panel_border(x_center, y_center, width, height, color, thickness=3):
    """Borde con cuatro rectángulos finos."""
    half_w = width / 2
    half_h = height / 2

    # Arriba
    draw_centered_rect_filled(
        x_center,
        y_center + half_h - thickness / 2,
        width,
        thickness,
        color,
    )
    # Abajo
    draw_centered_rect_filled(
        x_center,
        y_center - half_h + thickness / 2,
        width,
        thickness,
        color,
    )
    # Izquierda
    draw_centered_rect_filled(
        x_center - half_w + thickness / 2,
        y_center,
        thickness,
        height - 2 * thickness,
        color,
    )
    # Derecha
    draw_centered_rect_filled(
        x_center + half_w - thickness / 2,
        y_center,
        thickness,
        height - 2 * thickness,
        color,
    )


def draw_menu_panel(title: str, subtitle: str = ""):
    """Panel central reutilizable para login / registro / verificación."""
    panel_w = 550
    panel_h = 380
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2

    # Panel principal
    draw_centered_rect_filled(cx, cy, panel_w, panel_h, COLOR_PANEL)
    draw_panel_border(cx, cy, panel_w, panel_h, COLOR_PANEL_BORDER, thickness=3)

    # Franja superior (lrbt = left, right, bottom, top)
    header_h = 80
    left = cx - panel_w / 2
    right = cx + panel_w / 2
    bottom = cy + panel_h / 2 - header_h
    top = cy + panel_h / 2
    arcade.draw_lrbt_rectangle_filled(
        left, right, bottom, top, (30, 45, 95)
    )

    # "Pokeball" decorativa a la izquierda
    draw_pokeball_like(cx - panel_w / 2 + 70, cy + panel_h / 2 - 40, radius=28)

    # Título
    arcade.draw_text(
        title,
        cx - panel_w / 2 + 120,
        cy + panel_h / 2 - 40,
        arcade.color.WHITE,
        20,
        anchor_x="left",
        anchor_y="center",
        bold=True,
    )

    if subtitle:
        arcade.draw_text(
            subtitle,
            cx,
            cy + panel_h / 2 - 100,
            COLOR_TEXT_SOFT,
            12,
            anchor_x="center",
        )

    # Borde interior decorativo
    inner_w = panel_w - 24
    inner_h = panel_h - 24
    draw_panel_border(cx, cy, inner_w, inner_h, COLOR_ACCENT, thickness=2)


# ================= VISTAS =================

class LoginView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        center_y = SCREEN_HEIGHT // 2

        # ===== Inputs =====
        # Más separados del subtítulo
        self.email_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 35,   # antes: +55
            width=300,
            text=""
        )
        self.password_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y - 30,   # antes: -15
            width=300,
            text=""
        )

        # Labels
        email_label = arcade.gui.UILabel(
            text="Correo Gmail:",
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 70,   # antes: +85 (quedaba casi sobre el subtítulo)
        )
        password_label = arcade.gui.UILabel(
            text="Contraseña:",
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 5,    # antes: +15
        )

        # Botones (también un poco más abajo para mantener proporción)
        login_button = arcade.gui.UIFlatButton(
            text="⚡ Iniciar sesión",
            width=200,
            x=SCREEN_WIDTH // 2 - 100,
            y=center_y - 80,   # antes: -65
        )
        login_button.on_click = self.on_click_login

        register_link_button = arcade.gui.UIFlatButton(
            text="¿Nuevo entrenador? Regístrate",
            width=260,
            x=SCREEN_WIDTH // 2 - 130,
            y=center_y - 130,  # antes: -115
        )
        register_link_button.on_click = self.on_click_go_to_register

        # Mensaje de estado
        self.status_label = arcade.gui.UILabel(
            text="",
            x=SCREEN_WIDTH // 2 - 240,
            y=center_y - 180,   # antes: -165
            width=480,
            multiline=True,
        )

        # Agregar al UIManager
        self.ui_manager.add(email_label)
        self.ui_manager.add(self.email_input)
        self.ui_manager.add(password_label)
        self.ui_manager.add(self.password_input)
        self.ui_manager.add(login_button)
        self.ui_manager.add(register_link_button)
        self.ui_manager.add(self.status_label)


    def on_click_login(self, event):
        email = self.email_input.text.strip()
        password = self.password_input.text

        ok, msg, profile_name = login_user(email, password)
        self.status_label.text = msg

        if ok:
            self.window.current_user_email = email
            self.window.current_profile_name = profile_name
            game_view = GameView()
            self.window.show_view(game_view)

    def on_click_go_to_register(self, event):
        register_view = RegisterView()
        self.window.show_view(register_view)

    def on_draw(self):
        self.clear()
        draw_gradient_background()
        draw_menu_panel(
            "Login Campus UGB",
            "Ingresa tus credenciales para comenzar la aventura",
        )
        arcade.draw_text(
            "Tip: Usa tu correo Gmail real para recibir el código.",
            SCREEN_WIDTH // 2,
            50,
            COLOR_TEXT_SOFT,
            11,
            anchor_x="center",
        )
        self.ui_manager.draw()


class RegisterView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        center_y = SCREEN_HEIGHT // 2

        # Estado para pasar a verificación
        self.pending_email = None
        self.pending_password = None
        self.pending_profile = None

        # ===== Inputs con más espacio =====
        self.email_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 35,
            width=300,
            text=""
        )
        self.password_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y - 30,
            width=300,
            text=""
        )
        self.profile_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y - 85,
            width=300,
            text=""
        )

        # Labels
        email_label = arcade.gui.UILabel(
            text="Correo Gmail:",
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 70,
        )
        password_label = arcade.gui.UILabel(
            text="Contraseña (Aa1! mínimo 8 caracteres):",
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 5,
            width=350,
            multiline=True,
        )
        profile_label = arcade.gui.UILabel(
            text="Nombre de perfil (único):",
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y - 55,
        )

        # Botones
        send_code_button = arcade.gui.UIFlatButton(
            text="📩 Enviar código de verificación",
            width=270,
            x=SCREEN_WIDTH // 2 - 135,
            y=center_y - 135,
        )
        send_code_button.on_click = self.on_click_send_code

        back_button = arcade.gui.UIFlatButton(
            text="⬅ Volver",
            width=110,
            x=SCREEN_WIDTH // 2 - 55,
            y=center_y - 175,
        )
        back_button.on_click = self.on_click_back

        # Mensaje de estado (al borde inferior del panel, sin tocar botones)
        self.status_label = arcade.gui.UILabel(
            text="",
            x=SCREEN_WIDTH // 2 - 240,
            y=center_y - 190,
            width=480,
            multiline=True,
        )

        # Agregar al UIManager
        self.ui_manager.add(email_label)
        self.ui_manager.add(self.email_input)
        self.ui_manager.add(password_label)
        self.ui_manager.add(self.password_input)
        self.ui_manager.add(profile_label)
        self.ui_manager.add(self.profile_input)
        self.ui_manager.add(send_code_button)
        self.ui_manager.add(back_button)
        self.ui_manager.add(self.status_label)

    def on_click_send_code(self, event):
        email = self.email_input.text.strip()
        password = self.password_input.text
        profile_name = self.profile_input.text.strip()

        # Validaciones
        if not is_valid_email(email):
            self.status_label.text = "Correo inválido: solo @gmail.com"
            return
        if not is_valid_profile_name(profile_name):
            self.status_label.text = "El nombre de perfil debe tener al menos 3 caracteres"
            return
        ok_pass, msg_pass = validate_password(password)
        if not ok_pass:
            self.status_label.text = msg_pass
            return
        if email_exists(email):
            self.status_label.text = "Ya existe una cuenta con ese correo"
            return
        if profile_name_exists(profile_name):
            self.status_label.text = "Ese nombre de perfil ya está en uso"
            return

        # Generar y enviar código
        code = f"{random.randint(0, 9999):04d}"
        try:
            send_verification_code(email, code)
            self.pending_email = email
            self.pending_password = password
            self.pending_profile = profile_name
            verify_view = VerifyCodeView(code, email, password, profile_name)
            self.window.show_view(verify_view)
        except Exception as e:
            print("Error enviando correo:", e)
            self.status_label.text = "No se pudo enviar el código. Revisa la configuración del correo."

    def on_click_back(self, event):
        login_view = LoginView()
        self.window.show_view(login_view)

    def on_draw(self):
        self.clear()
        draw_gradient_background()
        draw_menu_panel(
            "Registro de Entrenador UGB",
            "Crea tu cuenta y valida tu correo para entrar al campus",
        )
        arcade.draw_text(
            "Consejo: Usa un nombre de perfil único para que tus amigos te encuentren.",
            SCREEN_WIDTH // 2,
            50,
            COLOR_TEXT_SOFT,
            11,
            anchor_x="center",
        )
        self.ui_manager.draw()


class VerifyCodeView(arcade.View):
    def __init__(self, verification_code, email, password, profile):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        center_y = SCREEN_HEIGHT // 2

        self.verification_code = verification_code
        self.pending_email = email
        self.pending_password = password
        self.pending_profile = profile

        # Input para código (más centrado y con espacio)
        self.code_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 45,
            width=300,
            text=""
        )

        # Labels
        code_label = arcade.gui.UILabel(
            text="Código de verificación (revisa tu correo):",
            x=SCREEN_WIDTH // 2 - 150,
            y=center_y + 80,
            width=350,
            multiline=True,
        )

        # Botones
        verify_button = arcade.gui.UIFlatButton(
            text="✅ Verificar y registrar",
            width=220,
            x=SCREEN_WIDTH // 2 - 110,
            y=center_y - 5,
        )
        verify_button.on_click = self.on_click_verify

        back_button = arcade.gui.UIFlatButton(
            text="⬅ Volver",
            width=110,
            x=SCREEN_WIDTH // 2 - 55,
            y=center_y - 55,
        )
        back_button.on_click = self.on_click_back

        # Mensaje de estado, bien separadito de los botones
        self.status_label = arcade.gui.UILabel(
            text="",
            x=SCREEN_WIDTH // 2 - 240,
            y=center_y - 115,
            width=480,
            multiline=True,
        )

        # Agregar al UIManager
        self.ui_manager.add(code_label)
        self.ui_manager.add(self.code_input)
        self.ui_manager.add(verify_button)
        self.ui_manager.add(back_button)
        self.ui_manager.add(self.status_label)

    def on_click_verify(self, event):
        user_code = self.code_input.text.strip()
        if user_code != self.verification_code:
            self.status_label.text = "Código incorrecto. Intenta de nuevo."
            return

        # Registrar usuario
        ok, msg = register_user(self.pending_email, self.pending_password, self.pending_profile)
        self.status_label.text = msg
        if ok:
            self.window.current_user_email = self.pending_email
            self.window.current_profile_name = self.pending_profile
            game_view = GameView()
            self.window.show_view(game_view)

    def on_click_back(self, event):
        register_view = RegisterView()
        self.window.show_view(register_view)

    def on_draw(self):
        self.clear()
        draw_gradient_background()
        draw_menu_panel(
            "Verificar código",
            "Ingresa el código que fue enviado a tu correo",
        )
        arcade.draw_text(
            "Si no ves el correo, revisa la bandeja de spam.",
            SCREEN_WIDTH // 2,
            50,
            COLOR_TEXT_SOFT,
            11,
            anchor_x="center",
        )
        self.ui_manager.draw()


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        center_y = SCREEN_HEIGHT // 2

        # Botón "Comenzar" (queda centrado respecto al panel)
        start_button = arcade.gui.UIFlatButton(
            text="🐦‍🔥 Comenzar aventura",
            width=230,
            x=SCREEN_WIDTH // 2 - 115,
            y=center_y - 10,
        )
        start_button.on_click = self.on_click_start

        # Botón "Cerrar sesión"
        logout_button = arcade.gui.UIFlatButton(
            text="🚪 Cerrar sesión",
            width=200,
            x=SCREEN_WIDTH // 2 - 100,
            y=center_y - 70,
        )
        logout_button.on_click = self.on_click_logout

        self.ui_manager.add(start_button)
        self.ui_manager.add(logout_button)

    def on_show_view(self):
        arcade.set_background_color(COLOR_BG_BOTTOM)

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
        draw_gradient_background()

        panel_w = 560
        panel_h = 320
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 + 20

        draw_centered_rect_filled(cx, cy, panel_w, panel_h, COLOR_PANEL)
        draw_panel_border(cx, cy, panel_w, panel_h, COLOR_PANEL_BORDER, thickness=3)

        profile = getattr(self.window, "current_profile_name", "Entrenador")

        # Título del juego
        arcade.draw_text(
            "UGB CAMPUS QUEST",
            cx,
            cy + panel_h / 2 - 50,
            arcade.color.WHITE,
            28,
            anchor_x="center",
            bold=True,
        )

        arcade.draw_text(
            f"Bienvenido/a, {profile}",
            cx,
            cy + 70,
            COLOR_ACCENT,
            20,
            anchor_x="center",
        )


        # Barra decorativa
        draw_centered_rect_filled(
            cx, cy - 95, 260, 10, (35, 160, 120)
        )

        self.ui_manager.draw()


class FirstGameView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_show_view(self):
        arcade.set_background_color((20, 60, 30))

    def on_draw(self):
        self.clear()

        # Fondo tipo césped sencillo
        for y in range(0, SCREEN_HEIGHT, 40):
            for x in range(0, SCREEN_WIDTH, 40):
                if (x // 40 + y // 40) % 2 == 0:
                    color = (34, 139, 34)
                else:
                    color = (24, 119, 34)

                # lrbt = left, right, bottom, top
                arcade.draw_lrbt_rectangle_filled(
                    x, x + 40, y, y + 40, color
                )

        arcade.draw_text(
            "Primer mapa del juego (placeholder)",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 80,
            arcade.color.WHITE,
            22,
            anchor_x="center",
        )
        arcade.draw_text(
            "Aquí podrás cargar el mapa del campus, NPCs, rutas, etc.",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 120,
            (220, 240, 220),
            14,
            anchor_x="center",
        )

        arcade.draw_text(
            "Presiona ESC para volver a la pantalla de bienvenida.",
            SCREEN_WIDTH // 2,
            60,
            (220, 240, 220),
            14,
            anchor_x="center",
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
