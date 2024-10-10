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

if background_music:
    background_music.play(-1)

# Game Constants
WIDTH, HEIGHT = 800, 600
ROTATION_SPEED = 0.1
MAX_FUEL = 300

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
        self.lander_image = pygame.transform.scale(pygame.image.load('lander.png'), (40, 40))
        self.width = self.lander_image.get_width()
        self.height = self.lander_image.get_height()
        self.gravity = gravity
        self.thrust = thrust
        self.thrusting = False
        self.flame_image = pygame.transform.scale(pygame.image.load('flame.png'), (20, 30))

    def apply_gravity(self):
        self.vy += self.gravity

    def apply_thrust(self):
        if self.fuel > 0:
            thrust_x = math.sin(self.angle) * self.thrust
            thrust_y = -math.cos(self.angle) * self.thrust
            self.vx += thrust_x
            self.vy += thrust_y
            self.fuel -= 1
            self.thrusting = True
        else:
            self.thrusting = False

    def rotate(self, direction):
        self.angle += direction * ROTATION_SPEED

    def update(self, keys):
        self.x += self.vx
        self.y += self.vy
        self.apply_gravity()
        if not keys[pygame.K_SPACE]:
            self.thrusting = False

    def draw(self, screen):
        if self.thrusting:
            flame_offset_x = -math.sin(self.angle) * (self.height // 2)
            flame_offset_y = math.cos(self.angle) * (self.height // 2)
            flame_x = self.x + flame_offset_x
            flame_y = self.y + flame_offset_y
            rotated_flame = pygame.transform.rotate(self.flame_image, -math.degrees(self.angle))
            flame_rect = rotated_flame.get_rect(center=(flame_x, flame_y))
            screen.blit(rotated_flame, flame_rect.topleft)

        rotated_image = pygame.transform.rotate(self.lander_image, -math.degrees(self.angle))
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

# Draw terrain and landing pad
def draw_terrain(screen, difficulty):
    if difficulty == 'easy':
        pygame.draw.rect(screen, GREEN, (0, 550, WIDTH, 50))
        pygame.draw.rect(screen, WHITE, (350, 550, 100, 10))
    elif difficulty == 'medium':
        pygame.draw.rect(screen, GREEN, (0, 550, WIDTH, 50))
        pygame.draw.lines(screen, WHITE, False, [(0, 550), (100, 530), (200, 550), (300, 520), (400, 550),
                                                 (500, 530), (600, 550), (700, 520), (WIDTH, 550)], 2)
        # Adding flat landing pads for medium level
        pygame.draw.rect(screen, WHITE, (150, 530, 80, 10))
        pygame.draw.rect(screen, WHITE, (500, 530, 80, 10))
    elif difficulty == 'hard':
        pygame.draw.rect(screen, GREEN, (0, 550, WIDTH, 50))
        pygame.draw.lines(screen, WHITE, False, [(0, 550), (50, 540), (150, 500), (250, 520), (350, 480),
                                                 (450, 500), (550, 460), (650, 500), (750, 520), (WIDTH, 550)], 2)
        # Adding flat landing pads
        pygame.draw.rect(screen, WHITE, (100, 500, 40, 10))
        pygame.draw.rect(screen, WHITE, (400, 480, 40, 10))
        pygame.draw.rect(screen, WHITE, (650, 500, 40, 10))

# Draw fuel gauge
def draw_fuel_gauge(screen, fuel):
    font = pygame.font.SysFont(None, 24)
    fuel_text = font.render(f'Fuel: {fuel}', True, WHITE)
    screen.blit(fuel_text, (10, 10))

# Draw animated background with ASCII art stars
def draw_animated_background(screen, frame):
    for (x, y), star_pattern in zip(star_positions, itertools.cycle(ascii_stars)):
        star_text = star_pattern[frame // 10 % len(star_pattern)]
        font = pygame.font.SysFont(None, 24)
        star_surface = font.render(star_text, True, BLUE)
        screen.blit(star_surface, (x, y))

# Check for collisions
def check_collision(lander, difficulty):
    terrain_points = []
    landing_pads = []
    if difficulty == 'easy':
        if 350 <= lander.x <= 450 and lander.y + lander.height // 2 >= 550:
            if safe_landing(lander):
                return 'landed'
            else:
                return 'crashed'
        elif lander.y + lander.height // 2 >= HEIGHT:
            return 'crashed'
    elif difficulty == 'medium':
        terrain_points = [(0, 550), (100, 530), (200, 550), (300, 520), (400, 550),
                          (500, 530), (600, 550), (700, 520), (WIDTH, 550)]
        landing_pads = [(150, 530, 80), (500, 530, 80)]
    elif difficulty == 'hard':
        terrain_points = [(0, 550), (50, 540), (150, 500), (250, 520), (350, 480),
                          (450, 500), (550, 460), (650, 500), (750, 520), (WIDTH, 550)]
        landing_pads = [(100, 500, 40), (400, 480, 40), (650, 500, 40)]

    if terrain_points:
        # Check collision with terrain lines
        for i in range(len(terrain_points) - 1):
            x1, y1 = terrain_points[i]
            x2, y2 = terrain_points[i + 1]
            if (x1 <= lander.x <= x2) or (x2 <= lander.x <= x1):
                if x2 != x1:
                    terrain_y = y1 + (y2 - y1) * ((lander.x - x1) / (x2 - x1))
                else:
                    terrain_y = (y1 + y2) / 2  # Handle vertical lines
                if lander.y + lander.height // 2 >= terrain_y:
                    return 'crashed'
        # Check for the ground beyond the terrain lines
        if lander.y + lander.height // 2 >= HEIGHT:
            return 'crashed'
        # Check landing pad collision
        if landing_pads:
            for pad_x, pad_y, pad_width in landing_pads:
                if pad_x <= lander.x <= pad_x + pad_width and lander.y + lander.height // 2 >= pad_y:
                    if safe_landing(lander):
                        return 'landed'
                    else:
                        return 'crashed'
    else:
        if lander.y + lander.height // 2 >= HEIGHT:
            return 'crashed'
    return None

# Determine if the landing is safe
def safe_landing(lander):
    return abs(lander.vx) < 0.5 and abs(lander.vy) < 1.0 and -0.3 < lander.angle < 0.3

# Title screen where player selects difficulty
def title_screen():
    font = pygame.font.SysFont(None, 48)
    instruction_font = pygame.font.SysFont(None, 32)
    running = True
    selected_difficulty = None
    while running:
        screen.fill(WHITE)
        title_text = font.render('Lunar Lander - Select Difficulty', True, BLACK)
        easy_text = font.render('1. Easy', True, BLACK)
        medium_text = font.render('2. Medium', True, BLACK)
        hard_text = font.render('3. Hard', True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(easy_text, (WIDTH // 2 - easy_text.get_width() // 2, 200))
        screen.blit(medium_text, (WIDTH // 2 - medium_text.get_width() // 2, 300))
        screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, 400))
        # Instructions
        instructions = [
            'Press 1, 2, or 3 to select a difficulty level:',
            '1. Easy - Gentle terrain with a single landing pad',
            '2. Medium - Moderate terrain with multiple landing pads',
            '3. Hard - Rugged terrain with challenging landing pads',
            '',
            'Use arrow keys (LEFT and RIGHT) to rotate the lander.',
            'Hold SPACE to apply thrust.',
            'Press Q to quit at any time.'
        ]
        for i, line in enumerate(instructions):
            instruction_text = instruction_font.render(line, True, BLACK)
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, 450 + i * 30))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'easy'
                elif event.key == pygame.K_2:
                    return 'medium'
                elif event.key == pygame.K_3:
                    return 'hard'
                elif event.key == pygame.K_q:
                    return 'quit'

def calculate_score(lander):
    return MAX_FUEL + lander.fuel


# End screen to show result and offer to play again or quit
def end_screen(message, score):
    font = pygame.font.SysFont(None, 48)
    running = True

    while running:
        screen.fill(WHITE)
        result_text = font.render(message, True, BLACK)
        score_text = font.render(f'Score: {score}', True, BLACK)
        play_again_text = font.render('Press Enter to play again or Q to quit', True, BLACK)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 150))
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200))
        screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, 250))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'play_again'
                elif event.key == pygame.K_q:
                    return 'quit'

# Main game loop
def game_loop(gravity, thrust, difficulty):
    lander = Lander(gravity, thrust)
    running = True
    game_result = None
    thrust_channel = None
    frame = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

        # Handle user input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            lander.rotate(1)
        if keys[pygame.K_RIGHT]:
            lander.rotate(-1)
        if keys[pygame.K_SPACE] and lander.fuel > 0:
            lander.apply_thrust()
            if thrust_channel is None or not thrust_channel.get_busy():
                thrust_channel = thrust_sound.play(-1)
        else:
            if thrust_channel is not None and thrust_channel.get_busy():
                thrust_channel.stop()

        # Update game state
        lander.update(keys)

        # Check for collisions
        collision_result = check_collision(lander, difficulty)
        if collision_result == 'landed':
            if landing_sound:
                landing_sound.play()
            game_result = 'landed'
            running = False
        elif collision_result == 'crashed':
            crash_sound.play()
            game_result = 'crashed'
            running = False

        if thrust_channel is not None and not running:
            thrust_channel.stop()

        # Redraw screen
        screen.fill(BLACK)
        draw_animated_background(screen, frame)
        draw_terrain(screen, difficulty)
        lander.draw(screen)
        draw_fuel_gauge(screen, lander.fuel)

        frame += 1
        pygame.display.flip()
        clock.tick(60)

    if game_result == 'landed':
        score = calculate_score(lander)
        return end_screen('Successful landing!', score)
    else:
        return end_screen('Crash!', 0)

def main():
    running = True
    while running:
        difficulty = title_screen()
        if difficulty == 'easy':
            gravity, thrust = 0.01, 0.15
        elif difficulty == 'medium':
            gravity, thrust = 0.03, 0.15
        elif difficulty == 'hard':
            gravity, thrust = 0.05, 0.15
        elif difficulty == 'quit':
            running = False
            break

        game_result = game_loop(gravity, thrust, difficulty)
        if game_result == 'quit':
            running = False

    pygame.quit()

if __name__ == '__main__':
    main()
