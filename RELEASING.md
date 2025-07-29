# Release Process

This document describes how to create a new release of Prosody.

## Prerequisites

- Ensure all tests are passing on main branch
- Update CHANGELOG.md with release notes
- Ensure README.md is up to date

## Automatic Release (Recommended)

### Option 1: Create a Git Tag

```bash
# Update version in setup.py
# Commit the change
git add setup.py
git commit -m "Release version X.Y.Z"

# Create and push a tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main
git push origin vX.Y.Z
```

The GitHub Actions workflow will automatically:
1. Run all tests
2. Build the Debian package
3. Create a GitHub release with the .deb file attached

### Option 2: Manual Workflow Trigger

1. Go to Actions → Release workflow
2. Click "Run workflow"
3. Enter the version number (e.g., 1.0.1)
4. Click "Run workflow"

## Manual Release Process

If you need to build and release manually:

```bash
# 1. Update version
sed -i 's/version=".*"/version="X.Y.Z"/' setup.py

# 2. Update debian changelog
dch -v X.Y.Z-1 "Release version X.Y.Z"

# 3. Build the package
./build-deb.sh

# 4. Test the package
sudo dpkg -i dist/prosody-stt_X.Y.Z-1_all.deb
sudo apt-get install -f

# 5. Create GitHub release and upload the .deb file
```

## Post-Release

1. Update version in setup.py to next development version (e.g., X.Y.Z+1.dev0)
2. Announce the release (if applicable)
3. Update any documentation that references the version

## Version Numbering

We follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes only

## Testing a Release

Before creating a release:

```bash
# Run tests
pytest

# Build and test the Debian package
./test-deb-install.sh

# Test the installation
prosody --version
```