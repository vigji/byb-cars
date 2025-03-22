#!/usr/bin/env python3
import argparse
import sys
import os
import importlib.util

def find_module(module_name, search_dirs=None):
    """Find a module file in the given directories"""
    if search_dirs is None:
        search_dirs = ['.', './byb_cars']
    
    for search_dir in search_dirs:
        module_path = os.path.join(search_dir, f"{module_name}.py")
        if os.path.exists(module_path):
            return module_path
    return None

def import_module_from_path(module_name, module_path):
    """Import a module from its file path"""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Simple Street - EMG controlled racing game")
    parser.add_argument("--demo", action="store_true", 
                        help="Run in demo mode with keyboard control instead of EMG")
    parser.add_argument("--port", type=str, default=None,
                        help="Serial port for Arduino (e.g., COM3 on Windows, /dev/ttyACM0 on Linux)")
    args = parser.parse_args()
    
    # Find and import required modules
    game_path = find_module("game")
    input_handler_path = find_module("input_handler")
    
    if not game_path:
        print("Error: Could not find game.py")
        sys.exit(1)
    if not input_handler_path:
        print("Error: Could not find input_handler.py")
        sys.exit(1)
    
    print(f"Found game module at: {game_path}")
    print(f"Found input_handler module at: {input_handler_path}")
    
    # Import the modules
    try:
        import pygame
    except ImportError:
        print("Error: pygame is not installed. Please install it with:")
        print("pip install pygame")
        sys.exit(1)
    
    game_module = import_module_from_path("game", game_path)
    input_handler_module = import_module_from_path("input_handler", input_handler_path)
    
    # Determine if we're running in demo mode
    demo_mode = True if args.demo else (args.port is None)
    
    # Initialize pygame
    pygame.init()
    
    print(f"Running in {'demo' if demo_mode else 'Arduino'} mode")
    if not demo_mode:
        print(f"Using port: {args.port}")
    
    # Create input handler with either demo mode or Arduino port
    input_handler = input_handler_module.InputHandler(demo_mode=demo_mode, port=args.port)
    
    # Create and run the game
    game = game_module.Game(input_handler)
    game.run()
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 