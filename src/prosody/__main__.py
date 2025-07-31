"""Allow running prosody as a module with python -m prosody."""

import os

# Set development mode when running with python -m prosody
os.environ['PROSODY_DEV'] = '1'

from .main import main

if __name__ == "__main__":
    main()
