# 🎥 TLDV Video Downloader

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange.svg)](https://ffmpeg.org/)

> **Download your TLDV meeting recordings instantly!** 🚀

A lightweight Python CLI tool to download [TLDV](https://tldv.io) meeting recordings for offline viewing. Perfect for professionals, students, and teams who need quick access to their meeting content with beautiful progress tracking.

## ✨ Features

- 🚀 **Fast Downloads** — Direct video stream copy from TLDV servers (no re-encoding)
- 📊 **Live Progress Bar** — Beautiful real-time download progress with speed, ETA, and statistics
- 📝 **Transcript Export** — Saves meeting transcripts with timestamps and speaker names
- 🎯 **Flexible Input** — Pass meeting URL and token via CLI flags, environment variables, or interactive prompts
- 🔍 **Auto-detect FFmpeg** — Finds ffmpeg on your PATH automatically
- 💻 **Cross-Platform** — Works on Windows, macOS, and Linux
- 🎨 **Beautiful UI** — Rich terminal interface with panels, tables, and color-coded output

## 📋 Prerequisites

- Python 3.6 or higher
- [FFmpeg](https://ffmpeg.org/download.html)
- Python packages: `requests`, `rich`

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/stackmasteraliza/tldv-video-download-free.git
cd tldv-video-download-free
```

### 2. Install Python Dependencies
```bash
pip install requests rich
```

### 3. Install FFmpeg

Choose your platform:

#### 🪟 Windows
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
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system PATH.

## 🚀 Usage

### Method 1: Interactive Mode (Easiest)

Simply run the script and follow the prompts:

```bash
python tldv.py
```

You'll be asked to enter:
1. Meeting URL or ID
2. Bearer token

### Method 2: Command-Line Arguments

```bash
python tldv.py --url "https://tldv.io/app/meetings/abc123" --token "Bearer eyJ..."
```

### Method 3: Environment Variables

```bash
export TLDV_URL="https://tldv.io/app/meetings/abc123"
export TLDV_TOKEN="Bearer eyJ..."
python tldv.py
```

### 📝 All Available Options

```
usage: tldv.py [-h] [-u URL] [-t TOKEN] [-o OUTPUT_DIR] [--ffmpeg FFMPEG] [--ffprobe FFPROBE]

Options:
  -u, --url URL           TLDV meeting URL or meeting ID
  -t, --token TOKEN       Authorization token (Bearer token from browser dev tools)
  -o, --output-dir DIR    Directory to save downloaded files (default: current directory)
  --ffmpeg FFMPEG         Path to ffmpeg binary (auto-detected if not provided)
  --ffprobe FFPROBE       Path to ffprobe binary (auto-detected if not provided)
```

## 🔑 How to Get Your Auth Token

Follow these steps to extract your authentication token:

1. 🌐 **Visit TLDV**: Go to [tldv.io](https://tldv.io) and log in to your account
2. 📹 **Open Meeting**: Navigate to the meeting you want to download
3. 🛠️ **Developer Tools**: Press **F12** to open browser developer tools
4. 📡 **Network Tab**: Click on the **Network** tab
5. 🔄 **Refresh Page**: Refresh the page (**Ctrl+R** or **Cmd+R**)
6. 🔍 **Find Request**: Look for a request named `auth` or `watch-page`
7. 🏷️ **Copy Token**: Click the request → Find the `Authorization` header → Copy the full `Bearer eyJ...` value

![How to get auth token](screenshots/guiding_screentshot.png)

*Visual guide showing how to extract the authentication token from browser developer tools.*

## 📁 Output Files

The script generates three files in the output directory:

| File | Description |
|------|-------------|
| `YYYY-MM-DD-HH-MM-SS_MeetingName.mp4` | 🎥 Meeting video |
| `YYYY-MM-DD-HH-MM-SS_MeetingName.json` | 📄 Raw API metadata |
| `YYYY-MM-DD-HH-MM-SS_MeetingName_transcript.txt` | 📝 Formatted transcript |

### Transcript Format

The transcript file contains speaker-attributed text with timestamps:

```
[00:00] Speaker Name: Hello everyone, welcome to the meeting.
[00:15] Another Speaker: Thanks for having me.
[01:30] Speaker Name: Let's get started with the agenda.
```

## ⚠️ Important Notes

- 🔐 **Security**: Never share your authentication tokens publicly
- 📅 **Token Expiration**: Tokens may expire, requiring fresh extraction from browser
- 🌐 **Internet Required**: Initial download requires internet connection
- 📝 **Legal**: Only download meetings you have legitimate access to
- 🔒 **Privacy**: The `.gitignore` excludes `.env` files to protect your credentials

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👨‍💻 Author

**Aliza Ali** — [GitHub](https://github.com/stackmasteraliza)

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>Built with ❤️ by Aliza Ali</strong>
</p>
