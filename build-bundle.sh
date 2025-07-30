#!/bin/bash
# Build a self-contained Prosody bundle with all dependencies

set -e

BUNDLE_DIR="debian/prosody-bundle"
VENV_DIR="$BUNDLE_DIR/opt/prosody/venv"

echo "Building self-contained Prosody bundle..."

# Clean previous builds
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/opt/prosody"

# Create a virtual environment in the bundle
python3 -m venv "$VENV_DIR"

# Activate and install all dependencies
source "$VENV_DIR/bin/activate"
pip install --upgrade pip wheel

# Install all dependencies
pip install numpy sounddevice pynput openai-whisper torch torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

# Install prosody itself into the venv
pip install -e .

# Deactivate venv
deactivate

echo "Bundle created! The package will now include all dependencies."
echo "Package size will be ~2GB but completely self-contained."