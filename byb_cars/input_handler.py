from typing import Optional
import numpy as np
from pyfirmata import Arduino, INPUT, ANALOG
from pyfirmata.util import Iterator

class InputHandler:
    def __init__(self, demo_mode: bool = True, port: Optional[str] = None):
        self.demo_mode = demo_mode
        self.port = port
        self.board = None
        self.iterator = None
        self.analog_pin = None
        self.key_pressed = False
        
        if not demo_mode and port:
            self._setup_arduino()
            
    def _setup_arduino(self):
        try:
            self.board = Arduino(self.port)
            self.iterator = Iterator(self.board)
            self.iterator.start()
            
            # Setup analog pin for EMG reading
            self.analog_pin = self.board.get_pin("a:0:i")
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Arduino: {e}")
            
    def set_key_state(self, pressed: bool):
        """Update the key press state for demo mode."""
        self.key_pressed = pressed
            
    def get_value(self) -> float:
        if self.demo_mode:
            # In demo mode, return biased random values based on key press
            if self.key_pressed:
                # When key is pressed, generate positive values with higher mean
                return np.random.normal(2.0, 0.5)
            else:
                # When key is not pressed, generate values around zero
                return np.random.normal(0.0, 0.2)
        else:
            # Read from Arduino
            if not self.analog_pin:
                raise RuntimeError("Arduino not initialized")
            return self.analog_pin.read() or 0.0
            
    def __del__(self):
        if self.board:
            self.board.exit() 