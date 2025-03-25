import pygame
import sys
import random
import requests
from pathlib import Path
import numpy as np
import time
import argparse
import json
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional

# Import the InputHandler
from byb_cars.input_handler import InputHandler
from byb_cars.elements import Car, SignalPlot, GameWorld, ScoreManager, get_username, show_high_scores
from byb_cars import defaults
from byb_cars.elements.layout_config import layout


@dataclass
class MainConfig:
    # Screen layout
    car_offset_from_bottom: int = 200
    plot_height: int = 100
    game_height_offset: int = 100
    
    # Separator line
    separator_line_width: int = 2
    separator_line_color: tuple = (100, 100, 100)
    
    # Font sizes
    debug_font_size: int = 20
    speed_font_size: int = 28
    controls_font_size: int = 24
    
    # Text positions with vertical spacing
    speed_text_pos: tuple = (20, 20)  # Keep speed at top
    user_text_pos: tuple = (defaults.WIDTH - 200, 20)  # User name at top right
    controls_text_pos: tuple = (20, 60)  # Controls below speed
    debug_text_pos: tuple = (10, 100)  # Debug below controls
    
    # Animation
    fps: int = 60

main_config = MainConfig()


# Parse command line arguments
parser = argparse.ArgumentParser(description="Scrolling Road with EMG Control")
parser.add_argument(
    "--demo",
    action="store_true",
    help="Run in demo mode with keyboard control instead of EMG",
)
parser.add_argument(
    "--port",
    type=str,
    default=None,
    help="Serial port for Arduino (e.g., COM3 on Windows, /dev/ttyACM0 on Linux)",
)
args = parser.parse_args()

# Determine if we're running in demo mode
demo_mode = True if args.demo else (args.port is None)

# Initialize configuration
config = MainConfig()

# Initialize score manager
score_manager = ScoreManager()
print(f"Loaded {len(score_manager.scores)} scores")

# Initialize Pygame
pygame.init()

# Screen dimensions
screen = pygame.display.set_mode((layout.screen_width, layout.screen_height))
pygame.display.set_caption("Scrolling Road with Car")

# Get initial username
current_username = get_username(screen)
user_best_time = score_manager.get_best_time(current_username)
print(f"Best time for {current_username}: {user_best_time}")

# Initialize InputHandler with command line parameters
input_handler = InputHandler(demo_mode=demo_mode, port=args.port)

# Print status message
if demo_mode:
    print("Running in demo mode - use SPACEBAR to control")
else:
    print(f"Connected to Arduino on port: {args.port}")

# Calculate positions based on config
car_screen_y = defaults.HEIGHT - config.car_offset_from_bottom
plot_y = defaults.HEIGHT - config.plot_height

# Create the car at a fixed screen position (centered, in lower part of screen)
car = Car(layout.screen_width // 2, layout.car_screen_y, input_handler)

# Create the game world - get user's best time if available
user_best_time = score_manager.get_best_time(current_username)
game_world = GameWorld(game_height=defaults.HEIGHT - config.game_height_offset)
if user_best_time is not None:
    game_world.best_time = user_best_time
    print(f"Loaded best time for {current_username}: {user_best_time}")

# Create the signal plot
signal_plot = SignalPlot(layout.screen_width, layout.plot_height)

# Game loop
running = True
clock = pygame.time.Clock()
show_scores = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_r:
                # Reset race and potentially get new username
                game_world.reset()
                # Remove the score saved flag so new scores will be saved
                if hasattr(game_world, '_score_saved'):
                    delattr(game_world, '_score_saved')
                current_username = get_username(screen)
                # Update user's best time
                user_best_time = score_manager.get_best_time(current_username)
                if user_best_time is not None:
                    game_world.best_time = user_best_time
            elif event.key == pygame.K_h:
                # Show high scores
                show_high_scores(screen, score_manager)
            elif event.key == pygame.K_SPACE:
                # Set key_pressed to True when space is pressed
                input_handler.set_key_state(True)
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                # Set key_pressed to False when space is released
                input_handler.set_key_state(False)

    # Handle high score display
    if show_scores:
        show_high_scores(screen, score_manager)
        show_scores = False
        continue

    # Get input value and update signal plot
    input_value = input_handler.get_value()
    signal_plot.update(input_value)

    # Update car speed based on input
    current_speed = car.update()

    # Update game world with car speed
    game_world.update(current_speed)

    # Check if race just finished and save score
    if game_world.race_finished and game_world.finish_time and not hasattr(game_world, '_score_saved'):
        finish_time = game_world.finish_time - game_world.start_time
        score_manager.add_score(current_username, finish_time)
        # Mark that we've saved this score
        game_world._score_saved = True

    # Clear screen
    screen.fill(defaults.SKY_BLUE)

    # Draw game world
    game_world.draw(screen, layout.car_screen_y)

    # Draw car
    car.draw(screen)

    # Draw timer and race status
    game_world.draw_timer(screen)

    # Show debug info
    debug_font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.debug_size)
    debug_text = f"Position: {game_world.position:.1f}"
    # Activate for debug
    # debug = debug_font.render(debug_text, True, layout.fonts.normal_color)
    # screen.blit(debug, layout.debug_text_pos)

    # Draw separator line
    pygame.draw.line(
        screen,
        layout.separator_line_color,
        (0, layout.separator_line_y),
        (layout.screen_width, layout.separator_line_y),
        layout.separator_line_width,
    )

    # Draw signal plot at the bottom of the screen
    signal_plot.draw(screen, 0, layout.plot_y)

    # Show speed
    font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.normal_size)
    speed_text = f"Speed: {current_speed:.1f}"
    text_surface = font.render(speed_text, True, layout.fonts.normal_color)
    screen.blit(text_surface, layout.speed_text_pos)

    # Show current user (use the configured position)
    user_text = f"User: {current_username}"
    user_surface = font.render(user_text, True, layout.fonts.normal_color)
    screen.blit(
        user_surface, (defaults.WIDTH - user_surface.get_width() - layout.user_text_x_padding, layout.user_text_y)
    )

    # Show controls
    controls_font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.small_size)
    if input_handler.demo_mode:
        controls_text = "R: Reset | H: Ranking | Q: Quit"
    else:
        controls_text = "R: Reset | H: Ranking | Q: Quit"
    controls_surface = controls_font.render(controls_text, True, layout.fonts.normal_color)
    screen.blit(controls_surface, layout.controls_text_pos)

    # Update display
    pygame.display.flip()
    clock.tick(main_config.fps)

pygame.quit()
sys.exit()
