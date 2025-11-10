# Reminders to Google Calendar

A macOS menubar app that automatically syncs Mac/iPhone Reminders to Google Calendar.

![Version](https://img.shields.io/badge/version-0.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

[한국어 문서](README.ko.md)

## Features

- ✅ **One-way Sync**: Mac/iPhone Reminders → Google Calendar
- ✅ **Auto Sync**: Configurable intervals (15min, 30min, 1hr, 2hr)
- ✅ **Menubar Integration**: Lightweight and convenient menubar app
- ✅ **Priority Colors**: Maps Reminders priority to Google Calendar colors
- ✅ **Location Support**: Syncs location information from Reminders
- ✅ **Completed Items**: Auto-delete or keep completed items
- ✅ **Duplicate Prevention**: UUID-based mapping prevents duplicate events
- ✅ **Error Recovery**: Retry and re-authentication options on sync failure

## Screenshots

(Coming soon)

## System Requirements

- macOS 10.15 (Catalina) or later
- Python 3.9+ (for development)
- Google Account
- Apple ID (for iCloud sync)

## Installation

### Method 1: DMG Installation (Recommended)

1. Download the latest DMG from [Releases](https://github.com/huiseo/reminders-to-gcal/releases)
2. Open the DMG file and drag `Reminders to GCal.app` to the `Applications` folder
3. Launch the app

### Method 2: Build from Source

```bash
# Clone repository
git clone https://github.com/huiseo/reminders-to-gcal.git
cd reminders-to-gcal

# Install dependencies
pip3 install -r requirements.txt

# Build app
./build_app.sh

# Install
cp -r "dist/Reminders to GCal.app" /Applications/
```

## Initial Setup

### 1. Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 Client ID (Desktop app)
5. Download `credentials.json`
6. Copy the file to the app's Resources folder:
   ```bash
   cp credentials.json "/Applications/Reminders to GCal.app/Contents/Resources/"
   ```

### 2. First Launch

1. Double-click `Reminders to GCal.app` in Finder
2. Approve Reminders access permission
3. Complete Google OAuth authentication in browser
4. Check for the R→GCal icon in the menubar

## Usage

### Menubar Menu

- **Sync Now**: Run sync immediately
- **Last Sync**: Show last sync information
- **Preferences**: Configure auto-sync interval
- **View Logs**: View sync logs
- **Open Reminders**: Open Reminders app
- **Open Google Calendar**: Open Google Calendar web
- **Help**: Help and GitHub issues page
- **About**: App information
- **Quit**: Quit app

### Configuration

Edit `config.yaml` to customize settings:

```yaml
reminders:
  sync_lists: []  # Sync specific lists (empty = all)
  skip_completed_older_than_days: 30  # Skip old completed items

sync:
  completed_action: delete  # Action for completed: delete or keep

google_calendar:
  calendar_id: primary  # Target calendar ID
  priority_colors:
    high: "11"    # Red
    medium: "5"   # Yellow
    low: "7"      # Blue
```

## Architecture

```
reminders-to-gcal/
├── src/
│   ├── auth.py              # Google OAuth authentication
│   ├── reminders_reader.py  # Mac Reminders reader (EventKit)
│   ├── gcal_writer.py       # Google Calendar writer
│   └── sync_engine.py       # Sync logic and DB
├── tests/                   # Test code (56 tests)
├── menubar_app.py          # Menubar app (rumps)
├── config.yaml             # Configuration file
├── build_app.sh            # Build script
└── Uninstall.command       # Uninstall script
```

## Development

### Development Setup

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run tests
python3 -m unittest discover -s tests -v

# Run app (development mode)
python3 menubar_app.py
```

### Testing

- **Total: 56 tests**
- **Pass rate: 94.6%** (53/56 passed)
- Includes unit tests, integration tests, and quality tests

```bash
# Run all tests
python3 -m unittest discover -s tests

# Run specific tests
python3 -m unittest tests.test_sync_engine
python3 -m unittest tests.test_quality
```

### Build

```bash
# Build app
./build_app.sh

# Create DMG
hdiutil create -volname "Reminders to GCal" \
  -srcfolder /tmp/dmg_build \
  -ov -format UDZO \
  "Reminders-to-GCal-Installer.dmg"
```

## Data & Privacy

### Stored Data

- **Local Database** (`mapping.db`): Stores UUID mappings only
- **OAuth Token** (`token.json`): Protected with 0o600 permissions
- **Config File**: User preferences

### Data Transfer

- Data transfer only through Google Calendar API
- All communication encrypted via HTTPS
- No data transfer to third-party servers

## Troubleshooting

### App Won't Launch

```bash
# Check logs
tail -f "/Applications/Reminders to GCal.app/Contents/Resources/logs/menubar_app.log"

# Check permissions
ls -la "/Applications/Reminders to GCal.app/Contents/Resources/credentials.json"

# Remove lock file
rm ~/.reminders-to-gcal.lock
```

### Sync Not Working

1. Check auto-sync interval in **Preferences**
2. Check error messages in **View Logs**
3. Reset Google OAuth token:
   ```bash
   rm "/Applications/Reminders to GCal.app/Contents/Resources/data/token.json"
   ```
4. Restart app and re-authenticate

## Uninstallation

### Using Uninstall.command from DMG

1. Re-mount the DMG
2. Double-click `Uninstall.command`
3. Enter administrator password

### Manual Uninstallation

```bash
# Quit app
pkill -f "Reminders to GCal"

# Remove all files
rm -rf "/Applications/Reminders to GCal.app"
rm ~/.reminders-to-gcal-prefs.json
rm ~/.reminders-to-gcal.lock
```

## Contributing

Pull requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Roadmap

- [ ] v1.0.0 - First stable release
- [ ] Auto-launch on login UI
- [ ] Multi-language support (Korean/English)
- [ ] Bi-directional sync (Google Calendar → Reminders)
- [ ] Selective list sync UI
- [ ] Performance optimization (large datasets)

## Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [PyObjC - EventKit](https://pyobjc.readthedocs.io/)
- [rumps - macOS menubar apps](https://github.com/jaredks/rumps)

## Contact

- **Issues**: [GitHub Issues](https://github.com/huiseo/reminders-to-gcal/issues)
- **Email**: hui.seo@gmail.com

---

**Made with ❤️ for productivity**
