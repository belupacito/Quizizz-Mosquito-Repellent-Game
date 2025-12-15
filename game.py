import pygame as pg
import os
import math
import random as rd

# Initialize Pygame
os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()

# Set up display
score = 0
game_over_flag = False
screen_width = 700
screen_height = 700
screen = pg.display.set_mode((screen_width, screen_height), flags=pg.RESIZABLE)
pg.display.set_caption("Quizizz Mosquito Repellent Game")

# Settings
font = pg.font.SysFont('Consolas', 20)
file_dir = os.path.dirname(os.path.abspath(__file__))

# Load images
saberhilt_image = os.path.join(file_dir, 'saber.png')
saberhilt_image = pg.image.load(saberhilt_image).convert_alpha()
rays_image = os.path.join(file_dir, 'rays.png')
rays_image = pg.image.load(rays_image).convert_alpha()
background_image = os.path.join(file_dir, 'background.jpg')
background_image = pg.image.load(background_image).convert()
obstacle_image = os.path.join(file_dir, 'obstacle.png')
obstacle_image = pg.image.load(obstacle_image).convert_alpha()

# Scale images
new_width = saberhilt_image.get_width() // 2
new_height = saberhilt_image.get_height() // 2
scaled_image = pg.transform.scale(saberhilt_image, (new_width, new_height))
rays_image = pg.transform.scale(rays_image, (screen_width//30, screen_height//30))
background_image = pg.transform.scale(background_image, (screen_width, screen_height))

# Position images
scaled_image_rect = scaled_image.get_rect()
scaled_image_rect.center = (screen_width // 2, screen_height // 2)

# Ray class
class Ray:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 1.75
        self.distance_traveled = 0
        self.max_distance = 500  # Maximum distance before disappearing
        self.image = rays_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Move the ray in the direction it's pointing
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        self.distance_traveled += self.speed
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        # Rotate the ray image to match the direction
        rotated_image = pg.transform.rotate(self.image, -math.degrees(self.direction + math.pi/2))
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        surface.blit(rotated_image, rotated_rect)

    def is_expired(self):
        # Check if the ray has traveled too far
        return self.distance_traveled > self.max_distance

# Function to move the object towards the target
def move_towards_target(x, y, target_x, target_y, speed):
    dx = target_x - x
    dy = target_y - y
    distance = math.sqrt(dx**2 + dy**2)

    if distance > 0:
        dx /= distance
        dy /= distance
        x += dx * speed
        y += dy * speed

    return x, y

# Function to generate a random position at least 225 pixels from center
def get_good_position(min_distance=225): # Away from Center, and also made the obstacles not overlap with each other
    center_x = screen_width // 2
    center_y = screen_height // 2

    while True:
        x = rd.randint(0, screen_width)
        y = rd.randint(0, screen_height)

        # Calculate distance from center
        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # If distance is at least min_distance, return the position
        if distance >= min_distance:
            return x, y

# Obstacle class (obstacles now move toward the center)
class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.3  # Movement speed toward center
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        # Move toward the center of the screen
        center_x = screen_width // 2
        center_y = screen_height // 2
        self.x, self.y = move_towards_target(self.x, self.y, center_x, center_y, self.speed)
        self.rect.center = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_expired(self):
        # Check if the obstacle has reached the center (or is very close)
        center_x = screen_width // 2
        center_y = screen_height // 2
        distance_to_center = math.sqrt((self.x - center_x)**2 + (self.y - center_y)**2)
        return distance_to_center < 10  # Expire when very close to center

def game_over():
    global game_over_flag
    game_over_flag = True
    text = font.render(f'Game Over! Press R to Restart. Score: {score}', True, (255, 0, 0))
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
    screen.blit(text, text_rect)
    restart_text = font.render('Press R to Restart', True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(restart_text, restart_rect)

def draw_score(score):
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

def reset_game():
    global score, game_over_flag, rays, obstacles
    score = 0
    game_over_flag = False
    rays = []
    obstacles = []

def gameloop():
    global mouse_x, mouse_y, direction, scaled_image_rect, rotated_image, rotated_image_rect, score, game_over_flag
    running = True
    rays = []  # List to store active rays
    obstacles = []
    clock = pg.time.Clock()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and not game_over_flag:
                    ray = Ray(scaled_image_rect.centerx, scaled_image_rect.centery, direction)
                    rays.append(ray)
                elif event.key == pg.K_r:  # Reset game with 'R' key
                    reset_game()
                    obstacles.clear()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over_flag:  # Left mouse button
                    # Create a new ray in the direction of the saber
                    ray = Ray(scaled_image_rect.centerx, scaled_image_rect.centery, direction)
                    rays.append(ray)
                elif event.button == 1 and game_over_flag:  # Restart on click when game over
                    reset_game()
                    obstacles.clear()

        if not game_over_flag:
            # Spawn obstacles randomly outside the event loop
            if rd.randint(1, 300) == 1:  # 2% chance per frame
                # Get a position at least 150 pixels away from center
                x, y = get_good_position(150)
                obstacle = Obstacle(x, y)
                obstacles.append(obstacle)

            # Update aiming/rotation every frame
            mouse_x, mouse_y = pg.mouse.get_pos()
            direction = math.atan2(mouse_y - scaled_image_rect.centery, mouse_x - scaled_image_rect.centerx)
            rotated_image = pg.transform.rotate(scaled_image, -math.degrees(direction))
            rotated_image_rect = rotated_image.get_rect(center=scaled_image_rect.center)

            # Update rays
            for ray in rays[:]:  # Iterate over a copy of the list
                ray.update()
                if ray.is_expired():
                    rays.remove(ray)

            # Update obstacles
            for obstacle in obstacles[:]:  # Iterate over a copy of the list
                obstacle.update()
                if obstacle.is_expired():
                    obstacles.remove(obstacle)

            # Check collision between rays and obstacles
            for ray in rays[:]:
                for obstacle in obstacles[:]:
                    if ray.rect.colliderect(obstacle.rect):
                        if ray in rays:
                            rays.remove(ray)
                        if obstacle in obstacles:
                            obstacles.remove(obstacle)
                        score += 1  # Increase score when hitting obstacle
                        break  # Break to avoid checking the same ray against other obstacles

            # Check collision with saber
            for obstacle in obstacles:
                if obstacle.rect.colliderect(rotated_image_rect):
                    game_over()

            # Draw everything
            screen.blit(background_image, (0, 0))  # Draw the background

            # Draw rays
            for ray in rays:
                ray.draw(screen)
            # Draw obstacles
            for obstacle in obstacles:
                obstacle.draw(screen)

            # Draw the hilt
            screen.blit(rotated_image, rotated_image_rect)

            # Draw score
            draw_score(score)
        else:
            # Game over screen
            screen.blit(background_image, (0, 0))
            game_over()
            draw_score(score)

        pg.display.update()
        clock.tick(600)  # Limit to 600 FPS

gameloop()
pg.quit()

