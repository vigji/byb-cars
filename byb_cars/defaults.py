import pygame
from pathlib import Path
import requests

WIDTH, HEIGHT = 800, 700  # Increased height for the signal plot


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

# Create assets directory if it doesn't exist
assets_dir = Path(__file__).parent / "assets"
assets_dir.mkdir(exist_ok=True)

# Asset URLs - better images
ASSETS = {
    "road": "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/road.png",
    "grass": "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/grass.png",
    "tree1": "https://opengameart.org/sites/default/files/Tree1.png",
    "tree2": "https://opengameart.org/sites/default/files/Tree2.png",
    "tree3": "https://opengameart.org/sites/default/files/Tree3.png",
    "car": "https://www.clipartmax.com/png/middle/6-66856_race-car-clipart-car-clipart-top-view.png",
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
