# Prosody Quick Start Guide

## 🚀 Installation (2 minutes)

```bash
# Download and install
wget https://github.com/loganthorneloe/prosody/releases/latest/download/prosody-stt_1.0.0-1_all.deb
sudo dpkg -i prosody-stt_1.0.0-1_all.deb
sudo apt-get install -f
```

**That's it!** Prosody starts automatically. Look for the notification!

### For Developers - Install from Source

```bash
# Clone
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt
pip install -e .
```

## ✨ First Use

**No need to start anything!** After installation:
- Prosody is already running (check notification area)
- First recording triggers Whisper model download (~140MB)
- Takes about 1 minute on first use only

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
- **Already auto-starts!** No configuration needed

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
- Report issues on [GitHub Issues](https://github.com/loganthorneloe/prosody/issues)