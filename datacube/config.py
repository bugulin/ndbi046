from pathlib import Path
from typing import Annotated

BASE: Annotated[
    str, "Base path of local RDF data's IRIs."
] = "https://bugulin.github.io/ndbi046"

DATA_DIR: Annotated[Path, "Path where to save downloaded files."] = Path(".data/")

PUBLISHER: Annotated[
    str, "Publisher of the generated data cubes."
] = "https://bugulin.github.io/"


CARE_PROVIDERS_URL: Annotated[
    str, "URL of the Care Providers dataset."
] = "https://opendata.mzcr.cz/data/nrpzs/narodni-registr-poskytovatelu-zdravotnich-sluzeb.csv"
