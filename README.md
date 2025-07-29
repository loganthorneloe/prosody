# Prosody

A simple, lightweight speech-to-text application for Linux that runs in the background and transcribes your speech on demand.

## Description

Prosody is a minimalist speech-to-text application that uses OpenAI's Whisper models for accurate transcription. It runs unobtrusively in the background and activates with a simple hotkey, making it perfect for quick voice input in any application.

## Features

- **Hotkey activation**: Double-tap Left Ctrl to start/stop recording
- **Visual indicator**: Clear on-screen indicator when recording is active
- **Menu bar icon**: System tray icon for easy access and application control
- **Auto-transcription**: Automatically types the transcribed text into your active window
- **Lightweight**: Minimal resource usage with efficient Whisper model

## Installation

### Quick Install (Debian/Ubuntu)

For Debian-based systems, you can install Prosody using our pre-built package:

```bash
sudo apt install ./prosody_1.0.0_amd64.deb
```

### Install from PyPI

```bash
pip install prosody-stt
```

### Install from Source

```bash
git clone https://github.com/yourusername/prosody.git
cd prosody
pip install -e .
```

## Usage

1. Start Prosody:
   ```bash
   prosody
   ```

2. The application will run in the background with an icon in your system tray

3. To record and transcribe:
   - Double-tap the Left Ctrl key to start recording
   - Speak your text
   - Double-tap Left Ctrl again to stop recording
   - The transcribed text will be automatically typed at your cursor position

4. To quit: Right-click the system tray icon and select "Quit"

### Controlling Prosody

Prosody runs in the background without a tray icon. Control it using:

#### Keyboard Shortcuts:
- **Double-tap Ctrl**: Start/stop recording
- **Ctrl+Shift+P**: Open control menu

#### Command Line:
```bash
prosody-control status    # Check if running
prosody-control pause     # Pause recording
prosody-control resume    # Resume recording  
prosody-control quit      # Stop Prosody
```

### Running at Startup

#### Option 1: Systemd User Service (Recommended)
```bash
# Install the service file
mkdir -p ~/.config/systemd/user
cp prosody.service ~/.config/systemd/user/

# Enable autostart
systemctl --user enable prosody.service
systemctl --user start prosody.service

# Check status
systemctl --user status prosody.service
```

#### Option 2: Desktop Autostart
```bash
# Create autostart entry
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/prosody.desktop << EOF
[Desktop Entry]
Type=Application
Name=Prosody
Exec=python3 -m prosody
Hidden=false
X-GNOME-Autostart-enabled=true
EOF
```

## Development

### Setting up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/prosody.git
   cd prosody
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # Option 1: Install minimal requirements first (recommended for testing)
   pip install -r requirements-minimal.txt
   
   # Then install Whisper separately (this downloads large models)
   pip install openai-whisper
   
   # Option 2: Install all at once (may timeout on slow connections)
   pip install -r requirements.txt --timeout 1000
   ```

4. Run from source:
   ```bash
   python -m prosody
   ```

### Project Structure

```
prosody/
├── src/
│   └── prosody/
│       ├── __init__.py
│       ├── main.py          # Main application entry point
│       ├── hotkey.py        # Hotkey listener logic
│       ├── audio.py         # Audio recording logic
│       ├── transcription.py # Whisper model interaction
│       └── ui.py            # Menu bar icon and recording indicator
├── tests/
│   ├── __init__.py
│   ├── test_hotkey.py
│   └── test_transcription.py
├── setup.py
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

### Building a Debian Package

To create a `.deb` package for easy distribution:

1. Install fpm (Effing Package Management):
   ```bash
   gem install fpm
   ```

2. Build the package:
   ```bash
   python setup.py sdist
   fpm -s python -t deb \
       --python-bin python3 \
       --python-package-name-prefix python3 \
       --python-install-bin /usr/local/bin \
       --after-install scripts/postinst.sh \
       --depends python3-pip \
       --depends python3-dev \
       --depends portaudio19-dev \
       setup.py
   ```

### Manual Testing

To verify full functionality:

1. **Test hotkey detection**: Run the app and double-tap Left Ctrl - the recording indicator should appear
2. **Test recording**: Speak while the indicator is visible, then double-tap Left Ctrl again
3. **Test transcription**: Verify that the spoken text appears at your cursor position
4. **Test system tray**: Right-click the tray icon and test the menu options
5. **Test persistence**: Ensure the app continues running after closing other applications

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit issues, feature requests, and pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.