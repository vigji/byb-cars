"""Simple Street Racing Game - Main Entry Point."""

import pygame
import sys
import time

# Import modules
from byb_cars.input_handler import InputHandler
from simple_street.resources import (
    WIDTH, HEIGHT, SKY_BLUE, CAR_HEIGHT, CAR_SCREEN_Y, 
    download_assets, load_car_image, load_tree_images
)
from simple_street.entities import GameWorld, Car
from simple_street.ui import SignalPlot, draw_game_info

def main():
    # Initialize Pygame
    pygame.init()
    
    # Create screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Street Racing")
    
    # Download and load assets
    assets_dir = download_assets()
    car_img = load_car_image(assets_dir, CAR_HEIGHT)
    tree_imgs = load_tree_images(assets_dir)
    
    # Initialize input handler (demo mode = keyboard control)
    input_handler = InputHandler(demo_mode=True)
    
    # Create the car
    car = Car(car_img, WIDTH // 2, CAR_SCREEN_Y, input_handler)
    
    # Create the game world
    game_world = GameWorld(baseline_speed=car.speed, game_height=HEIGHT - 100)
    
    # Generate trees
    game_world.generate_trees(tree_imgs)
    
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
        game_world.draw(screen, car.screen_y)
        
        # Draw car
        car.draw(screen)
        
        # Draw timer and race status
        game_world.draw_timer(screen)
        
        # Show debug info
        game_world.draw_debug_info(screen)
        
        # Draw separator line
        pygame.draw.line(screen, (100, 100, 100), (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)
        
        # Draw signal plot at the bottom of the screen
        signal_plot.draw(screen, 0, HEIGHT - 100)
        
        # Show speed and controls
        draw_game_info(screen, current_speed, input_handler)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 