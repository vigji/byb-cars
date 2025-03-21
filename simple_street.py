import pygame
import sys
import random
import requests
from pathlib import Path
import numpy as np  # For some calculations

# Import the InputHandler
from byb_cars.input_handler import InputHandler

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Road with Car")

# Colors
SKY_BLUE = (135, 206, 235)
ROAD_GRAY = (100, 100, 100)
GRASS_GREEN = (76, 153, 0)
LINE_WHITE = (255, 255, 255)

# Create assets directory if it doesn't exist
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Asset URLs - better images
ASSETS = {
    "road": "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/road.png",
    "grass": "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/grass.png",
    "tree1": "https://opengameart.org/sites/default/files/Tree1.png",
    "tree2": "https://opengameart.org/sites/default/files/Tree2.png",
    "tree3": "https://opengameart.org/sites/default/files/Tree3.png",
    "car": "https://www.pngkit.com/png/full/16-165375_top-view-of-car-png-car-top-view.png",
}

def download_assets():
    for name, url in ASSETS.items():
        file_path = assets_dir / f"{name}.png"
        
        # Skip if file already exists
        if file_path.exists():
            continue
            
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded {name}.png")
        except Exception as e:
            print(f"Failed to download {name}.png: {e}")
            
            # Create a simple placeholder image
            placeholder = pygame.Surface((100, 100), pygame.SRCALPHA)
            placeholder.fill((0, 0, 0, 0))  # Transparent
            
            if "road" in name:
                placeholder.fill(ROAD_GRAY)  # Dark gray for road
            elif "grass" in name:
                placeholder.fill(GRASS_GREEN)  # Green for grass
            elif "tree" in name:
                # Create a simple tree
                pygame.draw.rect(placeholder, (101, 67, 33), (40, 50, 20, 50))  # Trunk
                pygame.draw.circle(placeholder, (0, 100, 0), (50, 40), 30)  # Leaves
            elif "car" in name:
                # Create a simple car shape
                pygame.draw.rect(placeholder, (255, 0, 0), (25, 25, 50, 75))  # Car body
                pygame.draw.rect(placeholder, (0, 0, 0), (30, 45, 15, 25))  # Window
                pygame.draw.circle(placeholder, (0, 0, 0), (30, 90), 10)  # Rear wheel
                pygame.draw.circle(placeholder, (0, 0, 0), (70, 90), 10)  # Front wheel
                
            pygame.image.save(placeholder, file_path)
            print(f"Created placeholder for {name}.png")

# Download assets
download_assets()

# Load assets
try:
    car_img = pygame.image.load(assets_dir / "car.png").convert_alpha()
except:
    # Create a simple car
    car_img = pygame.Surface((60, 100), pygame.SRCALPHA)
    car_img.fill((255, 0, 0))  # Red car

# Load tree images
tree_imgs = []
for i in range(1, 4):
    try:
        img = pygame.image.load(assets_dir / f"tree{i}.png").convert_alpha()
        tree_imgs.append(img)
    except:
        print(f"Could not load tree{i}.png")

# If no tree images were loaded, use a default
if not tree_imgs:
    default_tree = pygame.Surface((60, 100), pygame.SRCALPHA)
    default_tree.fill((0, 0, 0, 0))  # Transparent
    pygame.draw.rect(default_tree, (101, 67, 33), (25, 50, 10, 50))  # Trunk
    pygame.draw.circle(default_tree, (0, 100, 0), (30, 30), 25)  # Leaves
    tree_imgs.append(default_tree)

# Scale car image
car_height = 80
car_width = 40
try:
    car_aspect_ratio = car_img.get_width() / car_img.get_height()
    car_width = int(car_height * car_aspect_ratio)
    car_img = pygame.transform.scale(car_img, (car_width, car_height))
except:
    car_img = pygame.transform.scale(car_img, (car_width, car_height))

# Scale tree images
scaled_tree_imgs = []
for img in tree_imgs:
    height = 120
    width = int(img.get_width() * (height / img.get_height()))
    scaled_tree_imgs.append(pygame.transform.scale(img, (width, height)))
tree_imgs = scaled_tree_imgs

# Road dimensions
road_width = WIDTH // 3
road_left = (WIDTH - road_width) // 2
road_right = road_left + road_width

# Generate the road surface with markings
def create_road():
    # Create a large road surface to scroll
    tile_size = 100  # The size of each road tile
    num_tiles = 8    # How many tiles to create
    
    road_surface = pygame.Surface((road_width, tile_size * num_tiles))
    road_surface.fill(ROAD_GRAY)
    
    # Draw center line (dashed)
    dash_length = 40
    gap_length = 20
    line_width = 8
    center_x = road_width // 2
    
    y = 0
    while y < road_surface.get_height():
        pygame.draw.rect(road_surface, LINE_WHITE, 
                         (center_x - line_width//2, y, line_width, dash_length))
        y += dash_length + gap_length
    
    # Draw edge lines
    pygame.draw.rect(road_surface, LINE_WHITE, (5, 0, 3, road_surface.get_height()))
    pygame.draw.rect(road_surface, LINE_WHITE, (road_width - 8, 0, 3, road_surface.get_height()))
    
    return road_surface

# Create the road
road_surface = create_road()
road_height = road_surface.get_height()

# Generate trees with fixed world positions
class Tree:
    def __init__(self, img, x, y):
        self.img = img
        self.x = x
        self.y = y  # World Y position
    
    def draw(self, surface, camera_y):
        # Calculate screen position (relative to camera)
        screen_y = self.y - camera_y
        
        # Wrap around vertically if tree goes off-screen
        world_height = HEIGHT * 2
        while screen_y > HEIGHT:
            screen_y -= world_height
        while screen_y < -self.img.get_height():
            screen_y += world_height
        
        # Only draw if on screen
        if -self.img.get_height() < screen_y < HEIGHT:
            surface.blit(self.img, (self.x, screen_y))

# Create trees on both sides of the road
def generate_trees(num_trees):
    trees = []
    # Create a large enough world height
    world_height = HEIGHT * 2
    
    for _ in range(num_trees):
        # Choose which side of the road
        if random.random() < 0.5:
            # Left side
            x = random.randint(50, road_left - 50)
        else:
            # Right side
            x = random.randint(road_right + 10, WIDTH - 50)
        
        # Distribute trees evenly in world space
        y = random.randint(0, world_height)
        
        # Choose a random tree image
        img = random.choice(tree_imgs)
        
        trees.append(Tree(img, x, y))
    
    return trees

# Create a car with speed control via InputHandler
class Car:
    def __init__(self, img, x, y, input_handler):
        self.img = img
        self.x = x
        self.y = y        # World Y position
        self.screen_y = y # Fixed screen position
        self.input_handler = input_handler
        
        # Speed parameters
        self.min_speed = 0.5
        self.max_speed = 8.0
        self.speed = 3.0  # Default speed
        
        # Speed feedback visuals
        self.speed_bar_width = 100
        self.speed_bar_height = 10
    
    def update(self):
        # Get input value from InputHandler
        input_value = self.input_handler.get_value()
        
        # Map input value to speed (adjust ranges as needed)
        # When input is around 0, speed is minimum
        # When input is high (around 2.0+), speed is maximum
        if input_value <= 0:
            mapped_speed = self.min_speed
        else:
            # Map input_value (0 to ~3) to speed range
            mapped_speed = self.min_speed + (input_value / 3.0) * (self.max_speed - self.min_speed)
            mapped_speed = min(mapped_speed, self.max_speed)  # Cap at max speed
        
        # Set car speed
        self.speed = mapped_speed
        
        # Move car upward in world space
        self.y -= self.speed
        
        return self.speed
    
    def draw(self, surface):
        # Always draw at the fixed screen position
        surface.blit(self.img, (self.x - self.img.get_width()//2, self.screen_y))
        
        # Draw speed indicator
        self._draw_speed_indicator(surface)
    
    def _draw_speed_indicator(self, surface):
        # Draw a speed bar on the right side of the screen
        bar_x = WIDTH - self.speed_bar_width - 20
        bar_y = 20
        
        # Background bar (outline)
        pygame.draw.rect(surface, (50, 50, 50), 
                        (bar_x, bar_y, self.speed_bar_width, self.speed_bar_height), 2)
        
        # Calculate fill amount based on current speed
        fill_width = int((self.speed / self.max_speed) * self.speed_bar_width)
        
        # Fill bar (colored by speed)
        if self.speed < self.max_speed * 0.33:
            color = (0, 255, 0)  # Green for low speed
        elif self.speed < self.max_speed * 0.66:
            color = (255, 255, 0)  # Yellow for medium speed
        else:
            color = (255, 0, 0)  # Red for high speed
            
        pygame.draw.rect(surface, color, 
                        (bar_x, bar_y, fill_width, self.speed_bar_height))

# Generate trees
trees = generate_trees(30)

# Initialize InputHandler in demo mode
input_handler = InputHandler(demo_mode=True)

# Create the car - at a fixed screen position
car_screen_y = HEIGHT - 150
car = Car(car_img, WIDTH // 2, car_screen_y, input_handler)

# Main game variables
camera_y = 0  # Camera position in world coordinates
running = True
clock = pygame.time.Clock()

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_SPACE:
                # Set key_pressed to True when space is pressed
                input_handler.set_key_state(True)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # Set key_pressed to False when space is released
                input_handler.set_key_state(False)
    
    # Update car position and speed based on input
    current_speed = car.update()
    
    # Camera follows car
    camera_y = car.y - car_screen_y
    
    # Clear screen
    screen.fill(SKY_BLUE)
    
    # Draw grass (simple colored rectangles)
    pygame.draw.rect(screen, GRASS_GREEN, (0, 0, road_left, HEIGHT))
    pygame.draw.rect(screen, GRASS_GREEN, (road_right, 0, WIDTH - road_right, HEIGHT))
    
    # Draw road
    # Calculate the position of the road based on camera position
    road_y = camera_y % road_height
    
    # Draw multiple copies of the road to fill the screen
    for i in range(-1, 2):  # Draw one above, one on screen, one below
        screen.blit(road_surface, (road_left, i * road_height - road_y))
    
    # Draw trees
    for tree in trees:
        tree.draw(screen, camera_y)
    
    # Draw car
    car.draw(screen)
    
    # Show speed
    font = pygame.font.SysFont(None, 36)
    speed_text = f"Speed: {current_speed:.1f}"
    text_surface = font.render(speed_text, True, (0, 0, 0))
    screen.blit(text_surface, (20, 20))
    
    # Show input value
    input_value = input_handler.get_value()
    input_text = f"Input: {input_value:.2f}"
    input_surface = font.render(input_text, True, (0, 0, 0))
    screen.blit(input_surface, (20, 60))
    
    # Show controls
    controls_font = pygame.font.SysFont(None, 24)
    if input_handler.demo_mode:
        controls_text = "SPACE: Accelerate | Q: Quit"
    else:
        controls_text = "Use EMG Input | Q: Quit"
    controls_surface = controls_font.render(controls_text, True, (0, 0, 0))
    screen.blit(controls_surface, (20, 100))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
