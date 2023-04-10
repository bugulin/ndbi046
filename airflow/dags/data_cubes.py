from pathlib import Path
from unittest import TextTestRunner

from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.exceptions import AirflowSkipException
from airflow.models.param import Param
from pendulum import datetime, now
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import PROV, RDF, XSD

from datacube import CareProviders, Population, TerritorialUnits
from datacube.config import (
    CARE_PROVIDERS_URL,
    COUNTIES_URL,
    DATA_DIR,
    POPULATION_2021_URL,
    REGIONS_URL,
)
from datacube.helpers import save
from datacube.namespace import RESOURCE
from datacube.well_formed import IntegrityConstraintsFactory

CODELIST_FILENAME = "codelist.ttl"
HEALTH_CARE_FILENAME = "health_care.ttl"
POPULATION_FILENAME = "population.ttl"
PROVENANCE_FILENAME = "provenance.trig"  # Make sure the file extension matches the format passed to rdflib.Graph.serialize

care_providers_dataset = Dataset(
    CARE_PROVIDERS_URL,
    extra={"filename": "care-providers.csv", "force_download": True},
)
population_dataset = Dataset(
    POPULATION_2021_URL,
    extra={"filename": "population-2021.csv", "force_download": True},
)
regions_dataset = Dataset(REGIONS_URL)
counties_dataset = Dataset(COUNTIES_URL)


@dag(
    dag_id="data-cubes",
    schedule=None,
    catchup=False,
    start_date=datetime(2023, 3, 22),
    tags=["NDBI046"],
    params={
        "output_path": Param(
            str(Path.cwd()),
            type="string",
            title="Output path",
        ),
        "provenance": Param(
            None,
            type=["string", "null"],
            title="Input provenance path",
        ),
    },
)
def data_cubes():
    """
    ### Data cubes

    DAG that produces both data cubes from the
    [first assignment](https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/02-data-cube.html#/3).

    Parameter | Description
    ---|---
    `output_path`&emsp; | Path where to save output files to. Defaults to current working directory. The directory must exist, otherwise tasks will fail.
    `provenance` | Path to provenance file. This file will be enriched by dataset generation timestamps and output files locations. When set to `null` (default), no provenance file will be generated.
    """

    @task()
    def retrieve(src: Dataset) -> str:
        """
        #### Retrieve task
        A simple task to make data available for the rest of the pipeline by downloading it from
        given URL.
        """
        filename = src.extra.get("filename") if src.extra else None
        force_download = src.extra.get("force_download", False) if src.extra else False
        path = save(src.uri, filename, force_download).absolute()
        return str(path)

    @task()
    def make_codelist(
        regions_path: str,
        counties_path: str,
        output_path: Path = DATA_DIR / CODELIST_FILENAME,
    ) -> str:
        """
        #### Code list task
        A task that generates an RDF graph with code lists and saves it to a file for future use.
        """
        obj = TerritorialUnits()
        obj.load_data(regions_path, counties_path)

        graph = Graph()
        obj.add_to_graph(graph)
        graph.serialize(output_path)
        return str(output_path)

    @task(multiple_outputs=True)
    def make_health_care(
        src_path: str, codelist_path: str, **context
    ) -> dict[str, str]:
        """
        #### Health care task
        A task to create Care Providers data cube.
        """
        graph = Graph(base=RESOURCE)
        ds = CareProviders(src_path)
        ds.add_to_graph(graph)
        graph.parse(codelist_path)

        output_path = Path(context["params"]["output_path"]) / HEALTH_CARE_FILENAME
        graph.serialize(output_path, format="turtle")
        return {
            "datacube": ds.dataset,
            "file": output_path.absolute().as_uri(),
            "timestamp": str(now()),
        }

    @task(multiple_outputs=True)
    def make_population(src_path: str, codelist_path: str, **context) -> dict[str, str]:
        """
        #### Population task
        A task to create Population data cube.
        """
        graph = Graph(base=RESOURCE)
        ds = Population(src_path)
        ds.add_to_graph(graph)
        graph.parse(codelist_path)

        output_path = Path(context["params"]["output_path"]) / POPULATION_FILENAME
        graph.serialize(output_path, format="turtle")
        return {
            "datacube": ds.dataset,
            "file": output_path.absolute().as_uri(),
            "timestamp": str(now()),
        }

    @task()
    def validate(path: str):
        """
        #### Validation task
        A task to validate that a data cube is well-formed.
        """
        factory = IntegrityConstraintsFactory()
        factory.load_graph(path)
        suite = factory.get_test_suite()
        result = TextTestRunner().run(suite)

        assert result.wasSuccessful(), "The produced data cube is not well-formed."

    @task()
    def create_provenance(*datasets: dict, **context):
        """
        #### Provenance task
        A task to create provenance document using PROV-O.
        """
        graph = Graph()
        provenance = context["params"].get("provenance")
        if provenance is None:
            raise AirflowSkipException("no provenance")
        graph.parse(provenance)

        for ds in datasets:
            cube_res = URIRef(ds["datacube"])
            file_res = URIRef(ds["file"])
            timestamp = Literal(ds["timestamp"], datatype=XSD.dateTime)
            graph.add((cube_res, PROV.atLocation, file_res))
            graph.add((cube_res, PROV.generatedAtTime, timestamp))
            graph.add((file_res, RDF.type, PROV.Location))

        output_path = Path(context["params"]["output_path"]) / PROVENANCE_FILENAME
        graph.serialize(output_path, format="trig")

    data_cp = retrieve(care_providers_dataset)
    data_p = retrieve(population_dataset)
    data_tu1 = retrieve(regions_dataset)
    data_tu2 = retrieve(counties_dataset)

    codelist = make_codelist(data_tu1, data_tu2)

    output1 = make_health_care(data_cp, codelist)
    output2 = make_population(data_p, codelist)

    validate(output1["file"])
    validate(output2["file"])
    create_provenance(output1, output2)


data_cubes()
