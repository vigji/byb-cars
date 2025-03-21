# BYB Cars

A car racing game controlled by EMG signals from a Backyard Brains shield. The game features a simple oval track where players control a car using their muscle activity. The game keeps track of lap times and maintains a leaderboard of best times.

## Features

- Real-time EMG signal visualization
- Simple oval track with start/finish line
- Lap timing and leaderboard system
- Demo mode for testing without hardware
- Support for Arduino with Backyard Brains shield

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or `pip`

## Installation

### Using uv (Recommended)

1. Install uv if you haven't already:
```bash
# First, remove any existing uv installations
pip uninstall uv -y  # Remove pip-installed uv
rm -f ~/.local/bin/uv  # Remove any local uv installation
rm -f ~/.local/bin/uvx  # Remove any local uvx installation

# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

2. Install the package:
```bash
uv pip install byb-cars
```

### Using pip

```bash
pip install byb-cars
```

## Usage

### Demo Mode (No Hardware Required)

```bash
uv run byb-cars
```

### With Arduino and Backyard Brains Shield

1. Connect your Arduino with the Backyard Brains shield
2. Upload the Firmata firmware to your Arduino
3. Run the game with the Arduino port:

```bash
uv run byb-cars --port /dev/ttyUSB0  # or whatever your Arduino port is
```

## How to Play

1. Enter your name when prompted
2. Click "Start Game"
3. Use your muscle activity (or SPACE key in demo mode) to control the car
4. Complete a lap to record your time
5. Try to beat your best time!

## Development

To set up the development environment:

1. Install uv if you haven't already:
```bash
# First, remove any existing uv installations
pip uninstall uv -y  # Remove pip-installed uv
rm -f ~/.local/bin/uv  # Remove any local uv installation
rm -f ~/.local/bin/uvx  # Remove any local uvx installation

# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/byb-cars.git
cd byb-cars
```

3. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

4. Install development dependencies:
```bash
uv pip install -e .
```

5. Run the game:
```bash
uv run byb-cars
```

## Project Structure

```
byb-cars/
├── byb_cars/
│   ├── __init__.py
│   ├── main.py          # Main game window and logic
│   ├── input_handler.py # Input handling (EMG/Arduino)
│   └── game_world.py    # Game world and car physics
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

## License

MIT License
