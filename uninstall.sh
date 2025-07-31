#!/bin/bash
set -e

echo "Uninstalling Prosody..."

# Stop and disable systemd service if it exists
if command -v systemctl &> /dev/null && [ -n "$XDG_RUNTIME_DIR" ]; then
    if systemctl --user is-enabled prosody &> /dev/null; then
        echo "Disabling auto-start..."
        systemctl --user disable prosody
    fi
    
    if systemctl --user is-active prosody &> /dev/null; then
        echo "Stopping Prosody service..."
        systemctl --user stop prosody
    fi
    
    # Remove service file
    if [ -f ~/.config/systemd/user/prosody.service ]; then
        echo "Removing systemd service..."
        rm -f ~/.config/systemd/user/prosody.service
        systemctl --user daemon-reload
    fi
fi

# Get the installation directory from the prosody wrapper before removing it
INSTALL_DIR=""
if [ -f ~/.local/bin/prosody ]; then
    INSTALL_DIR=$(grep "^cd " ~/.local/bin/prosody | cut -d' ' -f2)
fi

# Remove prosody command from ~/.local/bin
if [ -f ~/.local/bin/prosody ]; then
    echo "Removing prosody command..."
    rm -f ~/.local/bin/prosody
fi

# Show note about installation directory if we found it
if [ -n "$INSTALL_DIR" ] && [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "Note: Prosody was installed from $INSTALL_DIR"
    echo "You may want to remove that directory if no longer needed:"
    echo "  rm -rf $INSTALL_DIR"
fi

echo ""
echo "✅ Prosody has been uninstalled."
echo ""
echo "Note: This uninstaller does not remove:"
echo "  - The original source/installation directory"
echo "  - Python packages installed in your system"
echo "  - The Whisper model cache (~140MB in ~/.cache/whisper)"
echo ""
echo "To remove the Whisper model cache:"
echo "  rm -rf ~/.cache/whisper"