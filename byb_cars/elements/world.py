import pygame
import random
import time
from byb_cars import defaults
from byb_cars.elements.handle_assets import get_tree_imgs


# World manages all game world elements including road, trees, and race lines
class GameWorld:
    def __init__(self, baseline_speed=3.0, game_height=600):
        self.baseline_speed = baseline_speed
        self.game_height = game_height

        # Track distance calculation - increased for more stable experience
        self.target_time = 10.0  # 10 seconds to finish at baseline speed
        fps = 60
        self.track_distance = int(self.baseline_speed * fps * self.target_time)

        # Road dimensions
        self.road_width = defaults.WIDTH // 3
        self.road_left = (defaults.WIDTH - self.road_width) // 2
        self.road_right = self.road_left + self.road_width

        # Create the road texture
        self.road_surface = self.create_road()
        self.road_height = self.road_surface.get_height()

        # Start and finish line positions - positive = distance from start
        self.start_line_position = 500
        self.finish_line_position = self.start_line_position + self.track_distance

        self.tree_imgs = get_tree_imgs()

        # Create trees
        self.trees = self.generate_trees(120)  # More trees for longer track

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
        self.start_line_height = 30
        self.finish_line_height = 30
        self.start_line_surface = self.create_checkerboard(
            self.road_width, self.start_line_height
        )
        self.finish_line_surface = self.create_checkerboard(
            self.road_width, self.finish_line_height, size=15
        )  # Smaller squares

        print(
            f"Track setup: Start at {self.start_line_position}, Finish at {self.finish_line_position}"
        )

    def create_road(self):
        # Create road texture with markings
        tile_size = 100  # Size of each road tile
        num_tiles = 10  # Increased number of tiles for more coverage

        surface = pygame.Surface((self.road_width, tile_size * num_tiles))
        surface.fill(defaults.ROAD_GRAY)

        # Draw center line (dashed)
        dash_length = 40
        gap_length = 20
        line_width = 8
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
        pygame.draw.rect(surface, defaults.LINE_WHITE, (5, 0, 3, surface.get_height()))
        pygame.draw.rect(
            surface,
            defaults.LINE_WHITE,
            (self.road_width - 8, 0, 3, surface.get_height()),
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
                x = random.randint(50, self.road_left - 50)
            else:
                # Right side
                x = random.randint(self.road_right + 10, defaults.WIDTH - 50)

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
        if -self.start_line_height < start_y < game_area_height:
            surface.blit(self.start_line_surface, (self.road_left, start_y))

            # Add "START" text
            font = pygame.font.SysFont(None, 36)
            text = font.render("START", True, (255, 255, 255))
            # Add a background to make text more visible
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 10))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)  # Semi-transparent
            surface.blit(
                text_bg,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2 - 5,
                    start_y - 45,
                ),
            )
            surface.blit(
                text,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2,
                    start_y - 40,
                ),
            )

        # Finish line screen position
        finish_y = self.position - self.finish_line_position
        if -self.finish_line_height < finish_y < game_area_height:
            surface.blit(self.finish_line_surface, (self.road_left, finish_y))

            # Add "FINISH" text
            font = pygame.font.SysFont(None, 36)
            text = font.render("FINISH", True, (255, 255, 255))
            # Add a background to make text more visible
            text_bg = pygame.Surface((text.get_width() + 10, text.get_height() + 10))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(180)  # Semi-transparent
            surface.blit(
                text_bg,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2 - 5,
                    finish_y - 45,
                ),
            )
            surface.blit(
                text,
                (
                    self.road_left + self.road_width / 2 - text.get_width() / 2,
                    finish_y - 40,
                ),
            )

    def draw_timer(self, surface):
        # Draw race information at the top of the screen
        font = pygame.font.SysFont(None, 36)

        # Draw current time or final time
        if self.race_finished:
            finish_time = self.finish_time - self.start_time
            time_text = f"Time: {finish_time:.2f}s"
            time_color = (0, 200, 0) if finish_time == self.best_time else (0, 0, 0)
        elif self.race_started:
            time_text = f"Time: {self.current_time:.2f}s"
            time_color = (0, 0, 0)
        elif self.passed_start_line:
            time_text = "Starting race..."
            time_color = (0, 0, 200)
        else:
            time_text = "Ready to start"
            time_color = (0, 0, 200)

        time_surface = font.render(time_text, True, time_color)
        surface.blit(
            time_surface, (defaults.WIDTH // 2 - time_surface.get_width() // 2, 20)
        )

        # Draw best time if available
        if self.best_time is not None:
            best_text = f"Best: {self.best_time:.2f}s"
            best_surface = font.render(best_text, True, (0, 0, 0))
            surface.blit(
                best_surface, (defaults.WIDTH - best_surface.get_width() - 20, 20)
            )

        # Draw race status indicators
        indicator_y = 60
        indicator_radius = 8
        padding = 10

        # Start indicator
        pygame.draw.circle(
            surface,
            (200, 200, 100)
            if self.passed_start_line and not self.race_started
            else (defaults.START_LINE_COLOR if self.race_started else (200, 200, 200)),
            (defaults.WIDTH // 2 - 50, indicator_y),
            indicator_radius,
        )

        status_font = pygame.font.SysFont(None, 24)
        start_text = status_font.render("Start", True, (0, 0, 0))
        surface.blit(
            start_text,
            (defaults.WIDTH // 2 - 50 + indicator_radius + padding, indicator_y - 10),
        )

        # Finish indicator
        pygame.draw.circle(
            surface,
            defaults.FINISH_LINE_COLOR if self.race_finished else (200, 200, 200),
            (defaults.WIDTH // 2 + 50, indicator_y),
            indicator_radius,
        )

        finish_text = status_font.render("Finish", True, (0, 0, 0))
        surface.blit(
            finish_text,
            (defaults.WIDTH // 2 + 50 + indicator_radius + padding, indicator_y - 10),
        )

    def create_checkerboard(
        self, width, height, size=20, colors=((255, 255, 255), (0, 0, 0))
    ):
        """Create a checkerboard pattern surface."""
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
