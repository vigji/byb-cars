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
        self.car_speed = 0.0
        self.max_speed = 0.5  # Maximum car speed
        
    def _generate_track(self) -> List[Tuple[float, float]]:
        # Generate a more interesting track with straightaways and curves
        t = np.linspace(0, 2 * np.pi, 200)  # More points for smoother track
        # Create a more complex shape with straightaways
        x = np.zeros_like(t)
        y = np.zeros_like(t)
        
        # Create a track with straightaways and curves
        for i in range(len(t)):
            if t[i] < np.pi/2:
                # First curve
                x[i] = 3 * np.cos(t[i])
                y[i] = 2 * np.sin(t[i])
            elif t[i] < np.pi:
                # First straightaway
                x[i] = -3 + (t[i] - np.pi/2) * 2
                y[i] = 2
            elif t[i] < 3*np.pi/2:
                # Second curve
                x[i] = 3 * np.cos(t[i])
                y[i] = 2 * np.sin(t[i])
            else:
                # Second straightaway
                x[i] = 3 - (t[i] - 3*np.pi/2) * 2
                y[i] = -2
                
        return list(zip(x, y))
        
    def reset(self):
        self.car_position = np.array([0.0, 0.0])
        self.car_angle = 0.0
        self.lap_started = False
        self.car_speed = 0.0
        
    def update(self, signal_integral: float):
        # Convert signal integral to speed with limits
        target_speed = 0.1 * signal_integral
        self.car_speed = np.clip(target_speed, 0, self.max_speed)
        
        # Update car position
        direction = np.array([np.cos(self.car_angle), np.sin(self.car_angle)])
        self.car_position += self.car_speed * direction
        
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
        
        # Draw track background (road)
        track_x, track_y = zip(*self.track_points)
        # Draw wider track for road effect
        plot_widget.plot(track_x, track_y, pen=pg.mkPen(color='#666666', width=8))
        # Draw track lines
        plot_widget.plot(track_x, track_y, pen=pg.mkPen(color='white', width=2, style=Qt.DashLine))
        
        # Draw start/finish line
        start_x, start_y = self.start_line
        finish_x, finish_y = self.finish_line
        # Draw start line (green)
        plot_widget.plot([start_x], [start_y], pen=None, symbol="o", symbolBrush="g", symbolSize=15)
        # Draw finish line (red)
        plot_widget.plot([finish_x], [finish_y], pen=None, symbol="o", symbolBrush="r", symbolSize=15)
        
        # Draw car
        car_length = 0.4
        car_width = 0.2
        
        # Car body points (rectangle)
        car_points = np.array([
            [-car_length/2, -car_width/2],
            [car_length/2, -car_width/2],
            [car_length/2, car_width/2],
            [-car_length/2, car_width/2],
        ])
        
        # Wheels
        wheel_radius = car_width/3
        wheel_positions = [
            (-car_length/3, -car_width/2),  # Front left
            (-car_length/3, car_width/2),   # Front right
            (car_length/3, -car_width/2),   # Back left
            (car_length/3, car_width/2),    # Back right
        ]
        
        # Rotate and translate car points
        rotation_matrix = np.array([
            [np.cos(self.car_angle), -np.sin(self.car_angle)],
            [np.sin(self.car_angle), np.cos(self.car_angle)],
        ])
        
        # Draw car body
        car_points_rotated = car_points @ rotation_matrix.T + self.car_position
        car_x, car_y = zip(*car_points_rotated)
        plot_widget.plot(car_x, car_y, pen="k", fillLevel=0, brush="#FF0000")
        
        # Draw wheels
        for wheel_pos in wheel_positions:
            wheel_center = np.array(wheel_pos) @ rotation_matrix.T + self.car_position
            wheel_points = []
            for angle in np.linspace(0, 2*np.pi, 20):
                wheel_points.append(wheel_center + wheel_radius * np.array([
                    np.cos(angle),
                    np.sin(angle)
                ]))
            wheel_x, wheel_y = zip(*wheel_points)
            plot_widget.plot(wheel_x, wheel_y, pen="k", fillLevel=0, brush="#333333")
        
        # Draw headlights
        headlight_positions = [
            (car_length/2, -car_width/3),
            (car_length/2, car_width/3),
        ]
        for headlight_pos in headlight_positions:
            headlight_center = np.array(headlight_pos) @ rotation_matrix.T + self.car_position
            plot_widget.plot([headlight_center[0]], [headlight_center[1]], 
                           pen=None, symbol="o", symbolBrush="yellow", symbolSize=8)
        
        # Set plot limits with some padding
        plot_widget.setXRange(-4, 4)
        plot_widget.setYRange(-3, 3) 