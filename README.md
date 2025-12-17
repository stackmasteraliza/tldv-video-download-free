# 🎥 TLDV Meeting Video Downloader

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange.svg)](https://ffmpeg.org/)

> **Download your TLDV meeting recordings instantly!** 🚀

A lightweight Python script to download TLDV (Too Long Didn't View) meeting recordings for offline viewing. Save important meetings, presentations, and discussions without internet dependency. Perfect for professionals, students, and teams who need quick access to their meeting content.

## ✨ Features

- 🚀 **Fast Downloads** - Direct video fetching from TLDV servers
- 🔒 **Secure** - Uses your own authentication tokens
- 💾 **Offline Access** - Store videos locally for anytime viewing
- 📱 **Cross-Platform** - Works on Windows, macOS, and Linux
- 🎯 **Simple Setup** - Minimal dependencies, easy installation

## 📋 Prerequisites

- Python 3.6 or higher
- FFmpeg (for video processing)

## 🛠️ Installation

### 1. Install FFmpeg

Choose your platform:

#### 🪟 Windows (Recommended)
```powershell
winget install ffmpeg
```

#### 🍎 macOS
```bash
brew install ffmpeg
```

#### 🐧 Linux (Ubuntu/Debian)
```bash
sudo apt update && sudo apt install ffmpeg
```

#### 📥 Manual Download
Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system PATH.

### 2. Install Python Dependencies
```bash
pip install requests
```

## 🚀 Usage Guide

### Step-by-Step Instructions

1. 🌐 **Visit TLDV**: Go to [tldv.io](https://tldv.io/) and log in to your account
2. 📹 **Find Meeting**: Navigate to the meeting you want to download
3. 🔗 **Copy URL**: Copy the meeting URL from your browser address bar
4. 🛠️ **Developer Tools**: Press `F12` to open browser developer tools
5. 📡 **Network Tab**: Click on the "Network" tab
6. 🔄 **Refresh Page**: Refresh the page (`Ctrl+R` or `Cmd+R`)
7. 🔍 **Find Request**: Look for the request having title `auth`
8. 🏷️ **Copy Token**: Right-click the request → Copy → Copy as cURL, then extract the `Authorization: Bearer <token>` header
9. ⚙️ **Configure Script**: Edit `tldv.py` and update:
   - `url` variable with your meeting URL
   - `auth_token` variable with your Bearer token
10. ▶️ **Run Script**:
    ```bash
    python tldv.py
    ```

## 📸 Visual Guide

![How to get auth token](screenshots/guiding_screentshot.png)

*This screenshot demonstrates how to find and copy the authentication token from browser developer tools.*

## 📁 Output

The script will generate:
- `YYYY-MM-DD-HH-MM-SS_MeetingName.mp4` - Your downloaded video
- `YYYY-MM-DD-HH-MM-SS_MeetingName.json` - Meeting metadata

## ⚠️ Important Notes

- 🔐 **Security**: Never share your authentication tokens
- 📅 **Expiration**: Tokens may expire, requiring fresh extraction
- 🌐 **Internet Required**: Initial download needs internet connection
- 📝 **Legal**: Only download meetings you have access to

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ for the developer community</strong>
</p>