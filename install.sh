#!/bin/bash
set -e

echo "Installing Prosody..."

# Check if we're in a proper graphical session
if [ -z "$DISPLAY" ]; then
    echo "⚠️  Warning: No DISPLAY detected. Prosody requires a graphical environment."
    echo "   If installing over SSH, the app will only work in a desktop session."
fi

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

# Check if we can write to current directory
if [ ! -w "." ]; then
    echo ""
    echo "⚠️  Permission issue detected!"
    echo ""
    echo "The extracted files are read-only (this is normal for downloaded releases)."
    echo "Please fix permissions first:"
    echo ""
    echo "  chmod -R u+w ."
    echo ""
    echo "Then run ./install.sh again."
    echo ""
    echo "This happens because release tarballs extract with read-only permissions"
    echo "for security. The chmod command makes them writable so we can install."
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
SYSTEMD_SETUP_SUCCESS=false

# Check if systemd directories exist with wrong ownership
if [ -d ~/.config/systemd ] && [ ! -w ~/.config/systemd ]; then
    echo "Warning: ~/.config/systemd exists but is not writable (probably owned by root)"
    echo "To fix this, run:"
    echo "  sudo chown -R $USER:$USER ~/.config/systemd"
    echo ""
elif [ -d ~/.config/systemd/user ] && [ ! -w ~/.config/systemd/user ]; then
    echo "Warning: ~/.config/systemd/user exists but is not writable (probably owned by root)"
    echo "To fix this, run:"
    echo "  sudo chown -R $USER:$USER ~/.config/systemd"
    echo ""
else
    # Try to create systemd directory
    if mkdir -p ~/.config/systemd/user/ 2>/dev/null; then
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
        SYSTEMD_SETUP_SUCCESS=true
    else
        echo "Warning: Cannot create ~/.config/systemd/user/"
        echo "Auto-start setup skipped. To set up manually later:"
        echo "  mkdir -p ~/.config/systemd/user/"
        echo "  cp prosody.service ~/.config/systemd/user/"
        echo "  systemctl --user daemon-reload"
        echo "  systemctl --user enable prosody"
    fi
fi

# Create prosody wrapper in ~/.local/bin
mkdir -p ~/.local/bin
cat > ~/.local/bin/prosody << EOF
#!/bin/bash
cd $(pwd)
source venv/bin/activate
exec python -m prosody
EOF

chmod +x ~/.local/bin/prosody


# Reload systemd and enable service (only if systemd is available AND we created the service file)
if [ "$SYSTEMD_SETUP_SUCCESS" = true ] && command -v systemctl &> /dev/null && [ -n "$XDG_RUNTIME_DIR" ]; then
    systemctl --user daemon-reload
    systemctl --user enable prosody
elif [ "$SYSTEMD_SETUP_SUCCESS" = false ]; then
    echo ""
    echo "Note: systemd service not set up (see warning above)."
else
    echo ""
    echo "Note: systemd not available or not in user session."
    echo "To enable auto-start later, run:"
    echo "  systemctl --user enable prosody"
fi

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
if [ "$SYSTEMD_SETUP_SUCCESS" = true ] && command -v systemctl &> /dev/null && [ -n "$XDG_RUNTIME_DIR" ]; then
    echo "  systemctl --user start prosody # Start as service"
    echo ""
    echo "Auto-start is enabled. Prosody will start on your next login."
else
    echo ""
fi
echo ""
echo "🎤 How to use:"
echo "  1. Click where you want to type"
echo "  2. Double-tap Left Ctrl to start recording"
echo "  3. Speak naturally"
echo "  4. Double-tap Left Ctrl again to transcribe"
echo ""
echo "Tip: Double-tap Escape to cancel recording"