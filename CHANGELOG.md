# Changelog

All notable changes to Prosody will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Prosody
- Global hotkey support (double-tap Ctrl to record)
- Cancel recording with double-tap Escape
- Visual waveform indicator during recording
- Automatic transcription using OpenAI Whisper
- Direct text typing into active application
- Systemd service for auto-start
- Debian package distribution
- Comprehensive test suite with 72% coverage
- CI/CD with GitHub Actions
- Automated release process

### Technical Details
- Built with Python 3.8+ compatibility
- Uses pynput for cross-platform hotkey detection
- sounddevice for audio recording
- OpenAI Whisper base.en model for transcription
- tkinter for visual indicators (no system tray)

## [1.0.0] - TBD

First public release.

[Unreleased]: https://github.com/yourusername/prosody/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/prosody/releases/tag/v1.0.0