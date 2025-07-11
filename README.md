# Prosody

<div align="center">

```
    ____                            __     
   / __ \_________  _________  ____/ /_  __
  / /_/ / ___/ __ \/ ___/ __ \/ __  / / / /
 / ____/ /  / /_/ (__  ) /_/ / /_/ / /_/ / 
/_/   /_/   \____/____/\____/\__,_/\__, /  
                                  /____/   
```

**🎙️ A local, free, and open source AI-powered dictation tool**

</div>

Prosody is a lightweight, powerful dictation tool that provides AI-enhanced speech-to-text with intelligent text refinement. It runs locally on your machine with full privacy, using hotkey activation to dictate into any application.

## ✨ Features

- **🔥 Local Processing**: All speech recognition and AI processing happens on your device
- **⚡ Hardware Acceleration**: Automatic GPU detection (CUDA, MPS, DirectML, Intel XPU)
- **🎯 Universal Typing**: Works with any application or text field
- **🧠 AI Text Refinement**: Uses Qwen2.5-1.5B LLM to clean up and improve transcribed text
- **🎛️ Flexible Controls**: Toggle mode (double-tap) or push-to-talk
- **🔒 Privacy First**: No data leaves your machine
- **⚙️ Smart Defaults**: Optimized settings that work out of the box

## 🔍 How It Works

1. **Hotkey Detection**: Listens for configured hotkey combinations
2. **Audio Recording**: Captures audio from your microphone
3. **Speech Recognition**: Uses Whisper for local speech-to-text (shows raw output)
4. **Text Refinement**: Applies Qwen2.5-1.5B LLM to remove filler words and add punctuation
5. **Text Injection**: Types the refined text at your cursor position

## 🚀 Quick Start

1. **Install Prosody**:
```bash
pip install prosody
```

2. **Run Prosody**:
```bash
prosody
```

3. **Grant permissions** (see platform-specific instructions below):
   - Microphone access
   - Accessibility permissions (for automatic typing)

4. **Start dictating**:
   - Double-tap Left Control to start/stop recording
   - Speak clearly
   - Text appears automatically where your cursor is

## 📋 Requirements

- **Python 3.8+**
- **macOS, Windows, or Linux**
- **Microphone**
- **4GB+ RAM** (for AI models)

## 🎛️ Usage

### Basic Usage
```bash
# Run with optimal defaults
prosody

# Use a different Whisper model
prosody --model medium

# Use different hotkey
prosody --hotkey f12

# Enable push-to-talk mode
prosody --push-to-talk

# Debug mode
prosody --debug
```

### Hotkey Options
- `ctrl_l` (default) - Left Control
- `ctrl_r` - Right Control  
- `f12`, `f11`, `f10`, `f9` - Function keys
- `cmd` - Command key (macOS)
- `alt` - Alt key

### Operating Modes
- **Toggle Mode** (default): Double-tap hotkey to start/stop
- **Push-to-Talk**: Hold hotkey to record, release to process

### System Requirements
- **Memory**: 4GB+ RAM available (~244MB for Whisper Small, ~3GB for Qwen2.5-1.5B)
- **Storage**: 4GB+ free space for AI models (downloaded to `~/.cache/huggingface/`)
- **CPU**: Multi-core processor recommended
- **GPU**: Optional but recommended for faster processing
  - **Mac**: Apple Metal Performance Shaders (MPS) - automatic
  - **NVIDIA**: CUDA support
  - **Windows**: DirectML for AMD/Intel GPUs
  - **Intel**: XPU acceleration

## 📊 Performance

- **Whisper Models**: Choose from tiny (39MB) to large (1.5GB)
  - **Default**: Small model (244MB) - optimal speed/accuracy balance
- **Qwen2.5-1.5B Model**: ~3GB, conservative text cleanup
  - Removes only filler words ("um", "uh", "er")
  - Adds basic punctuation without rephrasing
- **Memory Usage**: ~4GB total with both models loaded
- **Latency**: <3 seconds for typical utterances with text refinement

## 🔐 Privacy & Security

- **100% Local Processing**: No data sent to external servers
- **No Internet Required**: Works completely offline after initial setup
- **Secure Permissions**: Only requests necessary macOS permissions
- **No Data Storage**: Audio and transcriptions are not saved

### macOS
**Hardware Acceleration:**
- **Built-in**: Apple Metal Performance Shaders (MPS)
- **No additional setup required**

**Permissions:**
Prosody automatically detects missing permissions and guides you through setup:

- **Microphone Access:**
  1. System Settings > Privacy & Security > Microphone
  2. Find and enable your terminal application (Terminal, iTerm2, etc.)

- **Accessibility Access:**
  1. System Settings > Privacy & Security > Accessibility
  2. Click the "+" button and add your terminal application
  3. Enable the toggle switch

- **Automatic Setup:**
  - Prosody will prompt you when permissions are needed
  - Follow the on-screen instructions
  - Restart your terminal after granting permissions

### Windows (Needs testing)
**Hardware Acceleration:**

*NVIDIA GPUs:*
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

*AMD/Intel GPUs (DirectML):*
```bash
pip install torch-directml
```

*Intel NPUs/GPUs:*
```bash
pip install intel-extension-for-pytorch
```

**Permissions:**
- **Microphone Access:**
  1. Settings > Privacy & Security > Microphone
  2. Ensure "Microphone access" is enabled
  3. Allow apps to access your microphone
  4. Make sure Python/Command Prompt has microphone access

- **For Automatic Typing:**
  - Windows doesn't require special permissions for keyboard simulation
  - If typing doesn't work, run Command Prompt as Administrator

### Linux (needs testing)
**Hardware Acceleration:**

*NVIDIA GPUs:*
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

*Intel GPUs/NPUs:*
```bash
pip install intel-extension-for-pytorch
```

*AMD GPUs (ROCm):*
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
```

**Permissions:**
- **Microphone Access:**
  ```bash
  # Check if your user is in the audio group
  groups $USER
  
  # Add yourself to audio group if needed
  sudo usermod -a -G audio $USER
  # Log out and back in for changes to take effect
  ```

- **For Automatic Typing:**
  - Most Linux distributions don't require special permissions
  - If you encounter issues, ensure your user has access to input devices:
  ```bash
  # Check input device permissions
  ls -l /dev/input/
  
  # Add user to input group if needed
  sudo usermod -a -G input $USER
  ```

- **Wayland Users:**
  - Some Wayland compositors may block keyboard simulation
  - Consider running under X11 for full functionality
  - Or use applications that support Wayland's input protocols

## 🐛 Troubleshooting

### Permission Issues
- See platform-specific instructions above
- Restart terminal/command prompt after granting permissions
- On Windows, try running as Administrator if issues persist
- On Linux, ensure you're in the correct user groups

### Poor Audio Quality
- Check microphone setup and positioning
- Ensure quiet environment
- Test with different Whisper models:
  - `tiny` - Fastest, least accurate (~39MB)
  - `base` - Good balance (~74MB)
  - `small` - Default, optimal balance (~244MB)
  - `medium` - Higher accuracy (~769MB)
  - `large` - Best accuracy (~1550MB)

### Performance Issues
- **Check GPU acceleration**: Look for "🚀 GPU acceleration" message at startup
- **Mac users**: Should see "Apple Metal Performance Shaders" automatically
- **Text refinement too slow**: The Qwen2.5-1.5B model is the main performance bottleneck
- Close other resource-intensive applications
- Consider using smaller Whisper models on older hardware

### Output Quality Issues
- **Raw Whisper output**: Shows first, before refinement
- **Refined output**: Should only remove filler words and add punctuation
- **If refinement is too aggressive**: The model may be rephrasing too much
- **Debug mode**: Use `--debug` flag to see detailed processing logs

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** following the existing architecture
4. **Add tests** for new functionality
5. **Run the test suite**: `python -m pytest tests/ -v`
6. **Submit a pull request**

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/loganthorneloe/prosody.git
cd prosody

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .[dev]

# Run tests
pytest
```

## 🧪 Testing

Run tests:
```bash
# Run all tests
python -m pytest tests/ -v

# Run quick tests
python tests/run_tests.py quick

# Run with coverage
python tests/run_tests.py coverage
```

Test structure:
```
tests/
├── test_prosody.py          # Main component and integration tests
├── test_platform_specific.py # Platform-specific tests
└── run_tests.py             # Test runner
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) for efficient speech recognition
- [Transformers](https://github.com/huggingface/transformers) for the Qwen2.5-1.5B model
- [pynput](https://github.com/moses-palmer/pynput) for cross-platform input handling
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) for audio capture

---

<div align="center">
Made with ❤️ for seamless dictation
</div>