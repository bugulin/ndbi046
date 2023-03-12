import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, QB, RDF, RDFS, SKOS, XSD

from .config import PUBLISHER
from .namespace import CODE, ONTOLOGY, RESOURCE, SDMX_SUBJECT

BASE_DIR = Path(__file__).parent


class Resources:
    """Generate resource IRIs."""

    @staticmethod
    def get_dataset(name: str) -> URIRef:
        return RESOURCE[f"dataset/{name}"]

    @staticmethod
    def get_region(nuts_code: str) -> URIRef:
        return RESOURCE[f"region/{nuts_code}"]

    @staticmethod
    def get_county(lau_code: str) -> URIRef:
        return RESOURCE[f"county/{lau_code}"]

    @staticmethod
    def get_field_of_care(field_id: int) -> URIRef:
        return RESOURCE[f"field-of-care/{field_id:03d}"]

    @staticmethod
    def get_observation(obs_id: int, dataset: URIRef) -> URIRef:
        return URIRef(f"obs-{obs_id:05d}", dataset)


class CareProviders:
    """Care Providers dataset."""

    _fields_of_care: dict[str, int] = {}
    _observation_count: int = 0

    dataset = Resources.get_dataset("careproviders/")
    title = {
        "en": "Care Providers",
        "cs": "Poskytovatelé zdravotních služeb",
    }
    description = {
        "en": "Number of care providers within counties.",
        "cs": "Počet poskytovatelů zdravotních služeb v okresech.",
    }

    @dataclass(slots=True, frozen=True)
    class Dimensions:
        """Dimensions of Care Providers data cube."""

        county: str
        region: str
        field_of_care: int

    def __init__(self, path: str):
        self.src_path = path

    def _add_dataset(self, graph: Graph):
        issued = Literal(date.today().isoformat(), datatype=XSD.date)
        license_res = URIRef(
            "https://creativecommons.org/share-your-work/public-domain/pdm/"
        )

        graph.add((self.dataset, RDF.type, QB.DataSet))
        for predicate in [RDFS.label, DCTERMS.title]:
            for lang, title in self.title.items():
                graph.add((self.dataset, predicate, Literal(title, lang=lang)))
        for predicate in [RDFS.comment, DCTERMS.description]:
            for lang, description in self.description.items():
                graph.add((self.dataset, predicate, Literal(description, lang=lang)))
        graph.add((self.dataset, QB.structure, ONTOLOGY.CareProvidersStructure))
        graph.add((self.dataset, DCTERMS.issued, issued))
        graph.add((self.dataset, DCTERMS.publisher, URIRef(PUBLISHER)))
        graph.add((self.dataset, DCTERMS.license, license_res))
        # Health
        graph.add((self.dataset, DCTERMS.subject, SDMX_SUBJECT["1.4"]))
        # Regional and small area statistics
        graph.add((self.dataset, DCTERMS.subject, SDMX_SUBJECT["3.2"]))

    def _add_observation(self, graph: Graph, dimensions: Dimensions, measure: int):
        resource = Resources.get_observation(self._observation_count, self.dataset)
        graph.add((resource, RDF.type, QB.Observation))
        graph.add((resource, QB.dataSet, self.dataset))
        graph.add((resource, ONTOLOGY.region, Resources.get_region(dimensions.region)))
        graph.add((resource, ONTOLOGY.county, Resources.get_county(dimensions.county)))
        graph.add(
            (
                resource,
                ONTOLOGY.fieldOfCare,
                Resources.get_field_of_care(dimensions.field_of_care),
            )
        )
        graph.add(
            (
                resource,
                ONTOLOGY.numberOfCareProviders,
                Literal(measure, datatype=XSD.integer),
            )
        )

        self._observation_count += 1

    def _add_field_of_care(self, graph: Graph, title: str, field_id: int):
        resource = Resources.get_field_of_care(field_id)
        graph.add((resource, RDF.type, SKOS.Concept))
        graph.add((resource, RDF.type, CODE.FieldOfCare))
        graph.add((resource, SKOS.topConceptOf, CODE.fieldOfCare))
        graph.add((resource, SKOS.prefLabel, Literal(title, lang="cs")))
        graph.add((resource, SKOS.inScheme, CODE.fieldOfCare))

        graph.add((CODE.fieldOfCare, SKOS.hasTopConcept, resource))

    def _get_field_of_care_id(self, title: str) -> int:
        if not (field := self._fields_of_care.get(title)):
            field = len(self._fields_of_care)
            self._fields_of_care[title] = field

        return field

    def add_to_graph(self, graph: Graph):
        """Add this dataset to an RDF graph."""

        # Load data from a file
        data: dict[CareProviders.Dimensions, int] = {}
        with open(self.src_path, newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                key = CareProviders.Dimensions(
                    county=row["OkresCode"],
                    region=row["KrajCode"],
                    field_of_care=self._get_field_of_care_id(row["OborPece"].lower()),
                )
                data[key] = data.get(key, 0) + 1

        # Add data to the graph
        graph.parse(BASE_DIR / "rdf/care_providers.ttl")
        self._add_dataset(graph)
        for foc in self._fields_of_care.items():
            self._add_field_of_care(graph, *foc)
        for obs in data.items():
            self._add_observation(graph, *obs)
