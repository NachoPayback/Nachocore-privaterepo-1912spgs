#!/usr/bin/env python3
import os
import sys

# Ensure the project root is in sys.path.
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(current_dir, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import main() from game_ui using package syntax (game/__init__.py must exist).
from game.game_ui import main

if __name__ == "__main__":
    main()
