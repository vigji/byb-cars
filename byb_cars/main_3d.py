from pathlib import Path
import json
import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import QTimer
from pyqtgraph import PlotWidget
from byb_cars.game_world_3d import GameWorld3D
from byb_cars.input_handler import InputHandler

class GameWindow3D(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BYB Cars 3D")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize game state
        self.game_world = None
        self.input_handler = InputHandler()
        self.is_running = False
        self.current_time = 0.0
        self.best_time = float('inf')
        self.rankings = self._load_rankings()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create start button
        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)
        
        # Create name input
        self.name_label = QLabel("Enter your name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        
        # Create signal plot
        self.plot = PlotWidget()
        self.plot.setBackground('w')
        self.plot.setTitle("Input Signal")
        self.plot.setLabel('left', 'Signal')
        self.plot.setLabel('bottom', 'Time (s)')
        layout.addWidget(self.plot)
        
        # Create timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        
    def _load_rankings(self) -> dict:
        """Load rankings from file."""
        rankings_file = Path(__file__).parent / "rankings.json"
        if rankings_file.exists():
            with open(rankings_file, "r") as f:
                return json.load(f)
        return {}
        
    def _save_rankings(self):
        """Save rankings to file."""
        rankings_file = Path(__file__).parent / "rankings.json"
        with open(rankings_file, "w") as f:
            json.dump(self.rankings, f)
            
    def start_game(self):
        """Start a new game."""
        if not self.name_input.text():
            QMessageBox.warning(self, "Error", "Please enter your name first!")
            return
            
        self.is_running = True
        self.current_time = 0.0
        self.start_button.setEnabled(False)
        self.name_input.setEnabled(False)
        
        # Create and start game world
        self.game_world = GameWorld3D(self)
        self.game_world.start()
        
    def handle_lap_complete(self, lap_time: float):
        """Handle lap completion."""
        self.is_running = False
        self.current_time = lap_time
        
        # Update best time
        if lap_time < self.best_time:
            self.best_time = lap_time
            
        # Update rankings
        player_name = self.name_input.text()
        if player_name not in self.rankings or lap_time < self.rankings[player_name]:
            self.rankings[player_name] = lap_time
            self._save_rankings()
            
        # Show completion message
        QMessageBox.information(
            self,
            "Lap Complete!",
            f"Time: {lap_time:.2f}s\nBest time: {self.best_time:.2f}s"
        )
        
        # Reset UI
        self.start_button.setEnabled(True)
        self.name_input.setEnabled(True)
        
        # Clean up game world
        if self.game_world:
            self.game_world.cleanup()
            self.game_world = None
        
    def update(self):
        """Update game state."""
        if not self.is_running or not self.game_world:
            return
            
        # Update input signal
        signal = self.input_handler.get_signal()
        self.plot.clear()
        self.plot.plot(signal)
        
        # Update game world
        self.game_world.update(signal)
        
    def closeEvent(self, event):
        """Handle window close event."""
        if self.game_world:
            self.game_world.cleanup()
        event.accept()
        
def main():
    app = QApplication([])
    window = GameWindow3D()
    window.show()
    app.exec()

if __name__ == "__main__":
    main() 