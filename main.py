import arcade
import arcade.gui

from auth_db import init_db, register_user, login_user

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Login UGB - Juego Campus"

class LoginView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Input correo
        self.email_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 70,
            width=300,
            text="",
        )
        # Input contraseña
        self.password_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 20,
            width=300,
            text="",
        )
        # Input nombre de perfil (solo para registro)
        self.profile_input = arcade.gui.UIInputText(
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 - 30,
            width=300,
            text="",
        )

        # Labels
        email_label = arcade.gui.UILabel(
            text="Correo institucional:",
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 105,
        )
        password_label = arcade.gui.UILabel(
            text="Contraseña:",
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 55,
        )
        profile_label = arcade.gui.UILabel(
            text="Nombre de perfil (único):",
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 + 5,
        )

        # Botones
        login_button = arcade.gui.UIFlatButton(
            text="Iniciar sesión",
            width=140,
            x=SCREEN_WIDTH // 2 - 150,
            y=SCREEN_HEIGHT // 2 - 90,
        )
        register_button = arcade.gui.UIFlatButton(
            text="Registrarse",
            width=140,
            x=SCREEN_WIDTH // 2 + 10,
            y=SCREEN_HEIGHT // 2 - 90,
        )

        login_button.on_click = self.on_click_login
        register_button.on_click = self.on_click_register

        # Mensaje de estado
        self.status_label = arcade.gui.UILabel(
            text="",
            x=SCREEN_WIDTH // 2 - 200,
            y=SCREEN_HEIGHT // 2 - 150,
            width=400,
        )

        # Agregar al UIManager
        self.ui_manager.add(email_label)
        self.ui_manager.add(self.email_input)
        self.ui_manager.add(password_label)
        self.ui_manager.add(self.password_input)
        self.ui_manager.add(profile_label)
        self.ui_manager.add(self.profile_input)
        self.ui_manager.add(login_button)
        self.ui_manager.add(register_button)
        self.ui_manager.add(self.status_label)

    def on_click_login(self, event):
        email = self.email_input.text
        password = self.password_input.text

        ok, msg, profile_name = login_user(email, password)
        self.status_label.text = msg

        if ok:
            # Guardar usuario actual y nombre de perfil en la ventana
            self.window.current_user_email = email
            self.window.current_profile_name = profile_name
            game_view = GameView()
            self.window.show_view(game_view)

    def on_click_register(self, event):
        email = self.email_input.text
        password = self.password_input.text
        profile_name = self.profile_input.text

        ok, msg = register_user(email, password, profile_name)
        self.status_label.text = msg

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Bienvenido al juego del Campus UGB",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            font_size=22,
            anchor_x="center"
        )
        arcade.draw_text(
            "Inicia sesión o regístrate con tu correo institucional",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 140,
            arcade.color.LIGHT_GRAY,
            font_size=14,
            anchor_x="center"
        )
        self.ui_manager.draw()

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Estilos de botones
        button_style = {
            "normal": arcade.gui.UISkinDefault().get_texture("flat_button_normal"),
            "hover": arcade.gui.UISkinDefault().get_texture("flat_button_hover"),
            "press": arcade.gui.UISkinDefault().get_texture("flat_button_press"),
        }

        # Botón "Comenzar"
        start_button = arcade.gui.UIFlatButton(
            text="🚀 Comenzar",
            width=230,
            x=SCREEN_WIDTH // 2 - 115,
            y=SCREEN_HEIGHT // 2 - 40,
            style=button_style
        )
        start_button.on_click = self.on_click_start

        # Botón "Cerrar sesión"
        logout_button = arcade.gui.UIFlatButton(
            text="Cerrar sesión",
            width=200,
            x=SCREEN_WIDTH // 2 - 100,
            y=SCREEN_HEIGHT // 2 - 100,
            style=button_style
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
            (199, 199, 209),   # #C7C7D1
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
            # Volver a la pantalla de bienvenida
            welcome_view = GameView()
            self.window.show_view(welcome_view)


def main():
    init_db()  # crea la tabla con profile_name si no existe

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.current_user_email = None
    window.current_profile_name = None
    login_view = LoginView()
    window.show_view(login_view)
    arcade.run()

if __name__ == "__main__":
    main()
