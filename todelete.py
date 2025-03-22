import pygame
import sys
import random
import requests
from pathlib import Path
import numpy as np
import time
import argparse  # Added for command line arguments

# Import the InputHandler
from byb_cars.input_handler import InputHandler

# Parse command line arguments
parser = argparse.ArgumentParser(description="Scrolling Road with EMG Control")
parser.add_argument("--demo", action="store_true", 
                    help="Run in demo mode with keyboard control instead of EMG")
parser.add_argument("--port", type=str, default=None,
                    help="Serial port for Arduino (e.g., COM3 on Windows, /dev/ttyACM0 on Linux)")
args = parser.parse_args()

# Determine if we're running in demo mode
demo_mode = True if args.demo else (args.port is None)

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 700  # Increased height for the signal plot
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Scrolling Road with Car")

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

# Signal Plot class (similar to PyQtGraph implementation in main.py)
class SignalPlot:
    def __init__(self, width, height, buffer_size=200):
        self.width = width
        self.height = height
        self.buffer_size = buffer_size
        self.signal_buffer = np.zeros(buffer_size)
        self.surface = pygame.Surface((width, height))
        
        # Plot boundaries
        self.plot_margin = 10
        self.plot_width = width - 2 * self.plot_margin
        self.plot_height = height - 2 * self.plot_margin
        
        # Y-axis scaling
        self.y_min = 0
        self.y_max = 3.0  # Maximum expected signal value
        
    def update(self, new_value):
        # Roll buffer and add new value
        self.signal_buffer = np.roll(self.signal_buffer, -1)
        self.signal_buffer[-1] = new_value
        
        # Dynamically adjust y-axis if needed
        if new_value > self.y_max:
            self.y_max = new_value * 1.2  # Give some headroom
        
    def draw(self, surface, x, y):
        # Clear plot area
        self.surface.fill(PLOT_BG)
        
        # Draw border
        pygame.draw.rect(self.surface, (0, 0, 0), 
                        (self.plot_margin, self.plot_margin, 
                         self.plot_width, self.plot_height), 1)
        
        # Draw grid lines
        for i in range(1, 4):  # Draw 3 horizontal grid lines
            y_pos = self.plot_margin + i * self.plot_height // 4
            pygame.draw.line(self.surface, PLOT_GRID, 
                            (self.plot_margin, y_pos), 
                            (self.plot_margin + self.plot_width, y_pos), 1)
            
            # Add y-axis labels
            font = pygame.font.SysFont(None, 20)
            value = self.y_max * (4 - i) / 4
            label = font.render(f"{value:.1f}", True, (0, 0, 0))
            self.surface.blit(label, (5, y_pos - 10))
            
        # Draw threshold line at 1.0 (typical threshold for significant signal)
        threshold_y = self.plot_margin + self.plot_height - (1.0 / self.y_max * self.plot_height)
        pygame.draw.line(self.surface, THRESHOLD_LINE, 
                        (self.plot_margin, threshold_y), 
                        (self.plot_margin + self.plot_width, threshold_y), 1)
            
        # Draw signal line
        points = []
        for i in range(self.buffer_size):
            x_pos = self.plot_margin + i * self.plot_width / (self.buffer_size - 1)
            # Scale value to plot height (flipped, as pygame y increases downward)
            y_pos = self.plot_margin + self.plot_height - (self.signal_buffer[i] / self.y_max * self.plot_height)
            y_pos = min(self.plot_margin + self.plot_height, max(self.plot_margin, y_pos))  # Clamp to plot area
            points.append((x_pos, y_pos))
            
        # Draw signal line
        if len(points) > 1:
            pygame.draw.lines(self.surface, PLOT_LINE, False, points, 2)
        
        # Add title and labels
        font = pygame.font.SysFont(None, 24)
        title = font.render("EMG Signal", True, (0, 0, 0))
        self.surface.blit(title, (self.width // 2 - title.get_width() // 2, 5))
        
        # Current value
        if len(self.signal_buffer) > 0:
            current_value = self.signal_buffer[-1]
            value_text = font.render(f"Current: {current_value:.2f}", True, (0, 0, 0))
            self.surface.blit(value_text, (self.width - 150, 5))
        
        # Blit the plot surface onto the main surface
        surface.blit(self.surface, (x, y))

# World manages all game world elements including road, trees, and race lines
class GameWorld:
    def __init__(self, baseline_speed=3.0, game_height=600):
        self.baseline_speed = baseline_speed
        self.game_height = game_height
        
        # Track distance calculation - increased for more stable experience
        self.target_time = 10.0  # 10 seconds to finish at baseline speed
        fps = 60
        self.track_distance = int(self.baseline_speed * fps * self.target_time)
        
        # Create the road texture
        self.road_surface = self.create_road()
        self.road_height = self.road_surface.get_height()
        
        # Start and finish line positions - positive = distance from start
        self.start_line_position = 500
        self.finish_line_position = self.start_line_position + self.track_distance
        
        # Create trees
        self.trees = self.generate_trees(120)  # More trees for longer track
        
        # Race state
        self.race_started = False
        self.race_finished = False
        self.start_time = None
        self.finish_time = None
        self.current_time = 0
        self.best_time = None
        self.passed_start_line = False
        
        # World position - increases as we move forward through the world
        self.position = 0
        
        # Store the car's screen position for line crossing calculations
        self.car_screen_y = None
        
        # Create checkerboard patterns for start and finish lines
        self.start_line_height = 30
        self.finish_line_height = 30
        self.start_line_surface = self.create_checkerboard(road_width, self.start_line_height)
        self.finish_line_surface = self.create_checkerboard(road_width, self.finish_line_height, size=15)  # Smaller squares
        
        print(f"Track setup: Start at {self.start_line_position}, Finish at {self.finish_line_position}")

    def create_road(self):
        # Create road texture with markings
        tile_size = 100  # Size of each road tile
        num_tiles = 10   # Increased number of tiles for more coverage
        
        surface = pygame.Surface((road_width, tile_size * num_tiles))
        surface.fill(ROAD_GRAY)
        
        # Draw center line (dashed)
        dash_length = 40
        gap_length = 20
        line_width = 8
        center_x = road_width // 2
        
        y = 0
        while y < surface.get_height():
            pygame.draw.rect(surface, LINE_WHITE, 
                           (center_x - line_width//2, y, line_width, dash_length))
            y += dash_length + gap_length
        
        # Draw edge lines
        pygame.draw.rect(surface, LINE_WHITE, (5, 0, 3, surface.get_height()))
        pygame.draw.rect(surface, LINE_WHITE, (road_width - 8, 0, 3, surface.get_height()))
        
        return surface
        
    def generate_trees(self, num_trees):
        trees = []
        # Create a large enough world to include finish line
        world_length = self.finish_line_position + 1000
        
        for _ in range(num_trees):
            # Choose which side of the road
            if random.random() < 0.5:
                # Left side
                x = random.randint(50, road_left - 50)
            else:
                # Right side
                x = random.randint(road_right + 10, WIDTH - 50)
            
            # Distribute trees evenly through world length
            y = random.randint(0, world_length)
            
            # Choose a random tree image
            img = random.choice(tree_imgs)
            
            trees.append((x, y, img))
        
        return trees
        
    def reset(self):
        self.race_started = False
        self.race_finished = False
        self.start_time = None
        self.finish_time = None
        self.current_time = 0
        self.passed_start_line = False
        self.position = 0
        
    def update(self, speed):
        # Update world position
        self.position += speed
        
        # We need car_screen_y to be set for proper line crossing detection
        # (This will be set when draw() is called)
        if self.car_screen_y is None:
            return
        
        # Calculate where the start line appears on screen
        start_line_screen_y = self.position - self.start_line_position
        
        # Calculate where the finish line appears on screen
        finish_line_screen_y = self.position - self.finish_line_position
        
        # Check if start line has just crossed the car (disappeared off the bottom)
        if not self.race_started and not self.race_finished and start_line_screen_y > self.car_screen_y + 20:
            self.passed_start_line = True
            self.race_started = True
            self.start_time = time.time()
            print(f"Race started! Start line crossed car at position: {self.position}")
            
        # Update timer if race has started but not finished
        elif self.race_started and not self.race_finished:
            self.current_time = time.time() - self.start_time
            
            # Check if finish line has just crossed the car (disappeared off the bottom)
            if finish_line_screen_y > self.car_screen_y + 20:
                self.race_finished = True
                self.finish_time = time.time()
                finish_time = self.finish_time - self.start_time
                print(f"Race finished! Time: {finish_time:.2f}s")
                
                # Update best time
                if self.best_time is None or finish_time < self.best_time:
                    self.best_time = finish_time
        
    def draw(self, surface, car_screen_y):
        # Store car_screen_y for line crossing detection
        self.car_screen_y = car_screen_y
        
        game_area_height = self.game_height
    
        # Fill entire game area with sky blue (to avoid any previous draws)
        surface.fill(SKY_BLUE, (0, 0, WIDTH, game_area_height))
        
        # Draw grass background
        pygame.draw.rect(surface, GRASS_GREEN, (0, 0, road_left, game_area_height))
        pygame.draw.rect(surface, GRASS_GREEN, (road_right, 0, WIDTH - road_right, game_area_height))
        
        # Draw road - moving downward with improved tiling
        road_offset = int(self.position % self.road_height)
        
        # Draw one additional tile above the viewport to avoid gaps
        y_start = road_offset - self.road_height
        
        # Draw multiple copies of the road to fill the screen
        current_y = y_start
        while current_y < game_area_height:
            surface.blit(self.road_surface, (road_left, current_y))
            current_y += self.road_height
            
        # Draw trees - all trees move downward as position increases
        for x, pos, img in self.trees:
            # Tree appears on screen based on its position relative to world position
            screen_y = self.position - pos
            
            # Only draw if on screen
            if -img.get_height() < screen_y < game_area_height:
                surface.blit(img, (x, screen_y))
        
        # Draw start and finish lines as checkerboards
        start_y = self.position - self.start_line_position
        if -self.start_line_height < start_y < game_area_height:
            surface.blit(self.start_line_surface, (road_left, start_y))
            
            # Add "START" text
            font = pygame.font.SysFont(None, 36)
            text = font.render("START", True, (255, 255, 255))
            # Add a background to make text more visible
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 10))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)  # Semi-transparent
            surface.blit(text_bg, (road_left + road_width/2 - text.get_width()/2 - 5, start_y - 45))
            surface.blit(text, (road_left + road_width/2 - text.get_width()/2, start_y - 40))
            
        # Finish line screen position
        finish_y = self.position - self.finish_line_position
        if -self.finish_line_height < finish_y < game_area_height:
            surface.blit(self.finish_line_surface, (road_left, finish_y))
                           
            # Add "FINISH" text
            font = pygame.font.SysFont(None, 36)
            text = font.render("FINISH", True, (255, 255, 255))
            # Add a background to make text more visible
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 10))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)  # Semi-transparent
            surface.blit(text_bg, (road_left + road_width/2 - text.get_width()/2 - 5, finish_y - 45))
            surface.blit(text, (road_left + road_width/2 - text.get_width()/2, finish_y - 40))
            
    def draw_timer(self, surface):
        # Draw race information at the top of the screen
        font = pygame.font.SysFont(None, 36)
        
        # Draw current time or final time
        if self.race_finished:
            finish_time = self.finish_time - self.start_time
            time_text = f"Time: {finish_time:.2f}s"
            time_color = (0, 200, 0) if finish_time == self.best_time else (0, 0, 0)
        elif self.race_started:
            time_text = f"Time: {self.current_time:.2f}s"
            time_color = (0, 0, 0)
        elif self.passed_start_line:
            time_text = "Starting race..."
            time_color = (0, 0, 200)
        else:
            time_text = "Ready to start"
            time_color = (0, 0, 200)
            
        time_surface = font.render(time_text, True, time_color)
        surface.blit(time_surface, (WIDTH // 2 - time_surface.get_width() // 2, 20))
        
        # Draw best time if available
        if self.best_time is not None:
            best_text = f"Best: {self.best_time:.2f}s"
            best_surface = font.render(best_text, True, (0, 0, 0))
            surface.blit(best_surface, (WIDTH - best_surface.get_width() - 20, 20))
        
        # Draw race status indicators
        indicator_y = 60
        indicator_radius = 8
        padding = 10
        
        # Start indicator
        pygame.draw.circle(surface, 
                         (200, 200, 100) if self.passed_start_line and not self.race_started else
                         (START_LINE_COLOR if self.race_started else (200, 200, 200)), 
                         (WIDTH // 2 - 50, indicator_y), 
                         indicator_radius)
                         
        status_font = pygame.font.SysFont(None, 24)
        start_text = status_font.render("Start", True, (0, 0, 0))
        surface.blit(start_text, (WIDTH // 2 - 50 + indicator_radius + padding, indicator_y - 10))
        
        # Finish indicator
        pygame.draw.circle(surface, 
                         FINISH_LINE_COLOR if self.race_finished else (200, 200, 200), 
                         (WIDTH // 2 + 50, indicator_y), 
                         indicator_radius)
                         
        finish_text = status_font.render("Finish", True, (0, 0, 0))
        surface.blit(finish_text, (WIDTH // 2 + 50 + indicator_radius + padding, indicator_y - 10))

    def create_checkerboard(self, width, height, size=20, colors=((255, 255, 255), (0, 0, 0))):
        """Create a checkerboard pattern surface."""
        # Create a surface for the checkerboard
        surface = pygame.Surface((width, height))
        surface.fill(colors[0])  # Fill with first color as background
        
        # Calculate number of squares
        cols = width // size + 1
        rows = height // size + 1
        
        # Draw the checkerboard pattern
        for row in range(rows):
            for col in range(cols):
                # Alternate colors
                if (row + col) % 2 == 1:
                    pygame.draw.rect(surface, colors[1], 
                                   (col * size, row * size, size, size))
        
        return surface

# Car class with input-based speed control
class Car:
    def __init__(self, img, x, y, input_handler):
        self.img = img
        self.x = x
        self.screen_y = y  # Fixed screen position
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
        if input_value <= 0:
            mapped_speed = self.min_speed
        else:
            # Map input_value (0 to ~3) to speed range
            mapped_speed = self.min_speed + (input_value / 3.0) * (self.max_speed - self.min_speed)
            mapped_speed = min(mapped_speed, self.max_speed)  # Cap at max speed
        
        # Set car speed
        self.speed = mapped_speed
        
        return self.speed
    
    def draw(self, surface):
        # Draw car at its fixed screen position
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

# Initialize InputHandler with command line parameters
input_handler = InputHandler(demo_mode=demo_mode, port=args.port)

# Print status message
if demo_mode:
    print("Running in demo mode - use SPACEBAR to control")
else:
    print(f"Connected to Arduino on port: {args.port}")

# Create the car at a fixed screen position (centered, in lower part of screen)
car_screen_y = HEIGHT - 200  # Adjust for plot area
car = Car(car_img, WIDTH // 2, car_screen_y, input_handler)

# Create the game world
game_world = GameWorld(baseline_speed=car.speed, game_height=HEIGHT - 100)

# Create the signal plot
signal_plot = SignalPlot(WIDTH, 100)  # 100 pixels tall plot

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_r:
                # Reset race
                game_world.reset()
            elif event.key == pygame.K_SPACE:
                # Set key_pressed to True when space is pressed
                input_handler.set_key_state(True)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # Set key_pressed to False when space is released
                input_handler.set_key_state(False)
    
    # Get input value and update signal plot
    input_value = input_handler.get_value()
    signal_plot.update(input_value)
    
    # Update car speed based on input
    current_speed = car.update()
    
    # Update game world with car speed
    game_world.update(current_speed)
    
    # Clear screen
    screen.fill(SKY_BLUE)
    
    # Draw game world
    game_world.draw(screen, car_screen_y)
    
    # Draw car
    car.draw(screen)
    
    # Draw timer and race status
    game_world.draw_timer(screen)
    
    # Show debug info
    debug_font = pygame.font.SysFont(None, 20)
    debug_text = f"Position: {game_world.position:.1f}, Start: {game_world.start_line_position}, Finish: {game_world.finish_line_position}"
    debug = debug_font.render(debug_text, True, (0, 0, 0))
    screen.blit(debug, (10, 100))
    
    # Draw separator line
    pygame.draw.line(screen, (100, 100, 100), (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)
    
    # Draw signal plot at the bottom of the screen
    signal_plot.draw(screen, 0, HEIGHT - 100)
    
    # Show speed
    font = pygame.font.SysFont(None, 28)
    speed_text = f"Speed: {current_speed:.1f}"
    text_surface = font.render(speed_text, True, (0, 0, 0))
    screen.blit(text_surface, (20, 20))
    
    # Show controls
    controls_font = pygame.font.SysFont(None, 24)
    if input_handler.demo_mode:
        controls_text = "SPACE: Accelerate | R: Reset | Q: Quit"
    else:
        controls_text = "Use EMG Input | R: Reset | Q: Quit"
    controls_surface = controls_font.render(controls_text, True, (0, 0, 0))
    screen.blit(controls_surface, (20, 60))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
