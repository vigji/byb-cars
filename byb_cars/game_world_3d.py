from typing import List, Tuple
import numpy as np
from pathlib import Path
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

class GameWorld3D:
    def __init__(self, main_window):
        self.main_window = main_window
        
        # Initialize Ursina
        self.app = Ursina()
        
        # Game state
        self.car_speed = 0.0
        self.max_speed = 20
        self.lap_started = False
        self.current_time = 0.0
        self.game_started = False
        
        # Create track
        self._create_track()
        
        # Create car
        self._create_car()
        
        # Create environment
        self._create_environment()
        
        # Create UI
        self._create_ui()
        
        # Setup camera
        camera.position = (0, 15, -25)  # Moved camera higher and further back
        camera.rotation = (25, 0, 0)     # Adjusted angle for better view
        
        # Add start message
        self.start_text = Text(
            text='Press SPACE to start',
            position=(0, 0),
            scale=3,
            color=color.white
        )
        
    def _create_track(self):
        # Create a simple race track using a curved plane
        self.track = Entity(
            model='plane',
            scale=(20, 1, 20),
            color=color.gray,
            texture='white_cube',
            texture_scale=(20, 20),
            collider='box',
            scale_x=20,
            scale_z=20
        )
        
        # Create track boundaries
        self.track_lines = Entity(
            model='quad',
            scale=(20, 1, 20),
            color=color.white,
            alpha=0.5
        )
        
        # Create start/finish line
        self.start_line = Entity(
            model='quad',
            position=(0, 0.1, 0),
            scale=(2, 1, 0.5),
            color=color.green
        )
        
        self.finish_line = Entity(
            model='quad',
            position=(0, 0.1, 10),
            scale=(2, 1, 0.5),
            color=color.red
        )
        
    def _create_car(self):
        # Load the car model
        model_path = Path(__file__).parent / 'assets' / 'models' / 'car.glb'
        
        if not model_path.exists():
            print("Warning: Car model not found. Using basic car model.")
            self._create_basic_car()
            return
            
        # Create the car with the 3D model
        self.car = Entity(
            model=str(model_path),
            scale=(0.3, 0.3, 0.3),  # Reduced scale to make it smaller
            position=(0, 0.5, 0),   # Raised slightly above ground
            rotation=(0, 90, 0),    # Rotated 90 degrees to face forward
            collider='box',
            scale_x=2,
            scale_y=1,
            scale_z=4
        )
        
        # Add a shadow under the car
        self.car_shadow = Entity(
            model='quad',
            scale=(2, 1, 4),
            color=color.black,
            alpha=0.3,
            position=(0, 0.01, 0),
            rotation=(90, 0, 0)
        )
        
    def _create_basic_car(self):
        # Fallback to basic car model if 3D model is not available
        self.car = Entity(
            model='cube',
            scale=(2, 1, 4),
            color=color.red,
            position=(0, 0.5, 0),
            collider='box',
            scale_x=2,
            scale_y=1,
            scale_z=4
        )
        
        # Add wheels
        wheel_scale = (0.5, 0.5, 0.5)
        wheel_positions = [
            (-1, 0.5, -1.5),  # Front left
            (1, 0.5, -1.5),   # Front right
            (-1, 0.5, 1.5),   # Back left
            (1, 0.5, 1.5),    # Back right
        ]
        
        self.wheels = []
        for pos in wheel_positions:
            wheel = Entity(
                model='sphere',
                scale=wheel_scale,
                color=color.black,
                position=pos,
                parent=self.car
            )
            self.wheels.append(wheel)
            
        # Add headlights
        headlight_positions = [
            (0, 0.5, -2),  # Front
            (0, 0.5, 2),   # Back
        ]
        
        self.headlights = []
        for pos in headlight_positions:
            headlight = Entity(
                model='sphere',
                scale=(0.2, 0.2, 0.2),
                color=color.yellow,
                position=pos,
                parent=self.car
            )
            self.headlights.append(headlight)
            
    def _create_environment(self):
        # Add sky
        Sky()
        
        # Add ground
        ground = Entity(
            model='plane',
            scale=(100, 1, 100),
            color=color.green,
            texture='white_cube',
            texture_scale=(100, 100),
            collider='box',
            scale_x=100,
            scale_z=100
        )
        
        # Add some trees for reference
        for i in range(10):
            x = random.uniform(-40, 40)
            z = random.uniform(-40, 40)
            tree = Entity(
                model='cube',
                scale=(1, 3, 1),
                color=color.brown,
                position=(x, 1.5, z)
            )
            
    def _create_ui(self):
        # Create timer text
        self.timer_text = Text(
            text='Time: 0.00s',
            position=(-0.85, 0.45),
            scale=2
        )
        
        # Create best time text
        self.best_time_text = Text(
            text='Best: --',
            position=(-0.85, 0.4),
            scale=2
        )
        
        # Create controls text
        self.controls_text = Text(
            text='Use UP/DOWN arrows to control speed',
            position=(-0.85, 0.35),
            scale=1.5
        )
        
    def update(self, signal_integral: float = 0.0):
        # Handle game start
        if not self.game_started:
            if held_keys['space']:
                self.game_started = True
                self.start_text.enabled = False
                self.controls_text.enabled = False
            return
            
        # Update car speed based on signal or keyboard input
        if signal_integral > 0:
            target_speed = signal_integral * 2
        else:
            # Use keyboard input as fallback
            if held_keys['up arrow']:
                target_speed = self.max_speed
            elif held_keys['down arrow']:
                target_speed = -self.max_speed / 2
            else:
                target_speed = 0
                
        self.car_speed = min(target_speed, self.max_speed)
        
        # Move car forward
        self.car.z += self.car_speed * time.dt
        
        # Rotate wheels based on speed (only for basic car model)
        if hasattr(self, 'wheels'):
            wheel_rotation = self.car_speed * 100
            for wheel in self.wheels:
                wheel.rotation_y += wheel_rotation * time.dt
            
        # Update timer
        self.current_time += time.dt
        self.timer_text.text = f'Time: {self.current_time:.1f}s'
        
        # Check for lap completion
        if self._check_lap_complete():
            self._handle_lap_complete()
        
    def _check_lap_complete(self) -> bool:
        if not self.lap_started:
            # Check if car crossed start line
            if abs(self.car.z) < 0.5:
                self.lap_started = True
                return False
        else:
            # Check if car crossed finish line
            if abs(self.car.z - 10) < 0.5:
                self.lap_started = False
                return True
        return False
        
    def _handle_lap_complete(self):
        # Show completion message
        Text(
            text=f'Lap Complete! Time: {self.current_time:.1f}s',
            position=(0, 0),
            scale=3,
            color=color.green
        )
        
        # Reset car position
        self.car.z = 0
        
        # Notify main window of lap completion
        if self.main_window:
            self.main_window.handle_lap_complete(self.current_time)
        
    def run(self):
        # Add update function to the app
        self.app.update = self.update
        self.app.run() 