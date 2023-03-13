import csv
import json
from dataclasses import dataclass

from importlib_resources import as_file, files
from rdflib import Graph, Literal
from rdflib.namespace import RDF, SKOS

from .config import COUNTIES_URL, MAPPING_101_109, REGIONS_URL
from .helpers import Resources
from .loader import load
from .namespace import CODE


class CodeList:
    """Enumeration of code lists."""

    KRAJ_NUTS = 100
    OKRES_NUTS = 101
    NUTS3_2004 = 108
    OKRES_LAU = 109


class Indicator:
    """Enumeration of indicator codes."""

    MEAN_POPULATION = "DEM0004"


class TerritorialUnits:
    """Hierarchical code list of territorial units."""

    @dataclass(slots=True, frozen=True)
    class County:
        title: dict[str, str]
        region: str

    @dataclass(slots=True, frozen=True)
    class Region:
        title: dict[str, str]

    _counties: dict[str, County] | None = None
    _regions: dict[str, Region] | None = None
    _mappings: dict[tuple[int, int], dict[str, str]] = {}

    def load_data(self, regions_path: str, counties_path: str):
        """Load territorial units from JSON files."""
        with open(regions_path) as fp:
            data = json.load(fp)
            self._regions = {
                item["kodNuts3"]: TerritorialUnits.Region(title=item["nazev"])
                for item in data["polozky"]
            }

        region_index = {item["id"]: item["kodNuts3"] for item in data["polozky"]}

        with open(counties_path) as fp:
            data = json.load(fp)
            self._counties = {
                item["kodLau"]: TerritorialUnits.County(
                    title=item["nazev"], region=region_index[item["kraj"]]
                )
                for item in data["polozky"]
            }

    def _load_default_data(self):
        self.load_data(load(REGIONS_URL), load(COUNTIES_URL))

    def load_mapping_table(self, key: tuple[int, int], url: str) -> dict[str, str]:
        """Load code mapping table from a CSV file."""
        path = load(url, "MAP{}-{}.csv".format(*key))
        with open(path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            table = {row["chodnota1"]: row["chodnota2"] for row in reader}
            self._mappings[key] = table

        return table

    def add_counties(self, graph: Graph):
        if self._counties is None:
            self._load_default_data()

        assert self._counties is not None, "Counties not loaded."
        for code, county in self._counties.items():
            resource = Resources.get_county(code)
            graph.add((resource, RDF.type, SKOS.Concept))
            graph.add((resource, RDF.type, CODE.County))
            graph.add((resource, SKOS.inScheme, CODE.territorialUnit))
            graph.add((resource, SKOS.broader, Resources.get_region(county.region)))
            for lang, label in county.title.items():
                graph.add((resource, SKOS.prefLabel, Literal(label, lang=lang)))

    def add_regions(self, graph: Graph):
        if self._regions is None:
            self._load_default_data()

        assert self._regions is not None, "Regions not loaded."
        for code, region in self._regions.items():
            resource = Resources.get_region(code)
            graph.add((resource, RDF.type, SKOS.Concept))
            graph.add((resource, RDF.type, CODE.Region))
            graph.add((resource, SKOS.topConceptOf, CODE.territorialUnit))
            graph.add((resource, SKOS.inScheme, CODE.territorialUnit))
            for lang, label in region.title.items():
                graph.add((resource, SKOS.prefLabel, Literal(label, lang=lang)))

            graph.add((CODE.region, SKOS.hasTopConcept, resource))

    def add_to_graph(self, graph: Graph):
        """Add this code list to an RDF graph."""
        defs = files("datacube.rdf").joinpath("territorial_units.ttl")
        with as_file(defs) as path:
            graph.parse(path)
        self.add_counties(graph)
        self.add_regions(graph)

    def get_region_for(self, lau_code: str) -> str:
        """Get region that contains given county."""
        if self._counties is None:
            self._load_default_data()

        assert self._counties is not None, "Counties not loaded."
        return self._counties[lau_code].region

    def convert_code(self, code: str, direction: tuple[int, int]) -> str:
        """Convert territorial unit representation."""
        if (table := self._mappings.get(direction)) is None:
            if direction == (CodeList.OKRES_NUTS, CodeList.OKRES_LAU):
                table = self.load_mapping_table(direction, MAPPING_101_109)
            else:
                raise KeyError("Mapping table not found.")

        return table[code]
