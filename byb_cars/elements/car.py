import pygame
from dataclasses import dataclass
from byb_cars.defaults import WIDTH, HEIGHT
from byb_cars.elements.handle_assets import get_car_img
from byb_cars.elements.layout_config import layout


@dataclass
class CarConfig:
    min_speed: float = 0.1
    max_speed: float = 8.0
    default_speed: float = 3.0
    input_mapping_divisor: float = .3
    
    # Thresholds for speed color (as percentage of max_speed)
    low_speed_threshold: float = 0.33
    medium_speed_threshold: float = 0.66
    

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
        bar_x = WIDTH - layout.speed_bar_width - layout.speed_bar_padding
        bar_y = layout.speed_bar_y

        # Background bar (outline)
        pygame.draw.rect(
            surface,
            layout.speed_bar_outline_color,
            (bar_x, bar_y, layout.speed_bar_width, layout.speed_bar_height),
            2,
        )

        # Calculate fill amount based on current speed
        fill_width = int((self.speed / self.config.max_speed) * layout.speed_bar_width)

        # Fill bar (colored by speed)
        if self.speed < self.config.max_speed * self.config.low_speed_threshold:
            color = layout.low_speed_color
        elif self.speed < self.config.max_speed * self.config.medium_speed_threshold:
            color = layout.medium_speed_color
        else:
            color = layout.high_speed_color

        pygame.draw.rect(
            surface, color, (bar_x, bar_y, fill_width, layout.speed_bar_height)
        )
