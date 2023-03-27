from importlib_resources import files
from rdflib import Graph


def normalize(graph: Graph):
    """Apply a transformation algorithm which can normalize an abbreviated Data Cube."""

    normalization_script = files().joinpath("normalization.sparql")
    with normalization_script.open() as fp:
        buffer: list[str] = []
        prefixes: list[str] = []
        for line in fp:
            if line.startswith("PREFIX "):
                prefixes.append(line)
                continue

            buffer.append(line)
            if line.strip() == "};":
                graph.update("".join([*prefixes, *buffer]))
                buffer.clear()
