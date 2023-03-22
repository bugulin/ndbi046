from os.path import basename
from pathlib import Path

import requests
from rdflib import URIRef

from .config import DATA_DIR
from .namespace import CODE, RESOURCE


class Resources:
    """Generate resource IRIs."""

    @staticmethod
    def get_dataset(name: str) -> URIRef:
        return RESOURCE[f"dataset/{name}"]

    @staticmethod
    def get_region(nuts_code: str) -> URIRef:
        return CODE[nuts_code]

    @staticmethod
    def get_county(lau_code: str) -> URIRef:
        return CODE[lau_code]

    @staticmethod
    def get_field_of_care(field_id: int) -> URIRef:
        return RESOURCE[f"field-of-care/{field_id:03d}"]

    @staticmethod
    def get_observation(obs_id: int, dataset: URIRef) -> URIRef:
        return URIRef(f"obs-{obs_id:05d}", dataset)


def save(url: str, filename: str | None = None, force_download: bool = False) -> Path:
    """Save remote file to the data directory, if it's not already there."""
    DATA_DIR.mkdir(exist_ok=True)

    output_path = DATA_DIR / (filename if filename else basename(url))
    if force_download or not output_path.exists():
        r = requests.get(url, stream=True)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=4096):
                f.write(chunk)

    return output_path
