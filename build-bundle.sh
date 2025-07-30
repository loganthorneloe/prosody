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

# Create the launcher script that uses bundled Python
cat > "$BUNDLE_DIR/opt/prosody/launcher" << 'EOF'
#!/bin/bash
# Launcher for bundled Prosody
exec /opt/prosody/venv/bin/python -m prosody "$@"
EOF
chmod +x "$BUNDLE_DIR/opt/prosody/launcher"

# Update the wrapper scripts to use the bundled version
cat > debian/prosody-wrapper << 'EOF'
#!/bin/bash
# Wrapper that uses bundled Prosody
exec /opt/prosody/launcher "$@"
EOF

cat > prosody-launcher << 'EOF'
#!/bin/bash
# GUI launcher for bundled Prosody

LOG_FILE="$HOME/.config/prosody/prosody.log"
mkdir -p "$HOME/.config/prosody"

# Redirect output to log file
exec >> "$LOG_FILE" 2>&1

# Enable systemd service for auto-start
systemctl --user daemon-reload 2>/dev/null || true
systemctl --user enable prosody.service 2>/dev/null || true

# Run bundled Prosody
exec /opt/prosody/launcher "$@"
EOF
chmod +x prosody-launcher

echo "Bundle created! The package will now include all dependencies."
echo "Package size will be ~2GB but completely self-contained."