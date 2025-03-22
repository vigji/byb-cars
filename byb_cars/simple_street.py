"""Simple Street Racing Game - Main Entry Point."""

import argparse
import sys
import os
from pathlib import Path

# Add the current directory to the path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

# Try to find the required modules
try:
    # First, try direct imports (if files are in the same directory)
    import pygame
    try:
        from game import Game
        from input_handler import InputHandler
        print("Found game modules in current directory")
    except ImportError:
        # Check if we're in a subdirectory of the project
        parent_dir = current_dir.parent
        sys.path.insert(0, str(parent_dir))
        try:
            from game import Game
            from input_handler import InputHandler
            print("Found game modules in parent directory")
        except ImportError:
            # Last resort - look for byb_cars package
            try:
                from byb_cars.game import Game
                from byb_cars.input_handler import InputHandler
                print("Found game modules in byb_cars package")
            except ImportError:
                # List all Python files in current and parent directory to help debugging
                print("Error: Could not find required game modules.")
                print("\nPython files in current directory:")
                for file in current_dir.glob("*.py"):
                    print(f"  - {file.name}")
                print("\nPython files in parent directory:")
                for file in parent_dir.glob("*.py"):
                    print(f"  - {file.name}")
                sys.exit(1)
except ImportError:
    print("Error: pygame is not installed. Please install it with:")
    print("pip install pygame")
    sys.exit(1)

from simple_street.resources import (
    WIDTH, HEIGHT, SKY_BLUE, CAR_HEIGHT, CAR_SCREEN_Y, 
    download_assets, load_car_image, load_tree_images
)
from simple_street.entities import GameWorld, Car
from simple_street.ui import SignalPlot, draw_game_info

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple Street - EMG controlled racing game")
    parser.add_argument("--demo", action="store_true", 
                        help="Run in demo mode with keyboard control instead of EMG")
    parser.add_argument("--port", type=str, default=None,
                        help="Serial port for Arduino (e.g., COM3 on Windows, /dev/ttyACM0 on Linux)")
    args = parser.parse_args()
    
    # Determine if we're running in demo mode
    demo_mode = True if args.demo else (args.port is None)
    
    # Initialize pygame
    pygame.init()
    
    print(f"Running in {'demo' if demo_mode else 'Arduino'} mode")
    if not demo_mode:
        print(f"Using port: {args.port}")
    
    # Create screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Street Racing")
    
    # Download and load assets
    assets_dir = download_assets()
    car_img = load_car_image(assets_dir, CAR_HEIGHT)
    tree_imgs = load_tree_images(assets_dir)
    
    # Create input handler with either demo mode or Arduino port
    input_handler = InputHandler(demo_mode=demo_mode, port=args.port)
    
    # Create the car
    car = Car(car_img, WIDTH // 2, CAR_SCREEN_Y, input_handler)
    
    # Create the game world
    game_world = GameWorld(baseline_speed=car.speed, game_height=HEIGHT - 100)
    
    # Generate trees
    game_world.generate_trees(tree_imgs)
    
    # Create the signal plot
    signal_plot = SignalPlot(WIDTH, 100)  # 100 pixels tall plot
    
    # Create and run the game
    game = Game(input_handler)
    game.run()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 