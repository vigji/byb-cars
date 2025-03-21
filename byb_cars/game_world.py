from typing import List, Tuple
import numpy as np
import pyqtgraph as pg

class GameWorld:
    def __init__(self):
        self.car_position = np.array([0.0, 0.0])
        self.car_angle = 0.0
        self.track_points = self._generate_track()
        self.start_line = self.track_points[0]
        self.finish_line = self.track_points[-1]
        self.lap_started = False
        
    def _generate_track(self) -> List[Tuple[float, float]]:
        # Generate a simple oval track
        t = np.linspace(0, 2 * np.pi, 100)
        x = 3 * np.cos(t)
        y = 2 * np.sin(t)
        return list(zip(x, y))
        
    def reset(self):
        self.car_position = np.array([0.0, 0.0])
        self.car_angle = 0.0
        self.lap_started = False
        
    def update(self, signal_integral: float):
        # Convert signal integral to movement
        speed = 0.1 * signal_integral
        direction = np.array([np.cos(self.car_angle), np.sin(self.car_angle)])
        self.car_position += speed * direction
        
    def check_lap_complete(self) -> bool:
        # Check if car crossed the finish line
        if not self.lap_started:
            # Check if car crossed start line
            if np.linalg.norm(self.car_position - self.start_line) < 0.5:
                self.lap_started = True
                return False
        else:
            # Check if car crossed finish line
            if np.linalg.norm(self.car_position - self.finish_line) < 0.5:
                self.lap_started = False
                return True
        return False
        
    def draw(self, plot_widget: pg.PlotWidget):
        # Clear previous plot
        plot_widget.clear()
        
        # Draw track
        track_x, track_y = zip(*self.track_points)
        plot_widget.plot(track_x, track_y, pen="k")
        
        # Draw car
        car_size = 0.2
        car_points = np.array([
            [-car_size, -car_size],
            [car_size, -car_size],
            [car_size, car_size],
            [-car_size, car_size],
        ])
        
        # Rotate and translate car points
        rotation_matrix = np.array([
            [np.cos(self.car_angle), -np.sin(self.car_angle)],
            [np.sin(self.car_angle), np.cos(self.car_angle)],
        ])
        car_points = car_points @ rotation_matrix.T + self.car_position
        
        # Draw car
        car_x, car_y = zip(*car_points)
        plot_widget.plot(car_x, car_y, pen="r", fillLevel=0, brush="r")
        
        # Set plot limits
        plot_widget.setXRange(-4, 4)
        plot_widget.setYRange(-3, 3) 