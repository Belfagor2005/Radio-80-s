# RadioM - Enigma2 Radio Plugin

<div align="center">

<img src="https://raw.githubusercontent.com/Belfagor2005/Radio-80-s/main/usr/lib/enigma2/python/Plugins/Extensions/RadioM/skin/fhd/80s.png" width="150" height="150" alt="RadioM Logo">

**A powerful radio streaming plugin for Enigma2 receivers**

![](https://komarev.com/ghpvc/?username=Belfagor2005)
[![Version](https://img.shields.io/badge/Version-1.4-blue.svg)](https://github.com/Belfagor2005/RadioM)
[![License](https://img.shields.io/badge/License-GPLv2-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-2.7%2F3.x-yellow.svg)](https://python.org)

</div>

## 📻 Features

- **Massive Station Database**: Access thousands of radio stations from laut.fm
- **Multi-Page Loading**: Automatically loads multiple pages for extensive station selection
- **High-Quality Streams**: Direct stream URLs for optimal audio quality
- **Station Images**: Download and display station logos automatically
- **Multiple Players**: Support for different audio players (1-2-3)
- **Playlist Support**: Load custom playlists from local files
- **Real-time Info**: Display current song, listeners, and station metadata
- **Cross-Platform**: Compatible with Python 2.7 and Python 3.x
- **Responsive UI**: Adapts to different screen resolutions (HD, FHD, WQHD)

## 🚀 Installation

### IPK Package
```bash
# Install via IPK package
opkg install radiom_1.3_all.ipk
```

### Manual Installation
```bash
# Copy plugin files
cp -r RadioM /usr/lib/enigma2/python/Plugins/Extensions/

# Restart Enigma2
systemctl restart enigma2
```

## 🎮 Usage

1. **Navigate** to Plugin Menu → RadioM
2. **Browse** through available radio stations
3. **Select** a station to view detailed information
4. **Play** using your preferred audio player
5. **Manage** custom playlists in the Playlists section

### Player Selection
- **Player 1**: Default audio player
- **Player 2**: Alternative player implementation  
- **Player 3**: Additional player option

## 🛠️ Technical Details

### Supported Platforms
- Enigma2-based receivers (DreamOS, OpenPLi, etc.)
- Python 2.7 and Python 3.x compatibility
- Multiple screen resolutions (HD, FHD, WQHD)

### File Structure
```
RadioM/
├── plugin.py              # Main plugin code
├── PicLoader.py           # Image handling
├── Console.py            # Console operations
├── skin/                  # UI skins
│   ├── hd/               # HD resolution
│   ├── fhd/              # Full HD resolution  
│   └── wqhd/             # WQHD resolution
└── Playlists/            # Custom playlists directory
```

## 🔧 Configuration

### Custom Playlists
Create `.txt` files in the `Playlists` directory with the following format:
```
Station Name###http://stream.url
Another Station###http://another.stream.url
```

### Skin Customization
Modify skin files in the `skin/` directory to customize the appearance for different resolutions.

## 📷 Screenshots

*(Add your screenshots here)*

- Main station list view
- Station details with current song information
- Playlist management interface

## 🤝 Contributing

We welcome contributions! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup
```bash
git clone https://github.com/Belfagor2005/RadioM.git
cd RadioM
# Make your changes and test on Enigma2 receiver
```

## 📄 License

This project is licensed under the GPL v2 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Lululla** - Original concept and development
- **Mmark** - Plugin modifications and enhancements
- **laut.fm** - Radio station data and streams

## 🔗 Links

- [GitHub Repository](https://github.com/Belfagor2005/RadioM)
- [Enigma2 Development Forum](https://www.world-of-satellite.com)

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Visit Enigma2 development forums

---

<div align="center">

**Enjoy listening to your favorite radio stations! 📻**

</div>
```