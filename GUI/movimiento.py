import arcade
import random

# --- Constantes de la Ventana ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Practica de colisión y movimiento"

# --- Constantes del Jugador ---
PLAYER_SPEED = 5        
PLAYER_SIZE = 50 
PLAYER_COLOR = arcade.color.YELLOW

# --- Constantes del Target ---
TARGET_SIZE = 40        
TARGET_COLOR = arcade.color.PURPLE

# --- Constantes de Obstáculos ---
OBSTACLE_SIZE = 60
OBSTACLE_COLOR = arcade.color.RED
NUM_OBSTACLES = 5

class MyGame(arcade.Window):
    """
    Clase principal del juego. Hereda de arcade.Window.
    """

    def __init__(self, width, height, title):
        """
        Constructor. Se usa para inicializar variables.
        """
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.DEEP_SKY_BLUE)

        # --- Variables del Jugador ---
        self.player_sprite = None
        self.player_list = None
        
        # --- Variables del Target ---
        self.target_sprite = None
        self.target_list = None
        
        # --- Variables de Obstáculos ---
        self.obstacle_list = None
        
        # --- Variables de Movimiento ---
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False

    def setup(self):
        """
        Configura el juego.
        """
        # Inicializa la lista de sprites del jugador
        self.player_list = arcade.SpriteList()

        # Crea el sprite del jugador
        self.player_sprite = arcade.SpriteSolidColor(PLAYER_SIZE, PLAYER_SIZE, PLAYER_COLOR)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.player_list.append(self.player_sprite)

        # Inicializa la lista de obstáculos ANTES de crear el target
        self.obstacle_list = arcade.SpriteList()
        self.create_obstacles()

        # Inicializa la lista de sprites del target
        self.target_list = arcade.SpriteList()

        # Crea el sprite del target 
        self.target_sprite = arcade.SpriteSolidColor(TARGET_SIZE, TARGET_SIZE, TARGET_COLOR)
        self.move_target_randomly() 
        self.target_list.append(self.target_sprite)
        
    def create_obstacles(self):
        """
        Crea obstáculos aleatorios en la pantalla sin que se superpongan.
        """
        for _ in range(NUM_OBSTACLES):
            obstacle = arcade.SpriteSolidColor(OBSTACLE_SIZE, OBSTACLE_SIZE, OBSTACLE_COLOR)
            
            # Genera posiciones aleatorias sin sobreposición
            valid_position = False
            while not valid_position:
                obstacle.center_x = random.randrange(
                    OBSTACLE_SIZE // 2, SCREEN_WIDTH - OBSTACLE_SIZE // 2
                )
                obstacle.center_y = random.randrange(
                    OBSTACLE_SIZE // 2, SCREEN_HEIGHT - OBSTACLE_SIZE // 2
                )
                
                # Verifica que no esté muy cerca del jugador
                too_close_to_player = (abs(obstacle.center_x - SCREEN_WIDTH // 2) < 150 and 
                                       abs(obstacle.center_y - SCREEN_HEIGHT // 2) < 150)
                
                # Verifica que no se superponga con otros obstáculos
                overlaps_with_obstacle = False
                for existing_obstacle in self.obstacle_list:
                    distance = ((obstacle.center_x - existing_obstacle.center_x) ** 2 + 
                               (obstacle.center_y - existing_obstacle.center_y) ** 2) ** 0.5
                    if distance < OBSTACLE_SIZE + 20:  
                        overlaps_with_obstacle = True
                        break
                
                valid_position = not too_close_to_player and not overlaps_with_obstacle
            
            self.obstacle_list.append(obstacle)

    def move_target_randomly(self):
        """
        Mueve el sprite del target a una nueva posición aleatoria en la pantalla.
        """
        while True:
            self.target_sprite.center_x = random.randrange(
                TARGET_SIZE // 2, SCREEN_WIDTH - TARGET_SIZE // 2
            )
            self.target_sprite.center_y = random.randrange(
                TARGET_SIZE // 2, SCREEN_HEIGHT - TARGET_SIZE // 2
            )
            
            # Verifica que no esté sobre un obstáculo
            if not arcade.check_for_collision_with_list(self.target_sprite, self.obstacle_list):
                break

    def clamp_player_position(self):
        """
        Limita la posición del jugador para que no se salga de la pantalla.
        """
        if self.player_sprite.center_x < PLAYER_SIZE // 2:
            self.player_sprite.center_x = PLAYER_SIZE // 2
        elif self.player_sprite.center_x > SCREEN_WIDTH - PLAYER_SIZE // 2:
            self.player_sprite.center_x = SCREEN_WIDTH - PLAYER_SIZE // 2
        
        if self.player_sprite.center_y < PLAYER_SIZE // 2:
            self.player_sprite.center_y = PLAYER_SIZE // 2
        elif self.player_sprite.center_y > SCREEN_HEIGHT - PLAYER_SIZE // 2:
            self.player_sprite.center_y = SCREEN_HEIGHT - PLAYER_SIZE // 2

    def on_draw(self):
        """
        Función de dibujo. Renderiza todos los elementos en la pantalla.
        """
        self.clear()

        # Dibuja el jugador, el target y los obstáculos
        self.obstacle_list.draw()
        self.player_list.draw()
        self.target_list.draw()

    def on_key_press(self, key, modifiers):
        """
        Se llama cuando el usuario presiona una tecla.
        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.moving_up = True
            self.moving_down = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.moving_down = True
            self.moving_up = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.moving_left = True
            self.moving_right = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.moving_right = True
            self.moving_left = False

    def on_key_release(self, key, modifiers):
        """
        Se llama cuando el usuario suelta una tecla.
        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.moving_up = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.moving_down = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.moving_left = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.moving_right = False

    def on_update(self, delta_time):
        """
        Lógica del juego. Se llama en cada frame.
        """
        # Reinicia la velocidad
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        
        # Movimiento: solo en una dirección a la vez (prioridad vertical)
        if self.moving_up:
            self.player_sprite.change_y = PLAYER_SPEED
        elif self.moving_down:
            self.player_sprite.change_y = -PLAYER_SPEED
        elif self.moving_left:
            self.player_sprite.change_x = -PLAYER_SPEED
        elif self.moving_right:
            self.player_sprite.change_x = PLAYER_SPEED
        
        # Actualiza la posición del jugador
        self.player_list.update()
        
        # Limita la posición del jugador
        self.clamp_player_position()
        
        # Comprueba colisión with obstáculos y revierte movimiento si es necesario
        if arcade.check_for_collision_with_list(self.player_sprite, self.obstacle_list):
            # Revierte el movimiento
            self.player_sprite.center_x -= self.player_sprite.change_x
            self.player_sprite.center_y -= self.player_sprite.change_y

        # Comprueba si el jugador ha colisionado con el target
        hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.target_list
        )

        for target in hit_list:
            self.move_target_randomly()


def main():
    """
    Función principal para ejecutar el juego.
    """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()