"""UI elements for Simple Street racing game."""

import pygame
import numpy as np
from simple_street.resources import (
    WIDTH, PLOT_BG, PLOT_GRID, PLOT_LINE, THRESHOLD_LINE
)

class SignalPlot:
    """Real-time plot for signal data visualization."""
    
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
        """Add new value to the signal buffer."""
        # Roll buffer and add new value
        self.signal_buffer = np.roll(self.signal_buffer, -1)
        self.signal_buffer[-1] = new_value
        
        # Dynamically adjust y-axis if needed
        if new_value > self.y_max:
            self.y_max = new_value * 1.2  # Give some headroom
        
    def draw(self, surface, x, y):
        """Draw the plot on the provided surface."""
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


def draw_game_info(surface, speed, input_handler):
    """Draw game information and controls."""
    # Show speed
    font = pygame.font.SysFont(None, 28)
    speed_text = f"Speed: {speed:.1f}"
    text_surface = font.render(speed_text, True, (0, 0, 0))
    surface.blit(text_surface, (20, 20))
    
    # Show controls
    controls_font = pygame.font.SysFont(None, 24)
    if input_handler.demo_mode:
        controls_text = "SPACE: Accelerate | R: Reset | Q: Quit"
    else:
        controls_text = "Use EMG Input | R: Reset | Q: Quit"
    controls_surface = controls_font.render(controls_text, True, (0, 0, 0))
    surface.blit(controls_surface, (20, 60)) 