# 🎬 YouTube Video Downloader (Streamlit + yt-dlp)

A lightweight web application for downloading YouTube videos with [yt-dlp](https://github.com/yt-dlp/yt-dlp), wrapped in a modern [Streamlit](https://streamlit.io/) UI.  

This service is ideal for **HomeLab workflows** where you want to automatically fetch, clean, and organize videos before integrating them into media managers like **Plex** or **Jellyfin**.  

---

## ✨ Features

- Web UI built with **Streamlit**  
- Download videos in **MKV** format with best available quality  
- Metadata, thumbnail, and chapter embedding  
- Optional subtitle selection and embedding (configurable via `.env`)  
- Temporary download folder before moving files to the right place  
- SponsorBlock integration to automatically remove sponsored sections  
- Dockerized for easy deployment in a HomeLab  

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/youtube-downloader.git
cd youtube-downloader
```

### 2. Configure environment
Create a `.env` file in the project root:

```bash
# Path to YouTube cookies (see section below)
YOUTUBE_COOKIES_FILE_PATH=/config/youtube_cookies.txt

# Destination root folder for videos
VIDEOS_FOLDER=/data/Videos

# Temporary download folder
TMP_DOWNLOAD_FOLDER=/data/tmp

# Subtitles available for selection in UI
SUBTITLES_CHOICES=en,fr
```

### 3. Run with Docker Compose
```bash
docker compose up -d
```

The service will be available at:  
👉 [http://localhost:8501](http://localhost:8501)

---

## 📂 Project Structure

```
.
├── app/
│   ├── main.py          # Streamlit UI + download logic
│   └── requirements.txt # Python dependencies
├── .streamlit/
│   └── config.toml      # Theme customization
├── Dockerfile
├── docker-compose.yml
└── .env                 # Your environment variables
```

---

## 🍪 Using YouTube Cookies

Some videos may require authentication (age restrictions, region locks, subscriptions).  
To handle this, yt-dlp supports importing cookies from your browser.

1. Install the [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/ekhagklcjbdpajgpjgmbionohlpdbjgc) extension (Chrome/Edge) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (Firefox).  
2. Go to [YouTube](https://youtube.com) while logged into your account.  
3. Export cookies to a file (`cookies.txt`).  
4. Place the file in the path defined in your `.env` (`YOUTUBE_COOKIES_FILE_PATH`).  

Now downloads will work with your logged-in session.  

---

## 🛠️ Development

To run locally without Docker:

```bash
pip install -r app/requirements.txt
streamlit run app/main.py
```

---

## 🔒 Disclaimer

This project is for **personal and educational use only**.  
You are responsible for respecting YouTube’s Terms of Service and copyright law in your jurisdiction.  

---

## 📌 Example Workflow

- Deploy this service in your **HomeLab** (Proxmox, Docker, etc.)  
- Download YouTube content into your designated `VIDEOS_FOLDER`  
- Point your **Plex** or **Jellyfin** library to that folder  
- Enjoy a clean, subtitle-ready media collection, free from ads and sponsor interruptions 🎉  

---