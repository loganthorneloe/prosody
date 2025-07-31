<div align="center">
<pre>
    ____                            __     
   / __ \_________  _________  ____/ /_  __
  / /_/ / ___/ __ \/ ___/ __ \/ __  / / / /
 / ____/ /  / /_/ (__  ) /_/ / /_/ / /_/ / 
/_/   /_/   \____/____/\____/\__,_/\__, /  
                                  /____/   
</pre>
</div>

# Prosody

A lightweight, system-wide speech-to-text application for Linux that runs in the background and types transcribed text directly into any application.

[![CI](https://github.com/loganthorneloe/prosody/actions/workflows/test.yml/badge.svg)](https://github.com/loganthorneloe/prosody/actions/workflows/test.yml)
[![GitHub release](https://img.shields.io/github/release/loganthorneloe/prosody.svg)](https://github.com/loganthorneloe/prosody/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

For users who want to use Prosody:

### Option 1: Download Release
```bash
# Download latest release
wget https://github.com/loganthorneloe/prosody/releases/latest/download/prosody-1.0.0.tar.gz
tar -xzf prosody-1.0.0.tar.gz
cd prosody-1.0.0

# IMPORTANT: Fix permissions (downloaded files are read-only by default)
chmod -R u+w .

# Install
./install.sh
```

**Note:** The `chmod` step is required because downloaded releases extract with read-only permissions. Without it, the installer will fail with "Permission denied".

### Option 2: Clone from Git
```bash
git clone https://github.com/loganthorneloe/prosody.git
cd prosody
./install.sh
```

**Now run it:**
```bash
prosody  # This is the command you'll use
```

## 🛠️ Development Setup

For developers who want to contribute or modify the code:

```bash
# Clone the repo
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -e .

# Run your development version
python -m prosody  # Note: Don't use 'prosody' - that runs the installed version
```

**Important:** When developing, always use `python -m prosody` to test your changes. The `prosody` command will run the installed version, not your development code.

---

## How to Use Prosody

Once running (either `prosody` for users or `python -m prosody` for developers):

1. **Double-tap Left Ctrl** - You'll see a waveform at bottom of screen
2. **Speak clearly** - "Hello, this is a test of Prosody"
3. **Double-tap Left Ctrl again** - Text appears where your cursor is!
4. **To cancel:** Double-tap Escape while recording

### Running Options

```bash
# Run in foreground (see output)
prosody

# Run in background (silent)
prosody > /dev/null 2>&1 &

# Run with nohup (survives terminal close)
nohup prosody > /dev/null 2>&1 &

# Run as systemd service (cleanest option)
systemctl --user start prosody

# Enable auto-start on login
systemctl --user enable prosody
```

## What is Prosody?

Prosody is your personal voice-to-text assistant that lives quietly in the background. With a simple double-tap of the Ctrl key, speak naturally and watch your words appear wherever you're typing - in emails, documents, chat messages, or code editors. No need to switch windows or click buttons. Just speak and type!

### Why Prosody?

- **Works Everywhere**: Types directly into any application - browsers, editors, terminals, chat apps
- **Privacy First**: Runs locally on your machine, no cloud services required
- **Silent & Lightweight**: Runs invisibly in background, minimal CPU/memory usage
- **Fast**: Instant transcription with OpenAI's Whisper model
- **Simple**: Just one hotkey to remember - double-tap Ctrl
- **Open Source**: MIT licensed, hack away!

### Key Features

- 🎤 **Global Hotkey**: Double-tap Left Ctrl to start/stop recording
- 🚫 **Cancel Recording**: Double-tap Escape to cancel without transcribing
- 📊 **Visual Feedback**: Elegant waveform indicator shows recording status
- ⌨️ **Direct Typing**: Transcribed text is automatically typed at cursor position
- 🤖 **Powered by Whisper**: Uses OpenAI's Whisper model for accurate transcription

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Linux with X11 (Ubuntu, Debian, Fedora, etc.)
- Working microphone
- PulseAudio or PipeWire audio system

### System Dependencies (if needed)
Some systems may need additional packages:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-tk portaudio19-dev

# Fedora
sudo dnf install python3-devel python3-tkinter portaudio-devel

# Arch
sudo pacman -S python tk portaudio
```

### Install Script
The easiest way - downloads and sets up everything:

```bash
git clone https://github.com/loganthorneloe/prosody.git
cd prosody
./install.sh
```

### Manual Installation
If you prefer to install manually:

```bash
# Clone the repository
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Set up auto-start (optional)
mkdir -p ~/.config/systemd/user/
cp prosody.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable prosody
```

## First Use Notes

- First recording triggers Whisper model download (~140MB)
- Takes about 1 minute on first use only
- **Best results:** Speak clearly, moderate pace
- **Punctuation:** Say "period", "comma", "question mark"
- **Important:** Make sure `~/.local/bin` is in your PATH for the `prosody` command to work

## Updating Prosody

### Option 1: If you cloned with git
```bash
cd ~/prosody        # wherever you cloned it
git pull
./install.sh        # updates dependencies if needed
```

### Option 2: If you downloaded a release
```bash
# Download new version
wget https://github.com/loganthorneloe/prosody/releases/latest/download/prosody-X.X.X.tar.gz
tar -xzf prosody-X.X.X.tar.gz
cd prosody-X.X.X

# Fix permissions (needed for downloaded releases)
chmod -R u+w .

# Install (this updates the wrapper to point to the new location)
./install.sh

# Optional: Remove old version
rm -rf ~/prosody-1.0.0
```

**How it works:** The `prosody` command always runs from wherever you last ran `install.sh`, because the installer saves that location.

## Uninstalling Prosody

To uninstall Prosody:

```bash
# Run the uninstaller (works from any directory)
~/prosody/uninstall.sh  # or wherever you installed it

# Optional: Remove the installation directory
rm -rf ~/prosody

# Optional: Remove Whisper model cache (~140MB)
rm -rf ~/.cache/whisper
```

The uninstaller will:
- Stop and disable the systemd service
- Remove the `prosody` command from ~/.local/bin
- Clean up systemd configuration

## How It Works

Prosody uses:
- **OpenAI Whisper** (base.en model, ~140MB) for speech recognition
- **pynput** for global hotkey detection across all applications
- **sounddevice** for low-latency audio recording
- **tkinter** for the minimal waveform visualization

The app runs as a background service, listening for your hotkey. When you double-tap Ctrl, it records audio, sends it to Whisper for transcription, and types the result wherever your cursor is positioned.

## Troubleshooting

### No waveform appears?
- Check if another app uses Ctrl hotkey
- Try running with `sudo prosody` (test only)

### No text appears?
- Ensure cursor is in a text field
- Check microphone is working: `python -m sounddevice`

### Model download fails?
- Check internet connection
- Manually download: `python -c "import whisper; whisper.load_model('base.en')"`

### Installation fails with "error: Microsoft Visual C++ 14.0 is required"?
- This is a Windows error - Prosody is Linux-only
- Use WSL2 on Windows if needed

### "prosody: command not found"?
- Make sure ~/.local/bin is in your PATH
- Add to ~/.bashrc: `export PATH="$HOME/.local/bin:$PATH"`
- Then run: `source ~/.bashrc`

### "Cannot create ~/.config/systemd/user/" during install?
- Your systemd directory is probably owned by root
- Fix with: `sudo chown -R $USER:$USER ~/.config/systemd`
- Then run `./install.sh` again

## Contributing

We love contributions! Whether you're fixing bugs, adding features, or improving documentation, we'd love your help making Prosody better.

### ⚠️ Developer Warning

When developing, remember that the `prosody` command runs the installed version, not your development code. Always use `python -m prosody` to test your changes.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -e .

# Test YOUR development code
python -m prosody  # ← THIS IS HOW YOU TEST!

# Run tests
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

### Project Structure

```
prosody/
├── src/prosody/
│   ├── main.py          # Application entry point
│   ├── audio.py         # Audio recording
│   ├── hotkey.py        # Global hotkey detection
│   ├── transcription.py # Whisper integration
│   └── ui_polished.py   # Visual indicators
├── tests/               # Test suite
├── install.sh          # Installation script
└── prosody.service     # Systemd service file
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/prosody
```

### How to Contribute

1. Fork the repo
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

All contributions are welcome - code, documentation, bug reports, or feature ideas!

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [OpenAI Whisper](https://github.com/openai/whisper)
- Hotkey detection via [pynput](https://github.com/moses-palmer/pynput)
- Audio recording with [sounddevice](https://github.com/spatialaudio/python-sounddevice)