import pygame
import math
import itertools

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Sounds
thrust_sound = pygame.mixer.Sound('thrust.wav')
crash_sound = pygame.mixer.Sound('crash.wav')
try:
    landing_sound = pygame.mixer.Sound('landing.mp3')
except FileNotFoundError:
    landing_sound = None
try:
    background_music = pygame.mixer.Sound('background_music.mp3')
except FileNotFoundError:
    background_music = None

if background_music: background_music.play(-1)

# Game Constants
WIDTH, HEIGHT = 800, 600
ROTATION_SPEED = 0.1
MAX_FUEL = 100

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Lunar Lander')
clock = pygame.time.Clock()

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# ASCII Art Stars for Animated Background
ascii_stars = [
    "     .    ",
    "   .      ",
    "      .   ",
    "   .    . ",
    "       .  ",
]
star_positions = list(itertools.product(range(0, WIDTH, 100), range(0, HEIGHT, 100)))

# Lander class
class Lander:
    def __init__(self, gravity, thrust):
        import random
        self.x = random.randint(50, WIDTH - 50)  # Random x position within screen bounds (leaving margin)
        self.y = random.randint(50, HEIGHT // 2)  # Random y position above a certain threshold (upper half of screen)
        self.angle = random.uniform(-math.pi / 2, math.pi / 2)  # Random angle between -45 and 45 degrees
        
        self.vx = 0
        self.vy = 0
        
        self.fuel = MAX_FUEL
        self.alive = True
        self.lander_image = pygame.transform.scale(pygame.image.load('lander.png'), (40, 40))  # Load the lander image
        self.width = self.lander_image.get_width()
        self.height = self.lander_image.get_height()
        self.gravity = gravity
        self.thrust = thrust
        self.thrusting = False  # Flag for thrust animation
        self.flame_image = pygame.transform.scale(pygame.image.load('flame.png'), (20, 30))  # Load thrust flame image

    def apply_gravity(self):
        self.vy += self.gravity

    def apply_thrust(self):
        if self.fuel > 0:
            thrust_x = -math.sin(self.angle) * self.thrust  # Correct direction for horizontal thrust
            thrust_y = math.cos(self.angle) * self.thrust  # Correct direction for vertical thrust
            self.vx += thrust_x
            self.vy += thrust_y
            self.fuel -= 1  # Reduce fuel with each thrust
            self.thrusting = True  # Set thrust flag to True
        else:
            self.thrusting = False

    def rotate(self, direction):
        self.angle += direction * ROTATION_SPEED

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.apply_gravity()
        if not keys[pygame.K_SPACE]:
            self.thrusting = False

    def draw(self, screen):
        # Draw thrust flame if thrusting
        if self.thrusting:
            flame_offset_x = -math.sin(self.angle) * (self.height // 2)
            flame_offset_y = math.cos(self.angle) * (self.height // 2)
            flame_x = self.x + flame_offset_x
            flame_y = self.y + flame_offset_y
            rotated_flame = pygame.transform.rotate(self.flame_image, -math.degrees(self.angle))
            flame_rect = rotated_flame.get_rect(center=(flame_x, flame_y))
            screen.blit(rotated_flame, flame_rect.topleft)

        # Draw the lander with rotation
        rotated_image = pygame.transform.rotate(self.lander_image, -math.degrees(self.angle))
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)
        if self.thrusting:
            flame_offset_x = -math.sin(self.angle) * (self.height // 2)
            flame_offset_y = math.cos(self.angle) * (self.height // 2)
            flame_x = self.x + flame_offset_x
            flame_y = self.y + flame_offset_y
            rotated_flame = pygame.transform.rotate(self.flame_image, -math.degrees(self.angle))
            flame_rect = rotated_flame.get_rect(center=(flame_x, flame_y))
            screen.blit(rotated_flame, flame_rect.topleft)

# Draw terrain and landing pad
def draw_terrain(screen):
    pygame.draw.rect(screen, GREEN, (0, 550, WIDTH, 50))  # Ground
    pygame.draw.rect(screen, WHITE, (350, 550, 100, 10))  # Landing pad

# Draw fuel gauge
def draw_fuel_gauge(screen, fuel):
    font = pygame.font.SysFont(None, 24)
    fuel_text = font.render(f'Fuel: {fuel}', True, BLACK)
    screen.blit(fuel_text, (10, 10))

# Draw animated background with ASCII art stars
def draw_animated_background(screen, frame):
    for (x, y), star_pattern in zip(star_positions, itertools.cycle(ascii_stars)):
        star_text = star_pattern[frame // 10 % len(star_pattern)]
        font = pygame.font.SysFont(None, 24)
        star_surface = font.render(star_text, True, BLUE)
        screen.blit(star_surface, (x, y))

# Check for collisions
def check_collision(lander):
    if lander.y + lander.height // 2 > 550:  # Hit the ground
        return True
    return False

# Determine if the landing is safe
def safe_landing(lander):
    return abs(lander.vx) < 0.5 and abs(lander.vy) < 1.0 and -0.1 < lander.angle < 0.1

# Title screen where player selects difficulty
def title_screen():
    font = pygame.font.SysFont(None, 48)
    running = True
    selected_difficulty = None

    while running:
        screen.fill(BLACK)
        title_text = font.render('Lunar Lander - Select Difficulty', True, WHITE)
        easy_text = font.render('1. Easy', True, WHITE)
        medium_text = font.render('2. Medium', True, WHITE)
        hard_text = font.render('3. Hard', True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, 200))
        screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, 300))
        screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, 400))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_difficulty = 'easy'
                elif event.key == pygame.K_2:
                    selected_difficulty = 'medium'
                elif event.key == pygame.K_3:
                    selected_difficulty = 'hard'

        if selected_difficulty:
            return selected_difficulty

# End screen to show result and offer to play again or quit
def end_screen(message):
    font = pygame.font.SysFont(None, 48)
    running = True

    while running:
        screen.fill(WHITE)
        result_text = font.render(message, True, BLACK)
        play_again_text = font.render('Press Enter to play again or Q to quit', True, BLACK)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 200))
        screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'play_again'
                elif event.key == pygame.K_q:
                    return 'quit'

# Main game loop
def game_loop(gravity, thrust):
    lander = Lander(gravity, thrust)
    running = True
    game_result = None
    frame = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle user input
        global keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            lander.rotate(1)
        if keys[pygame.K_RIGHT]:
            lander.rotate(-1)
        if keys[pygame.K_SPACE]:
            if lander.fuel > 0:
                lander.apply_thrust()
                if not pygame.mixer.Sound.get_num_channels(thrust_sound):
                    pygame.mixer.Sound.play(thrust_sound)  # Play sound if not already playing
        else:
            if pygame.mixer.Sound.get_num_channels(thrust_sound):
                pygame.mixer.Sound.stop(thrust_sound)

        # Update lander position
        lander.update()

        # Check for collisions
        if check_collision(lander):
            if safe_landing(lander):
                game_result = "You landed safely!"
                if landing_sound: landing_sound.play()
            else:
                game_result = "You crashed!"
                pygame.mixer.Sound.play(crash_sound)

            pygame.display.flip() 
            pygame.time.wait(2000)    
            running = False

        # Redraw screen
        screen.fill(BLACK)
        draw_animated_background(screen, frame)
        draw_terrain(screen)
        draw_terrain(screen)
        lander.draw(screen)
        draw_fuel_gauge(screen, lander.fuel)
        pygame.display.flip()

        frame += 1
        clock.tick(60)

    return game_result

# Start the game with the title screen, game loop, and end screen
def main():
    while True:
        # Title screen to select difficulty
        difficulty = title_screen()

        if difficulty == 'easy':
            gravity, thrust = 0.03, -0.2
        elif difficulty == 'medium':
            gravity, thrust = 0.05, -0.15
        else:  # Hard difficulty
            gravity, thrust = 0.07, -0.1

        # Run the game loop based on selected difficulty
        result = game_loop(gravity, thrust)

        # End screen to show result and replay or quit option
        end_choice = end_screen(result)
        if end_choice == 'quit':
            break

# Run the main game loop
main()

# Quit Pygame
pygame.quit()
pygame.mixer.music.stop()
