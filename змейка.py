import pygame
import random
import time
import sqlite3

# Initialize Pygame
pygame.init()

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (5, 210, 80)
RED = (200, 0, 20)
BLUE = (80, 10, 250)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
GRAY = (169, 169, 169)

# Set dimensions
WIDTH = 600
HEIGHT = 600
BLOCK_SIZE = 20

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Initialize clock for controlling the frame rate
clock = pygame.time.Clock()

# Fonts for displaying score and level
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Database setup
conn = sqlite3.connect("snake_game.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    username TEXT PRIMARY KEY
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_score (
    username TEXT,
    level INTEGER,
    score INTEGER,
    length INTEGER,
    snake_list TEXT,
    food_x INTEGER,
    food_y INTEGER,
    FOREIGN KEY (username) REFERENCES user(username)
)
""")
conn.commit()

def get_user(username):
    """Retrieve or create user and score."""
    cursor.execute("SELECT * FROM user WHERE username=?", (username,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user (username) VALUES (?)", (username,))
        cursor.execute("INSERT INTO user_score (username, level, score, length, snake_list, food_x, food_y) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (username, 1, 0, 1, "[]", -1, -1))
        conn.commit()
        return 1, 0
    cursor.execute("SELECT level, score FROM user_score WHERE username=?", (username,))
    return cursor.fetchone()

def save_game(username, level, score, length, snake_list, food):
    """Save the current game state."""
    cursor.execute("""
        UPDATE user_score
        SET level=?, score=?, length=?, snake_list=?, food_x=?, food_y=?
        WHERE username=?
    """, (level, score, length, str(snake_list), food[0], food[1], username))
    conn.commit()

def load_game(username):
    """Load the saved game state."""
    cursor.execute("""
        SELECT level, score, length, snake_list, food_x, food_y
        FROM user_score
        WHERE username=?
    """, (username,))
    result = cursor.fetchone()
    if result:
        level, score, length, snake_list, food_x, food_y = result
        snake_list = eval(snake_list)
        food = [food_x, food_y, random.choice([10, 30, 50]), RED, 5] if food_x != -1 else None
        return level, score, length, snake_list, food
    return 1, 0, 1, [], None

def display_score(score, level):
    """Displays the current score and level on the screen."""
    value = score_font.render("Score: " + str(score), True, WHITE)
    level_text = score_font.render("Level: " + str(level), True, WHITE)
    screen.blit(value, [0, 0])
    screen.blit(level_text, [WIDTH - 120, 0])

def draw_snake(snake_block, snake_list):
    """Draws the snake on the screen."""
    for x in snake_list:
        pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])

def generate_food(snake_list, walls):
    """Generates food with random weights and colors that do not overlap with the snake or walls."""
    while True:
        food_x = random.randrange(1, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        food_y = random.randrange(1, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        weight = random.choice([10, 30, 50])  # Food weights: 10, 30, 50
        color = RED if weight == 10 else ORANGE if weight == 30 else PINK
        timer = 5 if weight == 10 else 10 if weight == 30 else 15
        if [food_x, food_y] not in snake_list and [food_x, food_y] not in walls:
            return [food_x, food_y, weight, color, timer]

def generate_wall(snake_list, walls):
    """Generates a wall with random length and orientation."""
    while True:
        wall_x = random.randrange(1, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        wall_y = random.randrange(1, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        length = random.randint(3, 6)  # Wall length between 3 and 6 blocks
        orientation = random.choice(["horizontal", "vertical"])
        wall = [[wall_x + BLOCK_SIZE * i, wall_y] if orientation == "horizontal" else [wall_x, wall_y + BLOCK_SIZE * i]
                for i in range(length)]
        if all(w not in snake_list and w not in walls for w in wall):
            return wall

def draw_walls(walls):
    """Draw the walls on the screen."""
    for wall in walls:
        for segment in wall:
            pygame.draw.rect(screen, GRAY, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])

def message(msg, color):
    """Displays a message on the screen."""
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])

def gameLoop():
    """Main game loop."""
    username = input("Enter your username: ")
    level, score = get_user(username)
    level, score, length_of_snake, snake_list, food = load_game(username)

    x1 = WIDTH // 2
    y1 = HEIGHT // 2
    x1_change = 0
    y1_change = 0
    game_over = False
    game_close = False
    food_timer = time.time() if food else None
    walls = []  # List to store wall segments
    wall_timer = time.time()

    while not game_over:
        while game_close:
            screen.fill(BLUE)
            message("Game Over! Press Q-Quit or C-Play Again", RED)
            display_score(score, level)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        save_game(username, level, score, length_of_snake, snake_list, food)
                        game_over = True
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(username, level, score, length_of_snake, snake_list, food)
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x1_change == 0:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change == 0:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change == 0:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change == 0:
                    y1_change = BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_p:
                    save_game(username, level, score, length_of_snake, snake_list, food)
                    message("Game Paused! Press any key to continue.", WHITE)
                    pygame.display.update()
                    pygame.event.clear()
                    pygame.event.wait()

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0 or any(x1 == segment[0] and y1 == segment[1] for wall in walls for segment in wall):
            game_close = True

        x1 += x1_change
        y1 += y1_change
        screen.fill(BLUE)

        if not food or time.time() - food_timer > food[4]:
            food = generate_food(snake_list, walls)
            food_timer = time.time()
        pygame.draw.rect(screen, food[3], [food[0], food[1], BLOCK_SIZE, BLOCK_SIZE])

        if time.time() - wall_timer > 10:  # Spawn walls every 10 seconds
            walls.append(generate_wall(snake_list, walls))
            wall_timer = time.time()

        draw_walls(walls)

        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)
        display_score(score, level)
        pygame.display.update()

        if x1 == food[0] and y1 == food[1]:
            length_of_snake += food[2] // 10
            score += food[2]
            food = None

            if score >= level * 50:
                level += 1

        clock.tick(10 + level)

    pygame.quit()
    quit()

gameLoop()
