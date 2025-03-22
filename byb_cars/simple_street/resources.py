"""Resources, constants, and asset management for Simple Street racing game."""

import pygame
import requests
from pathlib import Path

# Screen dimensions
WIDTH, HEIGHT = 800, 700  # Increased height for the signal plot
GAME_AREA_HEIGHT = HEIGHT - 100  # Space for the game, excluding plot area

# Colors
SKY_BLUE = (135, 206, 235)
ROAD_GRAY = (100, 100, 100)
GRASS_GREEN = (76, 153, 0)
LINE_WHITE = (255, 255, 255)
PLOT_BG = (240, 240, 240)
PLOT_GRID = (200, 200, 200)
PLOT_LINE = (0, 0, 255)  # Blue line for signal
THRESHOLD_LINE = (255, 0, 0)  # Red line for threshold
START_LINE_COLOR = (0, 255, 0)  # Green for start line
FINISH_LINE_COLOR = (255, 0, 0)  # Red for finish line

# Road dimensions
ROAD_WIDTH = WIDTH // 3
ROAD_LEFT = (WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT = ROAD_LEFT + ROAD_WIDTH

# Car settings
CAR_HEIGHT = 80
CAR_SCREEN_Y = HEIGHT - 200  # Fixed screen position for car

# Asset URLs
ASSETS = {
    "road": "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/road.png",
    "grass": "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/grass.png",
    "tree1": "https://opengameart.org/sites/default/files/Tree1.png",
    "tree2": "https://opengameart.org/sites/default/files/Tree2.png",
    "tree3": "https://opengameart.org/sites/default/files/Tree3.png",
    "car": "https://www.pngkit.com/png/full/16-165375_top-view-of-car-png-car-top-view.png",
}


def create_assets_dir():
    """Create assets directory if it doesn't exist."""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)
    return assets_dir


def download_assets():
    """Download all game assets or create placeholders if download fails."""
    assets_dir = create_assets_dir()
    
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
    
    return assets_dir


def load_car_image(assets_dir, car_height):
    """Load and scale car image."""
    try:
        car_img = pygame.image.load(assets_dir / "car.png").convert_alpha()
        
        # Scale car image
        car_aspect_ratio = car_img.get_width() / car_img.get_height()
        car_width = int(car_height * car_aspect_ratio)
        car_img = pygame.transform.scale(car_img, (car_width, car_height))
    except:
        # Create a simple car if loading fails
        car_width = 40
        car_img = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
        car_img.fill((255, 0, 0))  # Red car
    
    return car_img


def load_tree_images(assets_dir):
    """Load and scale tree images."""
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

    # Scale tree images
    scaled_tree_imgs = []
    for img in tree_imgs:
        height = 120
        width = int(img.get_width() * (height / img.get_height()))
        scaled_tree_imgs.append(pygame.transform.scale(img, (width, height)))
    
    return scaled_tree_imgs 