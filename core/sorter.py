"""
Natural File Sorting and Filtering Engine
Handles proper numerical ordering (e.g. part1, part2, ... part10) and format filtering.
"""

import re
from pathlib import Path
from typing import List, Union

SUPPORTED_EXTENSIONS = {
    ".mp4", ".ts", ".mkv", ".mov", ".avi", ".webm",
    ".flv", ".wmv", ".m4v", ".mts", ".m2ts", ".vob", ".3gp"
}


def natural_sort_key(s: Union[str, Path]):
    """Key for natural alphanumeric sorting (e.g. video_2 comes before video_10)."""
    text = str(s.name if isinstance(s, Path) else s)
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", text)]


def is_html_or_empty_file(file_path: Path) -> bool:
    """Check if file is empty or an HTML document (e.g. Google Drive quota / login error)."""
    try:
        if not file_path.is_file() or file_path.stat().st_size == 0:
            return True
        with open(file_path, "rb") as f:
            head = f.read(1024).strip().lower()
            if head.startswith(b"<!doctype html") or head.startswith(b"<html") or b"<head" in head or b"<body" in head or b"google drive" in head:
                return True
    except Exception:
        pass
    return False


def filter_video_files(paths: List[Path]) -> List[Path]:
    """Filter files by supported video extensions and valid content."""
    valid = []
    for p in paths:
        if not p.is_file() or p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if is_html_or_empty_file(p):
            print(f"⚠️ Skipping non-video/corrupted file '{p.name}' (HTML error page or 0 bytes).")
            continue
        valid.append(p)
    return valid


def sort_files(files: List[Path], sort_mode: str = "natural", reverse: bool = False) -> List[Path]:
    """
    Sort files according to specified mode:
    - 'natural': Alphanumeric natural order (video_1, video_2, video_10)
    - 'alphabetical': Standard string sort
    - 'date': Modification time (oldest first)
    - 'size': File size (smallest first)
    """
    if sort_mode == "natural":
        sorted_list = sorted(files, key=natural_sort_key)
    elif sort_mode == "alphabetical":
        sorted_list = sorted(files, key=lambda f: f.name.lower())
    elif sort_mode == "date":
        sorted_list = sorted(files, key=lambda f: f.stat().st_mtime)
    elif sort_mode == "size":
        sorted_list = sorted(files, key=lambda f: f.stat().st_size)
    else:
        sorted_list = list(files)
        
    if reverse:
        sorted_list.reverse()
    return sorted_list
