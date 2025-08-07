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

A lightweight speech-to-text application for Linux that runs in the background and types transcribed text directly into any application.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Run setup (installs dependencies and configures auto-start)
./setup.sh

# Start Prosody
systemctl --user start prosody
```

That's it! Prosody is now running and will start automatically when you log in.

## How to Use

1. **Double-tap Left Ctrl** - Start recording (waveform appears at bottom of screen)
2. **Speak clearly** into your microphone
3. **Double-tap Left Ctrl again** - Stop recording and transcribe
4. Text appears wherever your cursor is!

**Cancel recording:** Press Escape while recording

## Requirements

- Linux with X11
- Python 3.8+
- Working microphone
- ~2GB disk space for dependencies

## Managing Prosody

```bash
# Check if running
systemctl --user status prosody

# Stop
systemctl --user stop prosody

# Restart
systemctl --user restart prosody

# Disable auto-start
systemctl --user disable prosody

# View logs
journalctl --user -u prosody -f
```

## Development

```bash
# Set up development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Run from source
python -m prosody

# Run tests
pytest
```

## How It Works

Prosody uses OpenAI's Whisper model (base.en, ~140MB) for accurate speech recognition. The model downloads automatically on first use.

The app listens for your hotkey, records audio when triggered, transcribes it locally (no cloud services), and types the result wherever your cursor is positioned.

## Troubleshooting

**No waveform appears?**
- Check if another app uses Ctrl hotkey
- Make sure Prosody is running: `systemctl --user status prosody`

**No text appears?**
- Ensure cursor is in a text field
- Check microphone: `arecord -l`

**First use is slow?**
- Whisper model downloads on first use (~140MB)
- Subsequent uses are instant

## Contributing

Pull requests welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT - see [LICENSE](LICENSE)