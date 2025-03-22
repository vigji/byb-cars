import pygame
import random
import time
from dataclasses import dataclass
from byb_cars import defaults
from byb_cars.elements.handle_assets import get_tree_imgs
from byb_cars.elements.layout_config import layout


@dataclass
class WorldConfig:
    # Race configuration
    baseline_speed: float = 3.0
    target_time: float = 10.0  # 10 seconds to finish at baseline speed
    fps: int = 60
    start_line_position: int = 500

    
    # Road configuration
    road_width_fraction: float = 1/3  # Road width as a fraction of screen width
    
    # World elements
    num_trees: int = 120
    tree_min_side_offset: int = 50
    tree_min_road_offset: int = 10
    tree_height: int = 120
    
    # Road tile configuration
    tile_size: int = 100
    num_tiles: int = 10
    
    # Road markings
    dash_length: int = 40
    gap_length: int = 20
    line_width: int = 8
    edge_line_width: int = 3
    edge_line_offset: int = 5
    
    # Start/finish lines
    start_line_height: int = 30
    finish_line_height: int = 30
    checkerboard_size: int = 15
    finish_checkerboard_size: int = 15
    
    # Text configuration
    start_finish_font_size: int = 36
    status_font_size: int = 24
    text_bg_padding: int = 5
    text_y_offset: int = 40
    text_bg_alpha: int = 180
    

world_config = WorldConfig()


# World manages all game world elements including road, trees, and race lines
class GameWorld:
    def __init__(self, game_height=None):
        self.game_height = game_height or layout.game_height


        # Track distance calculation - increased for more stable experience
        self.target_time = 10.0  # 10 seconds to finish at baseline speed
        fps = 60
        baseline_speed = 3.0
        self.track_distance = int(baseline_speed * fps * self.target_time)

        # Road dimensions
        self.road_width = int(defaults.WIDTH * world_config.road_width_fraction)
        self.road_left = (defaults.WIDTH - self.road_width) // 2
        self.road_right = self.road_left + self.road_width

        # Create the road texture
        self.road_surface = self.create_road()
        self.road_height = self.road_surface.get_height()

        # Start and finish line positions - positive = distance from start
        self.start_line_position = 500  # This is a game parameter, not layout
        self.finish_line_position = self.start_line_position + self.track_distance

        self.tree_imgs = get_tree_imgs(world_config.tree_height)

        # Create trees - 120 is a game parameter, not layout
        self.trees = self.generate_trees(120)

        # Race state
        self.race_started = False
        self.race_finished = False
        self.start_time = None
        self.finish_time = None
        self.current_time = 0
        self.best_time = None
        self.passed_start_line = False

        # World position - increases as we move forward through the world
        self.position = 0

        # Store the car's screen position for line crossing calculations
        self.car_screen_y = None

        # Create checkerboard patterns for start and finish lines
        self.start_line_surface = self.create_checkerboard(
            self.road_width, world_config.start_line_height, size=world_config.checkerboard_size
        )
        self.finish_line_surface = self.create_checkerboard(
            self.road_width, 
            world_config.finish_line_height, 
            size=world_config.checkerboard_size
        )

        print(
            f"Track setup: Start at {self.start_line_position}, Finish at {self.finish_line_position}"
        )

    def create_road(self):
        # Create road texture with markings
        tile_size = 100  # This could be parameterized but it's not critical
        num_tiles = 10   # Same here
        
        surface = pygame.Surface((self.road_width, tile_size * num_tiles))
        surface.fill(defaults.ROAD_GRAY)

        # Draw center line (dashed)
        dash_length = world_config.dash_length
        gap_length = world_config.gap_length
        line_width = world_config.line_width
        center_x = self.road_width // 2

        y = 0
        while y < surface.get_height():
            pygame.draw.rect(
                surface,
                defaults.LINE_WHITE,
                (center_x - line_width // 2, y, line_width, dash_length),
            )
            y += dash_length + gap_length

        # Draw edge lines
        edge_offset = world_config.edge_line_offset
        edge_width = world_config.edge_line_width
        pygame.draw.rect(
            surface, defaults.LINE_WHITE, (edge_offset, 0, edge_width, surface.get_height())
        )
        pygame.draw.rect(
            surface,
            defaults.LINE_WHITE,
            (self.road_width - edge_offset - edge_width, 0, edge_width, surface.get_height()),
        )

        return surface

    def generate_trees(self, num_trees):
        trees = []
        # Create a large enough world to include finish line
        world_length = self.finish_line_position + 1000

        for _ in range(num_trees):
            # Choose which side of the road
            if random.random() < 0.5:
                # Left side
                x = random.randint(
                    world_config.tree_min_side_offset, 
                    self.road_left - world_config.tree_min_side_offset
                )
            else:
                # Right side
                x = random.randint(
                    self.road_right + world_config.tree_min_road_offset, 
                    defaults.WIDTH - world_config.tree_min_side_offset
                )

            # Distribute trees evenly through world length
            y = random.randint(0, world_length)

            # Choose a random tree image
            img = random.choice(self.tree_imgs)

            trees.append((x, y, img))

        return trees

    def reset(self):
        self.race_started = False
        self.race_finished = False
        self.start_time = None
        self.finish_time = None
        self.current_time = 0
        self.passed_start_line = False
        self.position = 0

    def update(self, speed):
        # Update world position
        self.position += speed

        # We need car_screen_y to be set for proper line crossing detection
        # (This will be set when draw() is called)
        if self.car_screen_y is None:
            return

        # Calculate where the start line appears on screen
        start_line_screen_y = self.position - self.start_line_position

        # Calculate where the finish line appears on screen
        finish_line_screen_y = self.position - self.finish_line_position

        # Check if start line has just crossed the car (disappeared off the bottom)
        if (
            not self.race_started
            and not self.race_finished
            and start_line_screen_y > self.car_screen_y + 20
        ):
            self.passed_start_line = True
            self.race_started = True
            self.start_time = time.time()
            print(f"Race started! Start line crossed car at position: {self.position}")

        # Update timer if race has started but not finished
        elif self.race_started and not self.race_finished:
            self.current_time = time.time() - self.start_time

            # Check if finish line has just crossed the car (disappeared off the bottom)
            if finish_line_screen_y > self.car_screen_y + 20:
                self.race_finished = True
                self.finish_time = time.time()
                finish_time = self.finish_time - self.start_time
                print(f"Race finished! Time: {finish_time:.2f}s")

                # Update best time
                if self.best_time is None or finish_time < self.best_time:
                    self.best_time = finish_time

    def draw(self, surface, car_screen_y):
        # Store car_screen_y for line crossing detection
        self.car_screen_y = car_screen_y

        game_area_height = self.game_height

        # Fill entire game area with sky blue (to avoid any previous draws)
        surface.fill(defaults.SKY_BLUE, (0, 0, defaults.WIDTH, game_area_height))

        # Draw grass background
        pygame.draw.rect(
            surface, defaults.GRASS_GREEN, (0, 0, self.road_left, game_area_height)
        )
        pygame.draw.rect(
            surface,
            defaults.GRASS_GREEN,
            (self.road_right, 0, defaults.WIDTH - self.road_right, game_area_height),
        )

        # Draw road - moving downward with improved tiling
        road_offset = int(self.position % self.road_height)

        # Draw one additional tile above the viewport to avoid gaps
        y_start = road_offset - self.road_height

        # Draw multiple copies of the road to fill the screen
        current_y = y_start
        while current_y < game_area_height:
            surface.blit(self.road_surface, (self.road_left, current_y))
            current_y += self.road_height

        # Draw trees - all trees move downward as position increases
        for x, pos, img in self.trees:
            # Tree appears on screen based on its position relative to world position
            screen_y = self.position - pos

            # Only draw if on screen
            if -img.get_height() < screen_y < game_area_height:
                surface.blit(img, (x, screen_y))

        # Draw start and finish lines as checkerboards
        start_y = self.position - self.start_line_position
        if -world_config.start_line_height < start_y < game_area_height:
            surface.blit(self.start_line_surface, (self.road_left, start_y))

            # Add "START" text
            font = pygame.font.SysFont(layout.fonts.default_font, world_config.start_finish_font_size)
            text = font.render("START", True, (255, 255, 255))
            # Add a background to make text more visible
            text_bg = pygame.Surface(
                (text.get_width() + 2*world_config.text_bg_padding, 
                 text.get_height() + 2*world_config.text_bg_padding)
            )
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(world_config.text_bg_alpha)  # Semi-transparent
            surface.blit(
                text_bg,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2 - world_config.text_bg_padding,
                    start_y - world_config.text_y_offset - world_config.text_bg_padding,
                ),
            )
            surface.blit(
                text,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2,
                    start_y - world_config.text_y_offset,
                ),
            )

        # Finish line screen position
        finish_y = self.position - self.finish_line_position
        if -world_config.finish_line_height < finish_y < game_area_height:
            surface.blit(self.finish_line_surface, (self.road_left, finish_y))

            # Add "FINISH" text
            font = pygame.font.SysFont(layout.fonts.default_font, world_config.start_finish_font_size)
            text = font.render("FINISH", True, (255, 255, 255))
            # Add a background to make text more visible
            text_bg = pygame.Surface(
                (text.get_width() + 2*world_config.text_bg_padding, 
                 text.get_height() + 2*world_config.text_bg_padding)
            )
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(world_config.text_bg_alpha)  # Semi-transparent
            surface.blit(
                text_bg,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2 - world_config.text_bg_padding,
                    finish_y - world_config.text_y_offset - world_config.text_bg_padding,
                ),
            )
            surface.blit(
                text,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2,
                    finish_y - world_config.text_y_offset,
                ),
            )

    def draw_timer(self, surface):
        # Draw race information at the top of the screen
        font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.title_size)

        # Draw current time or final time
        if self.race_finished:
            finish_time = self.finish_time - self.start_time
            time_text = f"Time: {finish_time:.2f}s"
            time_color = layout.fonts.highlight_color if finish_time == self.best_time else layout.fonts.normal_color
        elif self.race_started:
            time_text = f"Time: {self.current_time:.2f}s"
            time_color = layout.fonts.normal_color
        elif self.passed_start_line:
            time_text = "Starting race..."
            time_color = layout.fonts.info_color
        else:
            time_text = "Ready to start"
            time_color = layout.fonts.info_color

        time_surface = font.render(time_text, True, time_color)
        surface.blit(
            time_surface, (defaults.WIDTH // 2 - time_surface.get_width() // 2, layout.timer_y)
        )

        # Draw best time if available
        if self.best_time is not None:
            best_text = f"Best: {self.best_time:.2f}s"
            best_surface = font.render(best_text, True, layout.fonts.normal_color)
            surface.blit(
                best_surface, (defaults.WIDTH - best_surface.get_width() - layout.best_time_x_padding, layout.best_time_y)
            )

        # Draw race status indicators
        indicator_y = layout.indicator_y
        indicator_radius = layout.indicator_radius
        padding = layout.indicator_padding
        x_offset = layout.indicator_x_offset

        # Start indicator
        pygame.draw.circle(
            surface,
            (200, 200, 100)
            if self.passed_start_line and not self.race_started
            else (defaults.START_LINE_COLOR if self.race_started else (200, 200, 200)),
            (defaults.WIDTH // 2 - x_offset, indicator_y),
            indicator_radius,
        )

        status_font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.small_size)
        start_text = status_font.render("Start", True, layout.fonts.normal_color)
        surface.blit(
            start_text,
            (defaults.WIDTH // 2 - x_offset + indicator_radius + padding, 
             indicator_y - layout.indicator_radius),
        )

        # Finish indicator
        pygame.draw.circle(
            surface,
            defaults.FINISH_LINE_COLOR if self.race_finished else (200, 200, 200),
            (defaults.WIDTH // 2 + x_offset, indicator_y),
            indicator_radius,
        )

        finish_text = status_font.render("Finish", True, layout.fonts.normal_color)
        surface.blit(
            finish_text,
            (defaults.WIDTH // 2 + x_offset + indicator_radius + padding, 
             indicator_y - layout.indicator_radius),
        )

    def create_checkerboard(
        self, width, height, size=None, colors=((255, 255, 255), (0, 0, 0))
    ):
        """Create a checkerboard pattern surface."""
        if size is None:
            size = world_config.checkerboard_size
            
        # Create a surface for the checkerboard
        surface = pygame.Surface((width, height))
        surface.fill(colors[0])  # Fill with first color as background

        # Calculate number of squares
        cols = width // size + 1
        rows = height // size + 1

        # Draw the checkerboard pattern
        for row in range(rows):
            for col in range(cols):
                # Alternate colors
                if (row + col) % 2 == 1:
                    pygame.draw.rect(
                        surface, colors[1], (col * size, row * size, size, size)
                    )

        return surface
