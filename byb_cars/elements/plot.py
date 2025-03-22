import pygame
import numpy as np
from byb_cars import defaults
from byb_cars.elements.layout_config import layout


# Signal Plot class (similar to PyQtGraph implementation in main.py)
class SignalPlot:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer_size = 200  # Keep buffer size as it's not a layout parameter
        self.signal_buffer = np.zeros(self.buffer_size)
        self.surface = pygame.Surface((width, height))

        # Plot boundaries
        self.plot_width = width - 2 * layout.plot_margin
        self.plot_height = height - 2 * layout.plot_margin

        # Y-axis scaling (not layout, but kept here for simplicity)
        self.y_min = 0.0
        self.y_max = 3.0  # Maximum expected signal value

    def update(self, new_value):
        # Roll buffer and add new value
        self.signal_buffer = np.roll(self.signal_buffer, -1)
        self.signal_buffer[-1] = new_value

        # Dynamically adjust y-axis if needed
        if new_value > self.y_max:
            self.y_max = new_value * 1.2  # Add 20% headroom

    def draw(self, surface, x, y):
        # Clear plot area
        self.surface.fill(defaults.PLOT_BG)

        # Draw border
        pygame.draw.rect(
            self.surface,
            (0, 0, 0),
            (layout.plot_margin, layout.plot_margin, self.plot_width, self.plot_height),
            1,
        )

        # Draw grid lines
        for i in range(1, layout.plot_grid_lines):
            y_pos = layout.plot_margin + i * self.plot_height // layout.plot_grid_lines
            pygame.draw.line(
                self.surface,
                defaults.PLOT_GRID,
                (layout.plot_margin, y_pos),
                (layout.plot_margin + self.plot_width, y_pos),
                1,
            )

            # Add y-axis labels
            font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.small_size)
            value = self.y_max * (layout.plot_grid_lines - i) / layout.plot_grid_lines
            label = font.render(f"{value:.1f}", True, layout.fonts.normal_color)
            self.surface.blit(label, (layout.plot_margin - 5, y_pos - layout.plot_label_y_offset))

        # Draw threshold line at 1.0
        threshold_value = 1.0  # Keep this as it's a business logic parameter
        threshold_y = (
            layout.plot_margin + self.plot_height 
            - (threshold_value / self.y_max * self.plot_height)
        )
        pygame.draw.line(
            self.surface,
            defaults.THRESHOLD_LINE,
            (layout.plot_margin, threshold_y),
            (layout.plot_margin + self.plot_width, threshold_y),
            1,
        )

        # Draw signal line
        points = []
        for i in range(self.buffer_size):
            x_pos = layout.plot_margin + i * self.plot_width / (self.buffer_size - 1)
            # Scale value to plot height (flipped, as pygame y increases downward)
            y_pos = (
                layout.plot_margin
                + self.plot_height
                - (self.signal_buffer[i] / self.y_max * self.plot_height)
            )
            y_pos = min(
                layout.plot_margin + self.plot_height, max(layout.plot_margin, y_pos)
            )  # Clamp to plot area
            points.append((x_pos, y_pos))

        # Draw signal line
        if len(points) > 1:
            pygame.draw.lines(self.surface, defaults.PLOT_LINE, False, points, 2)

        # Add title and labels
        font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.normal_size)
        title = font.render("EMG Signal", True, layout.fonts.normal_color)
        self.surface.blit(
            title, 
            (self.width // 2 - title.get_width() // 2, layout.plot_title_y_offset)
        )

        # Current value
        if len(self.signal_buffer) > 0:
            current_value = self.signal_buffer[-1]
            value_text = font.render(f"Current: {current_value:.2f}", True, layout.fonts.normal_color)
            self.surface.blit(
                value_text, 
                (self.width - layout.plot_value_x_offset, layout.plot_title_y_offset)
            )

        # Blit the plot surface onto the main surface
        surface.blit(self.surface, (x, y))
