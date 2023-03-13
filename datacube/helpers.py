from rdflib import URIRef

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
