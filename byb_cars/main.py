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
from byb_cars.elements import Car, SignalPlot, GameWorld
from byb_cars import defaults
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
screen = pygame.display.set_mode((defaults.WIDTH, defaults.HEIGHT))
pygame.display.set_caption("Scrolling Road with Car")

# Initialize InputHandler with command line parameters
input_handler = InputHandler(demo_mode=demo_mode, port=args.port)

# Print status message
if demo_mode:
    print("Running in demo mode - use SPACEBAR to control")
else:
    print(f"Connected to Arduino on port: {args.port}")

# Create the car at a fixed screen position (centered, in lower part of screen)
car_screen_y = defaults.HEIGHT - 200  # Adjust for plot area
car = Car(defaults.WIDTH // 2, car_screen_y, input_handler)

# Create the game world
game_world = GameWorld(baseline_speed=car.speed, game_height=defaults.HEIGHT - 100)

# Create the signal plot
signal_plot = SignalPlot(defaults.WIDTH, 100)  # 100 pixels tall plot

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
    screen.fill(defaults.SKY_BLUE)
    
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
    pygame.draw.line(screen, (100, 100, 100), (0, defaults.HEIGHT - 100), (defaults.WIDTH, defaults.HEIGHT - 100), 2)
    
    # Draw signal plot at the bottom of the screen
    signal_plot.draw(screen, 0, defaults.HEIGHT - 100)
    
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
