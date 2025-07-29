# Prosody Quick Start Guide

## Installation (5 minutes)

### For Users - Install from Release

```bash
# Download latest .deb from GitHub releases
wget https://github.com/yourusername/prosody/releases/latest/download/prosody-stt_1.0.0-1_all.deb

# Install it
sudo dpkg -i prosody-stt_1.0.0-1_all.deb
sudo apt-get install -f
```

### For Developers - Install from Source

```bash
# Clone
git clone https://github.com/yourusername/prosody.git
cd prosody

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt
pip install -e .
```

## First Run (2 minutes)

1. **Start Prosody**
   ```bash
   prosody
   ```
   
2. **Wait for model download** (first time only, ~140MB)
   ```
   Loading Whisper model 'base.en'...
   Model loaded successfully
   Prosody is starting...
   ```

3. **You'll see:**
   ```
   Double-tap Left Ctrl to start/stop recording
   Double-tap Escape to cancel recording
   ```

## Using Prosody (30 seconds)

1. **Open any text editor or application**

2. **Double-tap Left Ctrl** - You'll see a waveform at bottom of screen

3. **Speak clearly** - "Hello, this is a test of Prosody"

4. **Double-tap Left Ctrl again** - Text appears where your cursor is!

5. **To cancel:** Double-tap Escape while recording

## Tips

- **Best results:** Speak clearly, moderate pace
- **Punctuation:** Say "period", "comma", "question mark"
- **Multiple languages:** Edit `transcription.py` to use multilingual model
- **Auto-start:** Run `systemctl --user enable prosody`

## Troubleshooting

**No waveform appears?**
- Check if another app uses Ctrl hotkey
- Try running with `sudo prosody` (test only)

**No text appears?**
- Ensure cursor is in a text field
- Check microphone is working: `python -m sounddevice`

**Model download fails?**
- Check internet connection
- Manual download: `python -c "import whisper; whisper.load_model('base.en')"`

## Next Steps

- Read full [README.md](README.md) for advanced usage
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Report issues on [GitHub Issues](https://github.com/yourusername/prosody/issues)