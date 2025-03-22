from dataclasses import dataclass
from typing import Tuple, Dict, Optional
from byb_cars import defaults


@dataclass
class FontConfig:
    """Configuration for all fonts used in the game"""
    # Font family - None means system default
    default_font: Optional[str] = None
    
    # Font sizes
    title_size: int = 36
    subtitle_size: int = 32
    normal_size: int = 28
    small_size: int = 24
    debug_size: int = 20
    
    # Font colors
    normal_color: Tuple[int, int, int] = (0, 0, 0)
    highlight_color: Tuple[int, int, int] = (0, 200, 0)
    alert_color: Tuple[int, int, int] = (200, 0, 0)
    info_color: Tuple[int, int, int] = (0, 0, 200)
    light_color: Tuple[int, int, int] = (255, 255, 255)
    gray_color: Tuple[int, int, int] = (200, 200, 200)


@dataclass
class LayoutConfig:
    """Central configuration for all UI layout parameters"""
    
    # ======================
    # Screen and global layout
    # ======================
    screen_width: int = defaults.WIDTH
    screen_height: int = defaults.HEIGHT
    
    # ======================
    # Main layout areas
    # ======================
    car_offset_from_bottom: int = 200  # Car position from bottom
    plot_height: int = 100
    game_height: int = defaults.HEIGHT - 100  # Height of game area
    separator_line_width: int = 2
    separator_line_color: Tuple[int, int, int] = (100, 100, 100)
    
    # ======================
    # Text positions
    # ======================
    speed_text_pos: Tuple[int, int] = (20, 20)  # Top left
    user_text_pos: Tuple[int, int] = (defaults.WIDTH - 200, 20)  # Top right
    controls_text_pos: Tuple[int, int] = (20, 60)  # Below speed
    debug_text_pos: Tuple[int, int] = (10, 100)  # Debug info position
    
    # ======================
    # Car display
    # ======================
    car_height: int = 120
    car_width: int = 60  # Will be adjusted by aspect ratio
    speed_bar_width: int = 100
    speed_bar_height: int = 10
    speed_bar_padding: int = 20  # Padding from right edge
    speed_bar_y: int = 60  # Vertical position
    speed_bar_outline_color: Tuple[int, int, int] = (50, 50, 50)
    low_speed_color: Tuple[int, int, int] = (0, 255, 0)
    medium_speed_color: Tuple[int, int, int] = (255, 255, 0)
    high_speed_color: Tuple[int, int, int] = (255, 0, 0)
    
    # ======================
    # Signal plot
    # ======================
    plot_margin: int = 10  # Margin inside the plot
    plot_grid_lines: int = 4
    plot_label_y_offset: int = 10
    plot_title_y_offset: int = 5
    plot_value_x_offset: int = 150  # X offset for current value display
    
    # ======================
    # World display
    # ======================
    
    # Timer and race info
    timer_y: int = 20  # Timer vertical position
    best_time_y: int = 60  # Best time vertical position
    best_time_x_padding: int = 20  # Padding from right edge
    
    # Race indicators
    indicator_y: int = 60  # Status indicators vertical position
    indicator_radius: int = 8
    indicator_padding: int = 10
    indicator_x_offset: int = 50  # Distance from center
    
    # ======================
    # Score and input display
    # ======================
    # Input dialog
    input_box_width: int = 300
    input_box_height: int = 40
    input_box_color: Tuple[int, int, int] = (100, 100, 200)
    input_box_active_color: Tuple[int, int, int] = (150, 150, 255)
    input_prompt_padding: int = 10  # Space between prompt and input box
    
    # High scores display
    highscore_title_top: int = 50  # Top position of highscore title
    highscore_list_top_padding: int = 50  # Space below title before first score
    highscore_entry_spacing: int = 40  # Vertical space between entries
    highscore_instruction_bottom: int = 50  # Bottom padding for instructions
    
    # ======================
    # Font configuration
    # ======================
    fonts: FontConfig = FontConfig()
    
    def __post_init__(self):
        # Calculate derived values
        self.separator_line_y = self.screen_height - self.plot_height
        self.car_screen_y = self.screen_height - self.car_offset_from_bottom
        self.plot_y = self.screen_height - self.plot_height


# Global instance for easy import
layout = LayoutConfig() 