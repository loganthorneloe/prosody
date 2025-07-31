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

## 🚀 Quick Start (2 minutes)

### Option 1: Download Release (Recommended)
```bash
# Download latest release
wget https://github.com/loganthorneloe/prosody/releases/latest/download/prosody-1.0.0.tar.gz
tar -xzf prosody-1.0.0.tar.gz
cd prosody-1.0.0 && ./install.sh
```

### Option 2: Clone from Git
```bash
# Clone and install
git clone https://github.com/loganthorneloe/prosody.git
cd prosody && ./install.sh
```

**That's it!** Run `prosody` to start.

### Using Prosody (30 seconds)

1. **Run prosody in terminal** (or enable auto-start)
2. **Double-tap Left Ctrl** - You'll see a waveform at bottom of screen
3. **Speak clearly** - "Hello, this is a test of Prosody"
4. **Double-tap Left Ctrl again** - Text appears where your cursor is!
5. **To cancel:** Double-tap Escape while recording

### Running Options

```bash
# Run in foreground (see output)
prosody

# Run in background
prosody &

# Run with nohup (survives terminal close)
nohup prosody &

# Enable auto-start on login
systemctl --user enable prosody
systemctl --user start prosody
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

## Contributing

We love contributions! Whether you're fixing bugs, adding features, or improving documentation, we'd love your help making Prosody better.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/loganthorneloe/prosody.git
cd prosody
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Run tests
pip install -r requirements-test.txt
pytest
```

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