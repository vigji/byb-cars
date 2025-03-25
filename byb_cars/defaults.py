import pygame
from pathlib import Path
import requests

WIDTH, HEIGHT = 1000, 900  # Increased height for the signal plot


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