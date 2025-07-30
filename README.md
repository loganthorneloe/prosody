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

A lightweight, system-wide speech-to-text application (designed for Linux) that runs in the background and types transcribed text directly into any application.

[![CI](https://github.com/loganthorneloe/prosody/actions/workflows/test.yml/badge.svg)](https://github.com/loganthorneloe/prosody/actions/workflows/test.yml)
[![GitHub release](https://img.shields.io/github/release/loganthorneloe/prosody.svg)](https://github.com/loganthorneloe/prosody/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

```bash
# Download and install (Ubuntu/Debian)
wget https://github.com/loganthorneloe/prosody/releases/latest/download/prosody-stt_1.0.0-1_all.deb
sudo dpkg -i prosody-stt_1.0.0-1_all.deb
sudo apt-get install -f
```

**That's it!** Find "Prosody Speech-to-Text" in your application menu and click to start!

*Note: First launch installs dependencies (~2GB) - you'll see progress notifications.*

**Prosody runs silently in the background** - no windows, no terminal, just notifications when starting.

### 🎤 How to Use
1. Click where you want to type
2. **Double-tap Left Ctrl** to start recording
3. Speak naturally
4. **Double-tap Left Ctrl** again to transcribe
5. Your words appear instantly!

**Pro tip:** Double-tap Escape to cancel recording without transcribing.

## What is Prosody?

Prosody is your personal voice-to-text assistant that lives quietly in the background. With a simple double-tap of the Ctrl key, speak naturally and watch your words appear wherever you're typing - in emails, documents, chat messages, or code editors. No need to switch windows or click buttons. Just speak and type!

### Why Prosody?

- **Works Everywhere**: Types directly into any application - browsers, editors, terminals, chat apps
- **Privacy First**: Runs locally on your machine, no cloud services required
- **Silent & Lightweight**: Runs invisibly in background, minimal CPU/memory usage
- **Fast**: Instant transcription with OpenAI's Whisper model
- **Simple**: Just one hotkey to remember - double-tap Ctrl
- **Auto-starts**: Runs automatically on every login (after first launch)
- **Open Source**: Powered by OpenAI Whisper (base.en model)

### Key Features

- 🎤 **Global Hotkey**: Double-tap Left Ctrl to start/stop recording
- 🚫 **Cancel Recording**: Double-tap Escape to cancel without transcribing
- 📊 **Visual Feedback**: Elegant waveform indicator shows recording status
- ⌨️ **Direct Typing**: Transcribed text is automatically typed at cursor position
- 🚀 **Zero Configuration**: Install and launch from application menu - no terminal needed
- 🤖 **Powered by Whisper**: Uses OpenAI's Whisper model for accurate transcription

### How It Works

Prosody uses:
- **OpenAI Whisper** (base.en model, ~140MB) for speech recognition
- **pynput** for global hotkey detection across all applications
- **sounddevice** for low-latency audio recording
- **tkinter** for the minimal waveform visualization

The app runs as a background service, listening for your hotkey. When you double-tap Ctrl, it records audio, sends it to Whisper for transcription, and types the result wherever your cursor is positioned.

### Controls
- **Double-tap Left Ctrl**: Start/stop recording and transcribe
- **Double-tap Escape**: Cancel current recording (no text output)
- **Visual Indicator**: Elegant waveform shows when recording

## Installation

### From Source (For Development)

```bash
# Clone the repository
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt
pip install -e .
```

**What happens after installation:**
- 🚀 Launch from your application menu (search "Prosody")
- ✅ Auto-starts on every login after first launch
- ⬇️ First use downloads Whisper model (~140MB, one-time)
- 🔔 Shows notification when ready

To manage the service:
```bash
# Check if running
systemctl --user status prosody

# Stop temporarily
systemctl --user stop prosody

# Disable auto-start
systemctl --user disable prosody
```

## Contributing to Prosody

We love contributions! Whether you're fixing bugs, adding features, or improving documentation, we'd love your help making Prosody better.

### Quick Start

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
├── debian/              # Debian packaging
├── .github/workflows/   # CI/CD automation
└── build-deb.sh        # Build Debian package
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/prosody

# Test the Debian package
./test-deb-install.sh
```

### Building Debian Package

```bash
# Build the package
./build-deb.sh

# Package will be in dist/
ls dist/*.deb
```

### Making a Release

Releases are automated via GitHub Actions:

```bash
# Tag and push to trigger release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will:
# 1. Run tests
# 2. Build .deb package
# 3. Create GitHub release
# 4. Attach .deb file
```


## Troubleshooting

### No audio recording
- Check microphone permissions
- Ensure PulseAudio/PipeWire is running
- Try: `python -m sounddevice`

### Hotkeys not working
- Some applications may capture Ctrl key
- Try running with sudo (not recommended for regular use)
- Check if another app is using the same hotkey

### Model download fails
- Check internet connection
- Manually download: `python -c "import whisper; whisper.load_model('base.en')"`

### How to Contribute

See our [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. Here's the quick version:

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