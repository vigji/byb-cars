import pygame
import numpy as np
from dataclasses import dataclass
from byb_cars import defaults


@dataclass
class PlotConfig:
    # Buffer configuration
    buffer_size: int = 200
    
    # Plot layout
    plot_margin: int = 10
    
    # Y-axis configuration
    y_min: float = 0.0
    y_max: float = 3.0
    y_max_headroom_factor: float = 1.2  # Multiplier for dynamic y-max adjustment
    
    # Grid configuration
    grid_lines: int = 4
    
    # Threshold configuration
    threshold_value: float = 1.0
    
    # Text configuration
    axis_font_size: int = 20
    title_font_size: int = 24
    label_y_offset: int = 10
    title_y_offset: int = 5
    current_value_x_offset: int = 150
    
    # Colors are already in defaults


# Signal Plot class (similar to PyQtGraph implementation in main.py)
class SignalPlot:
    def __init__(self, width, height, config=None):
        self.width = width
        self.height = height
        self.config = config or PlotConfig()
        self.buffer_size = self.config.buffer_size
        self.signal_buffer = np.zeros(self.buffer_size)
        self.surface = pygame.Surface((width, height))

        # Plot boundaries
        self.plot_width = width - 2 * self.config.plot_margin
        self.plot_height = height - 2 * self.config.plot_margin

        # Y-axis scaling
        self.y_min = self.config.y_min
        self.y_max = self.config.y_max  # Maximum expected signal value

    def update(self, new_value):
        # Roll buffer and add new value
        self.signal_buffer = np.roll(self.signal_buffer, -1)
        self.signal_buffer[-1] = new_value

        # Dynamically adjust y-axis if needed
        if new_value > self.y_max:
            self.y_max = new_value * self.config.y_max_headroom_factor

    def draw(self, surface, x, y):
        # Clear plot area
        self.surface.fill(defaults.PLOT_BG)

        # Draw border
        pygame.draw.rect(
            self.surface,
            (0, 0, 0),
            (self.config.plot_margin, self.config.plot_margin, self.plot_width, self.plot_height),
            1,
        )

        # Draw grid lines
        for i in range(1, self.config.grid_lines):
            y_pos = self.config.plot_margin + i * self.plot_height // self.config.grid_lines
            pygame.draw.line(
                self.surface,
                defaults.PLOT_GRID,
                (self.config.plot_margin, y_pos),
                (self.config.plot_margin + self.plot_width, y_pos),
                1,
            )

            # Add y-axis labels
            font = pygame.font.SysFont(None, self.config.axis_font_size)
            value = self.y_max * (self.config.grid_lines - i) / self.config.grid_lines
            label = font.render(f"{value:.1f}", True, (0, 0, 0))
            self.surface.blit(label, (self.config.plot_margin - 5, y_pos - self.config.label_y_offset))

        # Draw threshold line at threshold_value
        threshold_y = (
            self.config.plot_margin + self.plot_height 
            - (self.config.threshold_value / self.y_max * self.plot_height)
        )
        pygame.draw.line(
            self.surface,
            defaults.THRESHOLD_LINE,
            (self.config.plot_margin, threshold_y),
            (self.config.plot_margin + self.plot_width, threshold_y),
            1,
        )

        # Draw signal line
        points = []
        for i in range(self.buffer_size):
            x_pos = self.config.plot_margin + i * self.plot_width / (self.buffer_size - 1)
            # Scale value to plot height (flipped, as pygame y increases downward)
            y_pos = (
                self.config.plot_margin
                + self.plot_height
                - (self.signal_buffer[i] / self.y_max * self.plot_height)
            )
            y_pos = min(
                self.config.plot_margin + self.plot_height, max(self.config.plot_margin, y_pos)
            )  # Clamp to plot area
            points.append((x_pos, y_pos))

        # Draw signal line
        if len(points) > 1:
            pygame.draw.lines(self.surface, defaults.PLOT_LINE, False, points, 2)

        # Add title and labels
        font = pygame.font.SysFont(None, self.config.title_font_size)
        title = font.render("EMG Signal", True, (0, 0, 0))
        self.surface.blit(
            title, 
            (self.width // 2 - title.get_width() // 2, self.config.title_y_offset)
        )

        # Current value
        if len(self.signal_buffer) > 0:
            current_value = self.signal_buffer[-1]
            value_text = font.render(f"Current: {current_value:.2f}", True, (0, 0, 0))
            self.surface.blit(
                value_text, 
                (self.width - self.config.current_value_x_offset, self.config.title_y_offset)
            )

        # Blit the plot surface onto the main surface
        surface.blit(self.surface, (x, y))
