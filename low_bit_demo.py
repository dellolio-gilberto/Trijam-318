import pygame
import random
import sys

# Init
pygame.init()
WIDTH, HEIGHT = 960, 720  # Mappa più grande
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 24)

# Colors\
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Player
player = pygame.Rect(WIDTH//2, HEIGHT//2, 20, 20)
player_speed = 4
spawn_area = player.copy()

# Obstacles
obstacles = [pygame.Rect(random.randint(0, WIDTH-40), random.randint(0, HEIGHT-40), 40, 40) for _ in range(5)]
corrupted_obstacles = []

# Corruption tiles
corrupted_tiles = []

# Resources
def place_resource():
    while True:
        new_res = pygame.Rect(random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20), 15, 15)
        if not new_res.colliderect(spawn_area):
            return new_res

resource = place_resource()
resource_timer = 0

# Glitch (float for finer control)
glitch_level = 0.0
max_glitch = 100.0

# Counters and delays
corruption_counter = 0
corruption_base_delay = 30  # base, will scale down
glitch_inc_counter = 0
glitch_inc_delay = 50  # aumenta glitch level più velocemente
difficulty_threshold = 0  # per aumentare ostacoli

# Audio
pygame.mixer.init()
try:
    pygame.mixer.music.load("arcade_music.ogg")
    pygame.mixer.music.play(-1)
except:
    pass

# Functions

def draw_glitch():
    # Visivo: distorsioni 8-bit
    if glitch_level > 20:
        for _ in range(int(glitch_level)):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            color = random.choice(COLORS)
            pygame.draw.rect(screen, color, (x, y, 5, 5))
    # Audio: abbassa volume
    if glitch_level > 40:
        pygame.mixer.music.set_volume(max(0, 1.0 - glitch_level / max_glitch))


def corrupt_world():
    # Lethal corruption tiles
    if random.random() < (glitch_level/ max_glitch):
        for _ in range(5):
            x = random.randint(0, WIDTH-10)
            y = random.randint(0, HEIGHT-10)
            tile = pygame.Rect(x, y, 10, 10)
            if not tile.colliderect(spawn_area):
                corrupted_tiles.append(tile)
                break


def increase_difficulty():
    global difficulty_threshold
    # ad ogni 20 punti di glitch aggiunge un ostacolo normale
    level_int = int(glitch_level // 20)
    if level_int > difficulty_threshold:
        obstacles.append(pygame.Rect(random.randint(0, WIDTH-40), random.randint(0, HEIGHT-40), 40, 40))
        difficulty_threshold = level_int

# Game loop
score = 0
running = True
frame_rate = 60

while running:
    clock.tick(frame_rate)
    screen.fill(BLACK)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: player.x -= player_speed
    if keys[pygame.K_RIGHT]: player.x += player_speed
    if keys[pygame.K_UP]: player.y -= player_speed
    if keys[pygame.K_DOWN]: player.y += player_speed

    # Keep in bounds
    player.x = max(0, min(WIDTH-player.width, player.x))
    player.y = max(0, min(HEIGHT-player.height, player.y))

    # Collisions
    for obs in obstacles:
        if player.colliderect(obs):
            score = max(0, score - 10)
            player.x, player.y = WIDTH//2, HEIGHT//2

    for obs in corrupted_obstacles + corrupted_tiles:
        if player.colliderect(obs):
            running = False

    # Collect resource: only way to slow glitch
    if player.colliderect(resource):
        glitch_level = max(0.0, glitch_level - 20.0)
        score += 50
        resource = place_resource()
        resource_timer = 0

    # Draw background glitch pattern
    for x in range(0, WIDTH, 20):
        for y in range(0, HEIGHT, 20):
            if random.random() < 0.008 * (glitch_level / max_glitch):
                pygame.draw.rect(screen, random.choice(COLORS), (x, y, 20, 20))

    # Draw obstacles
    for obs in obstacles:
        color = (150,150,150) if glitch_level < 50 else random.choice(COLORS)
        pygame.draw.rect(screen, color, obs)
    for obs in corrupted_obstacles:
        pygame.draw.rect(screen, (255,50,50), obs)

    # Draw player
    if glitch_level < 60 or random.random() > (glitch_level / max_glitch):
        color = WHITE if glitch_level < 30 else random.choice(COLORS)
        pygame.draw.rect(screen, color, player)

    # Draw corruption tiles
    for tile in corrupted_tiles:
        pygame.draw.rect(screen, random.choice(COLORS), tile)

    # Draw resource
    pygame.draw.rect(screen, (0, 255, 0), resource)

    # Update glitch level fast and only increase over time
    glitch_inc_counter += 1
    if glitch_inc_counter > glitch_inc_delay:
        glitch_level = min(max_glitch, glitch_level + 5.0)
        glitch_inc_counter = 0

    # Corruption spawn faster as glitch increases
    corruption_counter += 1
    current_delay = max(5, int(corruption_base_delay - (glitch_level/ max_glitch)*20))
    if corruption_counter > current_delay:
        corrupt_world()
        corruption_counter = 0

    # Increase difficulty dynamically
    increase_difficulty()

    # Timers
    resource_timer +=1
    if resource_timer > 400:
        resource = place_resource()
        resource_timer = 0

    # HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    glitch_text = font.render(f"Corruption: {int(glitch_level)}%", True, WHITE)
    screen.blit(glitch_text, (10, 40))

    # Visual glitch overlay
    draw_glitch()

    pygame.display.flip()

pygame.quit()
sys.exit()

