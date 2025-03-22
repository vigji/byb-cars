import pygame
from byb_cars.defaults import WIDTH, HEIGHT
from byb_cars.elements.handle_assets import get_car_img


# Car class with input-based speed control
class Car:
    def __init__(self, x, y, input_handler):
        self.x = x
        self.screen_y = y  # Fixed screen position
        self.input_handler = input_handler

        
        self.img = get_car_img()
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
            mapped_speed = self.min_speed + (input_value / 3.0) * (
                self.max_speed - self.min_speed
            )
            mapped_speed = min(mapped_speed, self.max_speed)  # Cap at max speed

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
        bar_x = WIDTH - self.speed_bar_width - 20
        bar_y = 20

        # Background bar (outline)
        pygame.draw.rect(
            surface,
            (50, 50, 50),
            (bar_x, bar_y, self.speed_bar_width, self.speed_bar_height),
            2,
        )

        # Calculate fill amount based on current speed
        fill_width = int((self.speed / self.max_speed) * self.speed_bar_width)

        # Fill bar (colored by speed)
        if self.speed < self.max_speed * 0.33:
            color = (0, 255, 0)  # Green for low speed
        elif self.speed < self.max_speed * 0.66:
            color = (255, 255, 0)  # Yellow for medium speed
        else:
            color = (255, 0, 0)  # Red for high speed

        pygame.draw.rect(
            surface, color, (bar_x, bar_y, fill_width, self.speed_bar_height)
        )
