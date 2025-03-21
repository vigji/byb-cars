from pathlib import Path
from typing import Optional
import json
import time
from datetime import datetime

import numpy as np
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent
import pyqtgraph as pg

from .input_handler import InputHandler
from .game_world import GameWorld

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BYB Cars")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize game state
        self.game_world = GameWorld()
        self.input_handler = InputHandler()
        self.current_time = 0.0
        self.best_time = None
        self.rankings_file = Path.home() / ".byb_cars_rankings.json"
        self.rankings = self._load_rankings()
        self.game_state = "idle"  # idle, running, finished
        
        # Setup UI
        self._setup_ui()
        
        # Setup timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self._update_game)
        self.game_timer.start(16)  # ~60 FPS
        
        # Signal processing
        self.signal_buffer = np.zeros(1000)
        self.signal_integral = 0.0
        self.signal_decay = 0.95  # Decay factor for signal integral
        
        # Enable key tracking
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Space:
            self.input_handler.set_key_state(True)
            
    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release events."""
        if event.key() == Qt.Key.Key_Space:
            self.input_handler.set_key_state(False)
            
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Top bar with time and controls
        top_bar = QHBoxLayout()
        self.time_label = QLabel("Time: 0.00s")
        self.best_time_label = QLabel("Best: --")
        self.control_label = QLabel("Press SPACE to control the car")
        top_bar.addWidget(self.time_label)
        top_bar.addWidget(self.best_time_label)
        top_bar.addWidget(self.control_label)
        layout.addLayout(top_bar)
        
        # Signal plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setTitle("EMG Signal")
        self.plot_widget.setLabel("left", "Amplitude")
        self.plot_widget.setLabel("bottom", "Time")
        self.signal_curve = self.plot_widget.plot(pen="b")
        layout.addWidget(self.plot_widget)
        
        # Game world view
        self.game_view = pg.PlotWidget()
        self.game_view.setBackground("w")
        self.game_view.setTitle("Game World")
        self.game_view.setAspectLocked(True)
        layout.addWidget(self.game_view)
        
        # Start button
        self.start_button = QPushButton("Start Game")
        self.start_button.clicked.connect(self._start_game)
        layout.addWidget(self.start_button)
        
    def _load_rankings(self) -> dict:
        if self.rankings_file.exists():
            with open(self.rankings_file) as f:
                return json.load(f)
        return {}
        
    def _save_rankings(self):
        with open(self.rankings_file, "w") as f:
            json.dump(self.rankings, f)
            
    def _start_game(self):
        # Create a non-blocking input dialog
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Player Name")
        dialog.setLabelText("Enter your name:")
        dialog.setModal(False)  # Make it non-modal
        dialog.accepted.connect(lambda: self._handle_name_input(dialog.textValue()))
        dialog.show()
        
    def _handle_name_input(self, name: str):
        if name:
            self.player_name = name
            self.current_time = 0.0
            self.game_world.reset()
            self.start_button.setEnabled(False)
            self.game_state = "running"
            self.signal_integral = 0.0  # Reset signal integral
            
    def _update_game(self):
        if self.game_state != "running":
            return
            
        # Update signal
        signal_value = self.input_handler.get_value()
        self.signal_buffer = np.roll(self.signal_buffer, -1)
        self.signal_buffer[-1] = signal_value
        
        # Update signal integral with decay
        self.signal_integral = self.signal_integral * self.signal_decay + signal_value
        
        # Update plot
        self.signal_curve.setData(self.signal_buffer)
        
        # Update game world
        self.game_world.update(self.signal_integral)
        self.game_world.draw(self.game_view)
        
        # Update time
        self.current_time += 0.016  # ~60 FPS
        self.time_label.setText(f"Time: {self.current_time:.2f}s")
        
        # Check for lap completion
        if self.game_world.check_lap_complete():
            self._handle_lap_complete()
            
    def _handle_lap_complete(self):
        self.game_state = "finished"
        
        if self.player_name not in self.rankings or self.current_time < self.rankings[self.player_name]:
            self.rankings[self.player_name] = self.current_time
            self._save_rankings()
            self.best_time_label.setText(f"Best: {self.current_time:.2f}s")
            
        # Create a non-blocking message box
        msg = QMessageBox(self)
        msg.setWindowTitle("Lap Complete!")
        msg.setText(f"Time: {self.current_time:.2f}s")
        msg.setModal(False)  # Make it non-modal
        msg.accepted.connect(self._reset_game)
        msg.show()
        
    def _reset_game(self):
        self.game_state = "idle"
        self.start_button.setEnabled(True)
        self.signal_integral = 0.0  # Reset signal integral

def main():
    app = QApplication([])
    window = GameWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main() 