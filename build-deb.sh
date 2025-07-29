#!/bin/bash
# Build script to create a .deb package for Prosody

set -e

echo "Building Prosody Debian package..."

# Ensure we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: Must run from prosody root directory"
    exit 1
fi

# Install build dependencies if needed
echo "Checking build dependencies..."
if ! command -v dpkg-buildpackage &> /dev/null; then
    echo "Installing build tools..."
    sudo apt update
    sudo apt install -y build-essential debhelper dh-python python3-all python3-setuptools
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/ debian/.debhelper/
rm -f debian/files debian/*.log debian/*.substvars
rm -rf debian/prosody-stt/

# Update version in setup.py to match debian/changelog
VERSION=$(head -n1 debian/changelog | grep -oP '(?<=\().*(?=\))' | cut -d'-' -f1)
sed -i "s/version=\".*\"/version=\"$VERSION\"/" setup.py

# Build the package
echo "Building package..."
dpkg-buildpackage -us -uc -b

# Move the .deb to a predictable location
mkdir -p dist
mv ../prosody-stt*.deb dist/

# Clean up
rm -f ../prosody-stt*.buildinfo ../prosody-stt*.changes

echo ""
echo "Build complete!"
echo "Package created: dist/prosody-stt_${VERSION}-1_all.deb"
echo ""
echo "To install locally:"
echo "  sudo dpkg -i dist/prosody-stt_${VERSION}-1_all.deb"
echo "  sudo apt-get install -f  # To fix any missing dependencies"
echo ""
echo "To upload to GitHub releases:"
echo "  Upload the file: dist/prosody-stt_${VERSION}-1_all.deb"