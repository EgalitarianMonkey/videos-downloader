import os
import re
import shutil
import subprocess
from pathlib import Path
import streamlit as st

# === ENV ===
VIDEOS_FOLDER = Path(
    os.getenv(
        "VIDEOS_FOLDER",
        str(Path.home() / "Temporaires" / "Youtube_videos_downloads_tmp"),
    )
)
TMP_DOWNLOAD_FOLDER = Path(os.getenv("TMP_DOWNLOAD_FOLDER", str(VIDEOS_FOLDER / "tmp")))
YOUTUBE_COOKIES_FILE_PATH = os.getenv(
    "YOUTUBE_COOKIES_FILE_PATH",
    str(Path.home() / ".config" / "downloads" / "youtube_cookies.txt"),
)
SUBTITLES_CHOICES = [
    x.strip() for x in os.getenv("SUBTITLES_CHOICES", "en,fr").split(",") if x.strip()
]

# === UI CFG ===
st.set_page_config(
    page_title="Youtube Videos Downloader", page_icon="🎬", layout="centered"
)
st.title("🎬  YouTube Video Download")


# === Helpers ===
def list_subdirs(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted([p.name for p in root.iterdir() if p.is_dir()])


def sanitize_url(url: str) -> str:
    url = url.split("&t=")[0]
    url = url.split("?t=")[0]
    return url


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def move_final_file(tmp_dir: Path, dest_dir: Path, base_filename: str) -> Path | None:
    for ext in (".mkv", ".mp4", ".webm"):
        candidate = tmp_dir / f"{base_filename}{ext}"
        if candidate.exists():
            target = dest_dir / candidate.name
            shutil.move(str(candidate), str(target))
            return target
    return None


def cleanup_extras(tmp_dir: Path, base_filename: str):
    for ext in (".srt", ".vtt"):
        for f in tmp_dir.glob(f"{base_filename}*{ext}"):
            try:
                f.unlink()
            except Exception:
                pass
    for f in tmp_dir.glob(f"{base_filename}*.*.part"):
        try:
            f.unlink()
        except Exception:
            pass


# === FORM ===
with st.form("download_form"):
    url = st.text_input("URL de la vidéo")
    filename = st.text_input("Nom de la vidéo (sans extension)")

    # sous-dossiers existants
    existing = list_subdirs(VIDEOS_FOLDER)
    options = ["/"] + existing
    video_subfolder = st.selectbox("Destination sous :", options, index=0)

    # sous-titres multiselect depuis env
    subs_selected = st.multiselect(
        "Sous-titres à intégrer (laisser vide pour aucun)",
        options=SUBTITLES_CHOICES,
        default=[],
        help="Codes langue yt-dlp (ex: en, fr, es).",
    )

    submitted = st.form_submit_button("Télécharger")

# === ACTION ===
if submitted:
    if not url or not filename:
        st.error("Veuillez fournir l’URL et le nom de fichier.")
        st.stop()

    # resolve dest dir
    dest_dir = (
        VIDEOS_FOLDER if video_subfolder == "/" else (VIDEOS_FOLDER / video_subfolder)
    )

    # create dirs
    ensure_dir(VIDEOS_FOLDER)
    ensure_dir(TMP_DOWNLOAD_FOLDER)
    ensure_dir(dest_dir)

    # build cmd
    clean_url = sanitize_url(url)
    base_output = filename  # sans extension

    cmd = [
        "yt-dlp",
        "--newline",
        "-o",
        str(TMP_DOWNLOAD_FOLDER / f"{base_output}.%(ext)s"),
        "--paths",
        f"home:{TMP_DOWNLOAD_FOLDER}",
        "--paths",
        f"temp:{TMP_DOWNLOAD_FOLDER}",
        "--merge-output-format",
        "mkv",
        "-f",
        "bv*+ba/b",
        "--format-sort",
        "res:4320,fps,codec:av01,codec:vp9.2,codec:vp9,codec:h264",
        "--embed-metadata",
        "--embed-thumbnail",
        "--no-write-thumbnail",
        "--embed-chapters",
        "--convert-thumbnails",
        "jpg",
        "--sponsorblock-remove",
        "all",
        "--ignore-errors",
        "--concurrent-fragments",
        "1",
        "--sleep-requests",
        "1",
        "--retries",
        "10",
        "--retry-sleep",
        "2",
    ]

    # sous-titres (si l’utilisateur en a choisi)
    if subs_selected:
        langs_csv = ",".join(subs_selected)
        cmd += [
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            langs_csv,
            "--convert-subs",
            "srt",
            "--embed-subs",
        ]

    # cookies
    if os.path.isfile(YOUTUBE_COOKIES_FILE_PATH):
        cmd += ["--cookies", YOUTUBE_COOKIES_FILE_PATH]

    cmd += [clean_url]

    # UI progress
    progress = st.progress(0, text="Préparation…")
    status = st.empty()
    logs_box = st.empty()

    try:
        with subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        ) as proc:
            full_log = []
            for line in proc.stdout:
                line = line.rstrip("\n")
                full_log.append(line)
                logs_box.code("\n".join(full_log[-18:]), language="bash")

                m = re.search(r"(\d{1,3}\.\d)%", line) or re.search(r"(\d{1,3})%", line)
                if m:
                    try:
                        pct = float(m.group(1))
                        pct = min(100, pct)
                        progress.progress(int(pct), text=f"Téléchargement… {int(pct)}%")
                    except Exception:
                        pass
                else:
                    if "Downloading" in line:
                        status.info("Téléchargement…")
                    if "Merging formats" in line:
                        status.info("Fusion audio/vidéo…")
                    if "Embedding subtitles" in line:
                        status.info("Intégration des sous-titres…")

            ret = proc.wait()
    except Exception as e:
        st.error(f"Erreur d’exécution: {e}")
        st.stop()

    # post-process: cleanup + move
    if ret == 0:
        cleanup_extras(TMP_DOWNLOAD_FOLDER, base_output)
        final = move_final_file(TMP_DOWNLOAD_FOLDER, dest_dir, base_output)
        if final and final.exists():
            progress.progress(100, text="Terminé ✅")
            status.success(f"Fichier prêt : Videos/{video_subfolder}")
            st.toast("Téléchargement terminé", icon="✅")
        else:
            status.warning(
                "Téléchargement OK mais fichier final introuvable. Vérifie le dossier TMP."
            )
    else:
        status.error("yt-dlp a renvoyé une erreur. Regarde les logs ci-dessus.")
