import json
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field, asdict
import pygame
import sys
import time
from byb_cars import defaults
from byb_cars.elements.layout_config import layout

@dataclass
class Score:
    username: str
    time: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class ScoreConfig:
    scores_file: str = "scores.json"
    max_displayed_scores: int = 23

    # Text input
    max_username_length: int = 15
    # input_text_color: tuple = (0, 0, 0)

    #   input_font_size: int = 32
    # highscores_font_size: int = 28
    # highscores_title_font_size: int = 36



class ScoreManager:
    """Manage scores for the game."""
    score_config = ScoreConfig()

    def __init__(self, scores_file="scores.json"):
        # Store scores in the project root directory
        self.scores_path = Path(__file__).parent.parent.parent / scores_file
        self.scores = self.load_scores()
        
    def load_scores(self) -> List[Score]:
        """Load scores from the scores file."""
        try:
            if self.scores_path.exists():
                with open(self.scores_path, 'r') as f:
                    data = json.load(f)
                    scores = [Score(**score) for score in data]
                    print(f"Successfully loaded {len(scores)} scores from {self.scores_path}")
                    return scores
            else:
                print(f"Scores file not found at {self.scores_path}, starting with empty scores")
            return []
        except Exception as e:
            print(f"Error loading scores: {e}")
            return []
    
    def save_scores(self):
        """Save scores to the scores file."""
        try:
            with open(self.scores_path, 'w') as f:
                json.dump([asdict(score) for score in self.scores], f, indent=2)
            print(f"Scores saved to {self.scores_path}")
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, username: str, time_value: float):
        """Add a new score and save to file."""
        self.scores.append(Score(username=username, time=time_value))
        self.save_scores()
        print(f"Added score for {username}: {time_value}")
    
    def get_best_time(self, username: str) -> Optional[float]:
        """Get the best time for a specific user."""
        user_scores = [score.time for score in self.scores if score.username == username]
        return min(user_scores) if user_scores else None
    
    def get_all_scores_sorted(self) -> List[Score]:
        """Get all scores sorted from best to worst."""
        return sorted(self.scores, key=lambda score: score.time)


def get_username(screen, score_config: ScoreConfig = None) -> str:
    """Show a text input dialog to get the username."""
    score_config = score_config if score_config is not None else ScoreConfig()

    input_box = pygame.Rect(
        defaults.WIDTH // 2 - layout.input_box_width // 2,
        defaults.HEIGHT // 2 - layout.input_box_height // 2,
        layout.input_box_width,
        layout.input_box_height
    )
    color_inactive = layout.input_box_color
    color_active = layout.input_box_active_color
    color = color_inactive
    active = True
    text = ""
    font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.subtitle_size)
    prompt_font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.subtitle_size)
    prompt = prompt_font.render("Enter your name:", True, layout.fonts.normal_color)
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((defaults.WIDTH, defaults.HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)  # Semi-transparent
    
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if text:  # Only finish if text is not empty
                            done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        # Only add the character if we haven't reached max length
                        if len(text) < score_config.max_username_length and event.unicode.isprintable():
                            text += event.unicode
        
        # Render the current state
        screen.blit(overlay, (0, 0))
        
        # Render prompt above the input box
        prompt_rect = prompt.get_rect(
            centerx=defaults.WIDTH // 2,
            bottom=input_box.top - layout.input_prompt_padding
        )
        screen.blit(prompt, prompt_rect)
        
        # Render the input box
        pygame.draw.rect(screen, color, input_box, border_radius=5)
        
        # Render the text
        txt_surface = font.render(text, True, layout.fonts.normal_color)
        # Ensure text is centered in the input box
        text_rect = txt_surface.get_rect(center=input_box.center)
        screen.blit(txt_surface, text_rect)
        
        pygame.display.flip()
    
    return text.strip() if text.strip() else "Player"


def show_high_scores(screen, score_manager: ScoreManager):
    """Display the high scores screen."""
    sorted_scores = score_manager.get_all_scores_sorted()
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((defaults.WIDTH, defaults.HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    
    title_font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.title_size)
    score_font = pygame.font.SysFont(layout.fonts.default_font, layout.fonts.normal_size)
    
    # Title
    title = title_font.render("HIGH SCORES", True, layout.fonts.light_color)
    title_rect = title.get_rect(centerx=defaults.WIDTH // 2, top=layout.highscore_title_top)
    
    # Get scores to display
    display_scores = sorted_scores[:10]  # Show top 10 scores
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_h, pygame.K_SPACE):
                    running = False
        
        # Draw overlay
        screen.blit(overlay, (0, 0))
        
        # Draw title
        screen.blit(title, title_rect)
        
        # Draw scores
        if display_scores:
            y_pos = title_rect.bottom + 50
            for i, score in enumerate(display_scores):
                rank_text = f"{i+1}."
                rank_surf = score_font.render(rank_text, True, layout.fonts.light_color)
                
                name_text = f"{score.username}"
                name_surf = score_font.render(name_text, True, layout.fonts.light_color)
                
                time_text = f"{score.time:.2f}s"
                time_surf = score_font.render(time_text, True, layout.fonts.light_color)
                
                # Position the text components
                screen.blit(rank_surf, (defaults.WIDTH // 4 - 20, y_pos))
                screen.blit(name_surf, (defaults.WIDTH // 4 + 30, y_pos))
                screen.blit(time_surf, (defaults.WIDTH * 3 // 4 - 50, y_pos))
                
                y_pos += 40
        else:
            no_scores = score_font.render("No scores yet!", True, layout.fonts.light_color)
            no_scores_rect = no_scores.get_rect(center=(defaults.WIDTH // 2, defaults.HEIGHT // 2))
            screen.blit(no_scores, no_scores_rect)
        
        # Draw instructions
        instruction = score_font.render("Press any key to return", True, layout.fonts.normal_color)
        instruction_rect = instruction.get_rect(centerx=defaults.WIDTH // 2, bottom=defaults.HEIGHT - 50)
        screen.blit(instruction, instruction_rect)
        
        pygame.display.flip()