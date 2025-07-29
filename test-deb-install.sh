#!/bin/bash
# Test script for Debian package installation

set -e

echo "=== Testing Prosody Debian Package ==="
echo

# Check for existing installations
echo "Checking for existing installations..."
if command -v prosody &> /dev/null; then
    echo "WARNING: prosody is already installed at: $(which prosody)"
    echo "This may be from:"
    echo "  - pip install (check with: pip show prosody-stt)"
    echo "  - previous apt install (check with: dpkg -l | grep prosody)"
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. To remove existing installations:"
        echo "  pip: pip uninstall prosody-stt"
        echo "  apt: sudo apt remove prosody-stt"
        exit 1
    fi
fi
echo

# 1. Build the package
echo "1. Building the .deb package..."
./build-deb.sh

# 2. Show package info
echo
echo "2. Package information:"
dpkg-deb -I dist/*.deb

# 3. List package contents
echo
echo "3. Package contents:"
dpkg-deb -c dist/*.deb

# 4. Install the package
echo
echo "4. Installing the package (requires sudo)..."
sudo dpkg -i dist/*.deb || true
sudo apt-get install -f -y  # Fix any dependency issues

# 5. Verify installation
echo
echo "5. Verifying installation:"
which prosody
dpkg -l | grep prosody-stt

# 6. Test the command
echo
echo "6. Testing prosody command:"
prosody --help || echo "Note: First run will download Whisper model"

# 7. Check systemd service
echo
echo "7. Checking systemd service:"
systemctl --user status prosody || true

echo
echo "=== Test complete! ==="
echo
echo "To uninstall: sudo apt remove prosody-stt"
echo "To enable auto-start: systemctl --user enable prosody"