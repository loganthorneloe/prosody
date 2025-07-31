# Changelog

All notable changes to Prosody will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Simplified to source-only distribution (removed Debian packaging)
- Installation now via simple `./install.sh` script
- Removed all GUI launchers and complex bundling

### Added
- Global hotkey support (double-tap Ctrl to record)
- Cancel recording with double-tap Escape
- Visual waveform indicator during recording
- Automatic transcription using OpenAI Whisper
- Direct text typing into active application
- Systemd service for auto-start
- Comprehensive test suite
- CI/CD with GitHub Actions

### Technical Details
- Built with Python 3.8+ compatibility
- Uses pynput for cross-platform hotkey detection
- sounddevice for audio recording
- OpenAI Whisper base.en model for transcription
- tkinter for visual indicators (no system tray)

[Unreleased]: https://github.com/loganthorneloe/prosody/compare/HEAD...HEAD