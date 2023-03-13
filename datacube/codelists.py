import json
from dataclasses import dataclass

from rdflib import Graph, Literal
from rdflib.namespace import RDF, SKOS

from .config import COUNTIES_URL, REGIONS_URL
from .helpers import BASE_DIR, Resources
from .loader import load
from .namespace import CODE


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

    def load_data(self, regions_path: str, counties_path: str):
        """Load territorial units from files."""
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
        graph.parse(BASE_DIR / "rdf/territorial_units.ttl")
        self.add_counties(graph)
        self.add_regions(graph)
