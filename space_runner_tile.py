import pygame
import random
import sys
from pytmx.util_pygame import load_pygame

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Runner with Tiled Background")

# Load Tiled map
try:
    tmx_data = load_pygame("mymap.tmx")
except Exception as e:
    print("Error loading map:", e)
    sys.exit()

# Load and play background music
pygame.mixer.music.load("space.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Load bullet firing sound
shot_sound = pygame.mixer.Sound("shot.wav")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Falling stars background (will draw over tiled background)
stars = []
for _ in range(50):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    radius = random.randint(1, 3)
    speed = random.randint(1, 3)
    stars.append([x, y, radius, speed])

# Load assets
player_img = pygame.image.load("rocket.png")
player_img = pygame.transform.scale(player_img, (50, 50))

bullet_img = pygame.image.load("bullet.png")
bullet_img = pygame.transform.scale(bullet_img, (15, 30))

enemy_img = pygame.image.load("enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (50, 50))

# Clock and font
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 72)

# Game variables
player_rect = player_img.get_rect(center=(WIDTH // 2, HEIGHT - 60))
player_speed = 5
bullets = []
bullet_speed = 7
enemies = []
enemy_speed = 3
enemy_spawn_delay = 30
enemy_timer = 0
score = 0
level = 1
bullet_cooldown = 0
bullet_cooldown_delay = 10
game_over = False

# Function to reset the game
def reset_game():
    global player_rect, bullets, enemies, score, enemy_timer, bullet_cooldown, game_over, level, enemy_speed
    player_rect.center = (WIDTH // 2, HEIGHT - 60)
    bullets.clear()
    enemies.clear()
    score = 0
    level = 1
    enemy_speed = 2
    enemy_timer = 0
    bullet_cooldown = 0
    game_over = False

# Function to show Game Over screen
def show_game_over():
    screen.fill(BLACK)
    text = large_font.render("GAME OVER", True, (255, 0, 0))
    instruction = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Pre-render and scale the entire tiled map to a surface for performance
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight
map_surface = pygame.Surface((map_width, map_height))

for layer in tmx_data.visible_layers:
    if hasattr(layer, 'tiles'):
        for x, y, image in layer.tiles():
            if image:
                map_surface.blit(image, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# Scale the map surface to fit the screen size once, outside game loop
scaled_map = pygame.transform.scale(map_surface, (WIDTH, HEIGHT))

# Game loop
running = True
while running:
    screen.fill(BLACK)

    if game_over:
        show_game_over()
        continue

    # Draw scaled Tiled map background
    screen.blit(scaled_map, (0, 0))

    # Falling stars (drawn above background)
    for star in stars:
        x, y, r, speed = star
        pygame.draw.circle(screen, WHITE, (x, y), r)
        star[1] += speed
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed

    # Shooting bullets
    if keys[pygame.K_SPACE]:
        if bullet_cooldown == 0 and len(bullets) < 10:
            bullet_rect = bullet_img.get_rect(midbottom=player_rect.midtop)
            bullets.append(bullet_rect)
            shot_sound.play()
            bullet_cooldown = bullet_cooldown_delay

    if bullet_cooldown > 0:
        bullet_cooldown -= 1

    # Update bullets
    for bullet in bullets[:]:
        bullet.y -= bullet_speed
        if bullet.bottom < 0:
            bullets.remove(bullet)

    # Spawn enemies
    enemy_timer += 1
    if enemy_timer >= enemy_spawn_delay:
        enemy_timer = 0
        x_pos = random.randint(0, WIDTH - 50)
        enemy_rect = enemy_img.get_rect(topleft=(x_pos, 0))
        enemies.append(enemy_rect)

    # Update enemies
    for enemy in enemies[:]:
        enemy.y += enemy_speed

        if enemy.colliderect(player_rect):
            game_over = True
        elif enemy.top > HEIGHT:
            game_over = True

    # Collision detection
    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 20
                break

    # Leveling
    new_level = score // 500 + 1
    if new_level > level:
        level = new_level
        enemy_speed += 1

    # Draw everything
    screen.blit(player_img, player_rect)
    for bullet in bullets:
        screen.blit(bullet_img, bullet)
    for enemy in enemies:
        screen.blit(enemy_img, enemy)

    # Draw score and level
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
