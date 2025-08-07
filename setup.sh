#!/bin/bash

# Simple setup script for Prosody - runs from source
set -e

PROSODY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up Prosody..."

# Create virtual environment if it doesn't exist
if [ ! -d "$PROSODY_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROSODY_DIR/venv"
fi

# Install dependencies
echo "Installing dependencies..."
"$PROSODY_DIR/venv/bin/pip" install -q -r "$PROSODY_DIR/requirements.txt"
"$PROSODY_DIR/venv/bin/pip" install -q -e "$PROSODY_DIR"

# Set up systemd service for auto-start on login
echo "Setting up systemd service..."
mkdir -p ~/.config/systemd/user/

# Create systemd service file
cat > ~/.config/systemd/user/prosody.service << EOF
[Unit]
Description=Prosody Speech-to-Text Service
After=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$PROSODY_DIR
ExecStart=$PROSODY_DIR/venv/bin/python -m prosody
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable prosody.service

echo ""
echo "✅ Prosody setup complete!"
echo ""
echo "To start Prosody now:"
echo "  systemctl --user start prosody"
echo ""
echo "Prosody will automatically start on your next login."
echo ""
echo "To check status:"
echo "  systemctl --user status prosody"
echo ""
echo "To stop:"
echo "  systemctl --user stop prosody"
echo ""
echo "To disable auto-start:"
echo "  systemctl --user disable prosody"