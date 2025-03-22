import pygame
from dataclasses import dataclass
from byb_cars.defaults import WIDTH, HEIGHT
from byb_cars.elements.handle_assets import get_car_img


@dataclass
class CarConfig:
    min_speed: float = 0.5
    max_speed: float = 8.0
    default_speed: float = 3.0
    input_mapping_divisor: float = 3.0
    
    speed_bar_width: int = 100
    speed_bar_height: int = 10
    speed_bar_padding: int = 20
    speed_bar_y: int = 20
    
    # Thresholds for speed color (as percentage of max_speed)
    low_speed_threshold: float = 0.33
    medium_speed_threshold: float = 0.66
    
    # Speed indicator colors
    low_speed_color: tuple = (0, 255, 0)     # Green
    medium_speed_color: tuple = (255, 255, 0) # Yellow
    high_speed_color: tuple = (255, 0, 0)     # Red
    speed_bar_outline_color: tuple = (50, 50, 50)


# Car class with input-based speed control
class Car:
    def __init__(self, x, y, input_handler, config=None):
        self.x = x
        self.screen_y = y  # Fixed screen position
        self.input_handler = input_handler
        self.config = config or CarConfig()

        self.img = get_car_img()
        self.speed = self.config.default_speed

    def update(self):
        # Get input value from InputHandler
        input_value = self.input_handler.get_value()

        # Map input value to speed (adjust ranges as needed)
        if input_value <= 0:
            mapped_speed = self.config.min_speed
        else:
            # Map input_value to speed range
            mapped_speed = self.config.min_speed + (input_value / self.config.input_mapping_divisor) * (
                self.config.max_speed - self.config.min_speed
            )
            mapped_speed = min(mapped_speed, self.config.max_speed)  # Cap at max speed

        # Set car speed
        self.speed = mapped_speed

        return self.speed

    def draw(self, surface):
        # Draw car at its fixed screen position
        surface.blit(self.img, (self.x - self.img.get_width() // 2, self.screen_y))

        # Draw speed indicator
        self._draw_speed_indicator(surface)

    def _draw_speed_indicator(self, surface):
        # Draw a speed bar on the right side of the screen
        bar_x = WIDTH - self.config.speed_bar_width - self.config.speed_bar_padding
        bar_y = self.config.speed_bar_y

        # Background bar (outline)
        pygame.draw.rect(
            surface,
            self.config.speed_bar_outline_color,
            (bar_x, bar_y, self.config.speed_bar_width, self.config.speed_bar_height),
            2,
        )

        # Calculate fill amount based on current speed
        fill_width = int((self.speed / self.config.max_speed) * self.config.speed_bar_width)

        # Fill bar (colored by speed)
        if self.speed < self.config.max_speed * self.config.low_speed_threshold:
            color = self.config.low_speed_color
        elif self.speed < self.config.max_speed * self.config.medium_speed_threshold:
            color = self.config.medium_speed_color
        else:
            color = self.config.high_speed_color

        pygame.draw.rect(
            surface, color, (bar_x, bar_y, fill_width, self.config.speed_bar_height)
        )
