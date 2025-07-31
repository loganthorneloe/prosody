#!/bin/bash
set -e

echo "Installing Prosody..."

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# Set up systemd service
echo "Setting up auto-start service..."
# Create systemd directory
mkdir -p ~/.config/systemd/user/ 2>/dev/null || true

# Create user-specific service file
cat > ~/.config/systemd/user/prosody.service << 'EOF'
[Unit]
Description=Prosody Speech-to-Text Service
After=graphical-session.target

[Service]
Type=simple
ExecStart=%h/.local/bin/prosody
Restart=always
RestartSec=10
Environment="DISPLAY=:0"

[Install]
WantedBy=default.target
EOF

# Create prosody wrapper in ~/.local/bin
mkdir -p ~/.local/bin
cat > ~/.local/bin/prosody << EOF
#!/bin/bash
cd $(pwd)
source venv/bin/activate
exec python -m prosody
EOF

chmod +x ~/.local/bin/prosody


# Reload systemd and enable service
systemctl --user daemon-reload
systemctl --user enable prosody

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  WARNING: ~/.local/bin is not in your PATH"
    echo "Add this line to your ~/.bashrc or ~/.profile:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo ""
echo "✅ Prosody installed successfully!"
echo ""
echo "To start Prosody:"
echo "  prosody                        # Run in foreground"
echo "  prosody &                      # Run in background"
echo "  systemctl --user start prosody # Start as service"
echo ""
echo "Auto-start is enabled. Prosody will start on your next login."
echo ""
echo "🎤 How to use:"
echo "  1. Click where you want to type"
echo "  2. Double-tap Left Ctrl to start recording"
echo "  3. Speak naturally"
echo "  4. Double-tap Left Ctrl again to transcribe"
echo ""
echo "Tip: Double-tap Escape to cancel recording"