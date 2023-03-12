from pathlib import Path
from typing import Annotated

DATA_DIR: Annotated[Path, "Path where to save downloaded files."] = Path(".data/")
