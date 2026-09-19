# 🎬 Advanced Lossless Video Joiner

A high-performance, quality-preserving Python video joiner capable of merging multiple video formats—including **MP4**, **MPEG-TS (.ts)**, **Matroska (.mkv)**, **MOV**, **AVI**, and **WebM**—while keeping audio and video quality **100% intact**.

---

## 🌟 Key Highlights

- **100% Intact Quality (Mathematical Zero-Loss)**:
  - When input files have compatible codecs (e.g. H.264 / HEVC and AAC), the joiner uses **FFmpeg Direct Stream Copy (`-c copy`)** via concat demuxer.
  - No re-encoding or re-compression takes place. It joins gigabytes of video in seconds without losing a single pixel or audio sample.
- **Smart MPEG-TS Handling & Auto-Conversion**:
  - Automatically converts any downloaded `.ts` videos (MPEG Transport Streams from Google Drive or local files) to `.mp4` format first using fast lossless remuxing (`-c copy`), then merges all standardized `.mp4` videos together seamlessly.
  - Automatically regenerates clean timestamps (`+genpts`) and applies bitstream filters (`aac_adtstoasc`).
- **Visually Lossless Fallback (CRF 17 / x264)**:
  - If videos have mismatched resolutions (e.g., 1080p and 720p) or different codecs, attempting direct stream copy produces corrupted playback. The joiner automatically identifies stream mismatches and performs **smart canvas harmonization** (scaling with aspect ratio preservation) with **CRF 17** (visually transparent/indistinguishable from raw source).
- **Natural Numerical Sorting**:
  - Automatically sorts files intelligently (`part1.ts`, `part2.ts`, ..., `part10.ts` instead of `part1`, `part10`, `part2`).
- **Zero Third-Party Python Dependencies**:
  - Built purely on Python standard libraries (`subprocess`, `tkinter`, `pathlib`, `json`, `urllib`).
- **Automatic FFmpeg Management**:
  - Auto-detects existing FFmpeg installations (system PATH, WinGet, Chocolatey, Scoop, local bin).
  - Offers a one-click automatic download of official static FFmpeg if not already present.
- **Cloud Native & GitHub Actions Ready**:
  - Pre-configured GitHub Actions workflow to download videos directly from Google Drive and merge in the cloud without using your local bandwidth.
- **Guided Interactive Wizard & Flexible CLI**:
  - Interactive step-by-step CLI wizard and full command-line automation for servers and CI/CD.

#### Join specific video files losslessly:
```bash
python video_joiner.py -i clip1.ts clip2.mp4 clip3.mkv -o combined.mp4
```

#### Join all videos in a directory with natural sorting:
```bash
python video_joiner.py -d "C:/path/to/my_videos" -o "final_movie.mkv"
```

#### Join using wildcard patterns:
```bash
python video_joiner.py -i "part_*.ts" -o "merged_series.mp4"
```

#### Interactive Terminal Wizard:
```bash
python video_joiner.py
```
*(Guides you step-by-step through choosing files, inspecting stream compatibility, and joining).*

---

## ⚙️ Command-Line Options

| Option | Description |
| :--- | :--- |
| `-i`, `--input <files...>` | List of video file paths or glob patterns |
| `-d`, `--dir <folder>` | Folder containing video clips to merge |
| `-l`, `--list <file.txt>` | Text file with paths to video files (one per line) |
| `-o`, `--output <path>` | Destination file path (default: `joined_video.mp4`) |
| `-m`, `--mode <mode>` | `auto` (default, smart lossless), `copy` (force stream copy), `transcode` (force CRF transcode) |
| `--crf <0-51>` | Quality factor when transcoding (default: `17` - visually transparent; `0` = mathematically lossless) |
| `--preset <preset>` | x264 speed preset: `ultrafast`, `superfast`, `veryfast` (default), `faster`, `fast`, `medium`, `slow` |
| `--cache-dir <dir>` | Intermediate segment cache directory for resumable joins (default: `.video_cache/<output_name>`) |
| `--max-runtime <mins>` | Max runtime in minutes before saving checkpoint & auto-continuing (default: `330` / 5.5 hours) |
| `--sort <mode>` | `natural` (default), `alphabetical`, `date`, `size`, `none` |
| `--reverse` | Reverse input sorting order |
| `-y`, `--yes` | Overwrite output file without asking |
| `--download-ffmpeg` | Auto-download official static FFmpeg Essentials build |

---

## 🔍 How Quality Preservation Works

1. **Stream Probing (`ffprobe`)**:
   - Each input file is inspected for video codec, resolution, framerate, pixel format, audio codec, and sample rate.
2. **Compatibility Analysis**:
   - If all parameters match: **100% Lossless Stream Copy (`-c copy`)** is executed. Zero transcoding, zero generational loss, processing speed reaches `50x - 200x`.
   - If containers differ (e.g. `.ts` to `.mp4`): FFmpeg applies container bitstream filters (`aac_adtstoasc`) to ensure proper packet headers without touching compressed audio/video data.
   - If parameters differ: The tool seamlessly harmonizes resolution using letterboxing/padding (preventing any aspect ratio distortion) and encodes with `CRF 17` high fidelity.

---

## ☁️ GitHub Actions (Cloud Downloading & Lossless Merging)

You can run this video joiner directly in the cloud on **GitHub Actions**—no local FFmpeg, disk space, or high-bandwidth download needed on your personal machine!

### How to Run via GitHub Web UI

1. Push this repository to GitHub.
2. Go to the **Actions** tab in your repository.
3. In the left sidebar, click **🎬 Lossless Video Joiner from Google Drive**.
4. Click the **Run workflow** dropdown button on the right.
5. Fill in the input fields:
   - **Google Drive URL(s) or Folder Link**:
     - Paste one or more public Google Drive links (one per line, comma-separated, or space-separated).
     - Or paste a public Google Drive folder link (`https://drive.google.com/drive/folders/...`) to automatically merge all videos in that folder.
     - Or specify a file in the repo (e.g., `example_links.txt`).
   - **Output Merged Video Filename**: e.g., `merged_video.mp4` or `final_cut.mkv`.
   - **Join Mode**: `auto` (smart lossless copy), `copy` (strictly stream copy), or `transcode`.
   - **File Sorting Order**: `natural` (recommended), `alphabetical`, or `date`.
   - **Create a GitHub Release**: Check to automatically publish a GitHub Release with direct download links.
6. Click **Run workflow**.

### How to Run via GitHub CLI (`gh`)
```bash
gh workflow run join_videos.yml \
  -f video_urls="https://drive.google.com/file/d/FILE_ID_1/view
https://drive.google.com/file/d/FILE_ID_2/view" \
  -f output_filename="merged.mp4" \
  -f join_mode="auto"
```

### Multi-Group Batch Processing with Labels & Auto-Cooldown
You can provide multiple groups of video links inside a links file (like `example_links.txt`) or in the `video_urls` input, demarcated by labels:
```text
                 this is angel moy

https://drive.google.com/file/d/1ExampleFileIdPart1XXXXXXXXXXX/view?usp=sharing
https://drive.google.com/file/d/1ExampleFileIdPart2YYYYYYYYYYY/view?usp=sharing
https://drive.google.com/file/d/1ExampleFileIdPart3ZZZZZZZZZZZ/view?usp=sharing

                 this is angel moy

                 this is bonka koy

https://drive.google.com/file/d/1ExampleFileIdPart1XXXXXXXXXXX/view?usp=sharing
https://drive.google.com/file/d/1ExampleFileIdPart2YYYYYYYYYYY/view?usp=sharing
https://drive.google.com/file/d/1ExampleFileIdPart3ZZZZZZZZZZZ/view?usp=sharing

                 this is bonka koy

                 this is minka

https://drive.google.com/file/d/1ExampleFileIdPart1XXXXXXXXXXX/view?usp=sharing
https://drive.google.com/file/d/1ExampleFileIdPart2YYYYYYYYYYY/view?usp=sharing
https://drive.google.com/file/d/1ExampleFileIdPart3ZZZZZZZZZZZ/view?usp=sharing
```

**How GitHub Actions executes this:**
1. **Discovers Batches**: Automatically identifies `01-angel_moy`, `02-bonka_koy`, and `03-minka`.
2. **Sequential Matrix Execution (`max-parallel: 1`)**:
   - **Batch 1 (`angel_moy`)**: Merges into `angel_moy.mp4` and **immediately uploads** the artifact `01-angel_moy-<run_id>`.
   - **Auto-Cooldown (5 Minutes)**: Waits 300 seconds automatically to protect Google Drive quota limits.
   - **Batch 2 (`bonka_koy`)**: Auto-resumes, merges into `bonka_koy.mp4`, and **immediately uploads** the artifact `02-bonka_koy-<run_id>`.
   - **Auto-Cooldown (5 Minutes)**: Waits 300 seconds automatically.
   - **Batch 3 (`minka`)**: Auto-resumes, merges into `minka.mp4`, and **immediately uploads** the artifact `03-minka-<run_id>`.
   - Continues automatically until all batches are totally finished!

### Retrieving Your Merged Videos
- **Immediate Artifact Availability**: As soon as each video batch finishes merging, its artifact is uploaded and immediately available in the workflow **Artifacts** section—no need to wait for the subsequent batches to finish before downloading!
- **Releases**: If `upload_release` is enabled, each video is published to GitHub Releases for direct public download.
- **Step Summary**: Each completed batch writes full video stream details, duration, file size, and lossless confirmation to the GitHub Step Summary.

---

## 📋 Requirements
- Python 3.8 or higher.
- Windows, macOS, or Linux.
- FFmpeg (automatically configured in GitHub Actions, and auto-downloaded on Windows if missing locally).

