from os.path import basename
from pathlib import Path

import requests

from .config import DATA_DIR


def load(url: str, filename: str | None = None, force_download: bool = False) -> Path:
    """Save remote file to the data directory, if it's not already there."""
    DATA_DIR.mkdir(exist_ok=True)

    output_path = DATA_DIR / (filename if filename else basename(url))
    if force_download or not output_path.exists():
        r = requests.get(url, stream=True)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=4096):
                f.write(chunk)

    return output_path
