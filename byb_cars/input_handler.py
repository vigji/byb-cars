from typing import Optional
import numpy as np
import threading
import serial
import time


class ArduinoEMGHandler:
    """Handler for Arduino EMG shield serial communication"""

    def __init__(self, port="/dev/ttyACM0", baud_rate=230400):
        self.port = port
        self.baud_rate = baud_rate
        self.serial = None
        self.running = False
        self.thread = None
        self.num_channels = 1
        self.latest_values = [0.0] * self.num_channels
        self.lock = threading.Lock()

        # Constants from Arduino firmware
        self.START_ESCAPE_SEQ = bytes([255, 255, 1, 1, 128, 255])
        self.END_ESCAPE_SEQ = bytes([255, 255, 1, 1, 129, 255])

    def connect(self):
        """Connect to the Arduino device"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
            )
            if not self.serial.is_open:
                self.serial.open()
            # Flush input buffer
            self.serial.reset_input_buffer()
            # Query board type to ensure communication
            self.send_command("b:1")
            return True
        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            return False

    def disconnect(self):
        """Disconnect from the Arduino device"""
        self.stop_reading()
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.serial = None

    def send_command(self, cmd):
        """Send a command to the Arduino"""
        if not self.serial or not self.serial.is_open:
            return False

        # Commands end with newline
        if not cmd.endswith("\n"):
            cmd += "\n"

        try:
            self.serial.write(cmd.encode("ascii"))
            return True
        except Exception as e:
            print(f"Failed to send command: {e}")
            return False

    def set_channels(self, num_channels):
        """Set the number of channels to read"""
        if 1 <= num_channels <= 6:
            self.num_channels = num_channels
            with self.lock:
                self.latest_values = [0.0] * self.num_channels
            return self.send_command(f"c:{num_channels}")
        return False

    def get_latest_value(self, channel=0):
        """Get the latest value from the specified channel"""
        with self.lock:
            if 0 <= channel < len(self.latest_values):
                return self.latest_values[channel]
            return 0.0

    def _read_thread(self):
        """Thread function to continuously read data"""
        buffer = bytearray()

        while self.running:
            try:
                if self.serial.in_waiting > 0:
                    data = self.serial.read(self.serial.in_waiting)
                    buffer.extend(data)

                    # Process buffer for complete frames
                    while len(buffer) >= 2 * self.num_channels:
                        # Check if we have a start-of-frame marker (first bit of first byte is 1)
                        if buffer[0] & 0x80:
                            # We have a complete frame
                            frame_values = []

                            for i in range(self.num_channels):
                                if len(buffer) < 2 * (i + 1):
                                    break

                                # Extract the 15-bit ADC value
                                # First 7 bits from first byte and 8 bits from second byte
                                high_byte = (
                                    buffer[2 * i] & 0x7F
                                )  # Remove start bit flag
                                low_byte = buffer[2 * i + 1] & 0x7F
                                value = (high_byte << 7) | low_byte

                                # Normalize value to 0.0-1.0 range (Arduino ADC is 10-bit: 0-1023)
                                normalized_value = value / 1023.0
                                frame_values.append(normalized_value)

                            if len(frame_values) == self.num_channels:
                                # Store the latest values
                                with self.lock:
                                    self.latest_values = frame_values

                                # Remove the processed frame from buffer
                                buffer = buffer[2 * self.num_channels :]
                            else:
                                # Incomplete frame, try again later
                                break
                        else:
                            # Not at start of frame, remove first byte and try again
                            buffer.pop(0)

                # Check for response messages (escape sequences)
                start_index = self._find_subsequence(buffer, self.START_ESCAPE_SEQ)
                if start_index >= 0:
                    end_index = self._find_subsequence(buffer, self.END_ESCAPE_SEQ)
                    if end_index > start_index:
                        # Extract the message
                        message = buffer[
                            start_index + len(self.START_ESCAPE_SEQ) : end_index
                        ]
                        # Remove the processed message from buffer
                        buffer = buffer[end_index + len(self.END_ESCAPE_SEQ) :]

                time.sleep(0.001)  # Small delay to prevent CPU hogging

            except Exception as e:
                print(f"Error reading data: {e}")
                time.sleep(0.1)  # Longer delay after error

    def _find_subsequence(self, sequence, subsequence):
        """Find a subsequence in a sequence"""
        if not subsequence or len(subsequence) > len(sequence):
            return -1

        for i in range(len(sequence) - len(subsequence) + 1):
            if sequence[i : i + len(subsequence)] == subsequence:
                return i
        return -1

    def start_reading(self):
        """Start reading data in a separate thread"""
        if self.running:
            return False

        if not self.serial or not self.serial.is_open:
            if not self.connect():
                return False

        self.running = True
        self.thread = threading.Thread(target=self._read_thread, daemon=True)
        self.thread.start()
        return True

    def stop_reading(self):
        """Stop reading data"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None


class InputHandler:
    def __init__(self, demo_mode: bool = True, port: Optional[str] = None):
        self.demo_mode = demo_mode
        self.port = port
        self.emg_handler = None
        self.key_pressed = False

        if not demo_mode and port:
            self._setup_arduino()

    def _setup_arduino(self):
        try:
            self.emg_handler = ArduinoEMGHandler(port=self.port)
            if not self.emg_handler.connect():
                raise RuntimeError(f"Failed to connect to Arduino on port {self.port}")

            # Start reading data
            self.emg_handler.start_reading()

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
            # Read from Arduino EMG handler
            if not self.emg_handler:
                raise RuntimeError("Arduino not initialized")
            # Get the latest value from channel 0
            return self.emg_handler.get_latest_value(0)

    def __del__(self):
        if self.emg_handler:
            self.emg_handler.disconnect()
