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

COUNTIES_URL: Annotated[
    str, "URL of a list of counties."
] = "https://data.mpsv.cz/od/soubory/ciselniky/okresy.json"

MAPPING_101_109: Annotated[
    str, "URL of code list 101 to 109 mapping."
] = "https://apl.czso.cz/iSMS/do_cis_export?kodcis=101&typdat=1&cisvaz=109_886&cisjaz=203&format=2&separator=%2C"

POPULATION_2021_URL: Annotated[
    str, "URL of the Population 2021 dataset."
] = "https://www.czso.cz/documents/10180/184344914/130141-22data2021.csv"

REGIONS_URL: Annotated[
    str, "URL of a list of regions."
] = "https://data.mpsv.cz/od/soubory/ciselniky/kraje.json"
