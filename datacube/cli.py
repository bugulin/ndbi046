import unittest

import click
from rdflib import Graph
from rdflib.namespace import DCTERMS

from .codelists import TerritorialUnits
from .config import CARE_PROVIDERS_URL, COUNTIES_URL, POPULATION_2021_URL, REGIONS_URL
from .datasets import CareProviders, Population
from .helpers import save
from .namespace import RESOURCE, SDMX_SUBJECT
from .well_formed import IntegrityConstraintsFactory


@click.group()
def main():
    pass


@main.command(
    short_help="Generate data cubes.",
    help="""Generate data cubes.\n
Currently available datasets are care-providers, population-2021 and regions+counties.""",
)
@click.option(
    "--format",
    default="turtle",
    help="Output format, e.g. turtle, pretty-xml, or trig.",
)
@click.argument("dataset", nargs=-1)
def generate(dataset, format):
    g = Graph(base=RESOURCE)
    g.bind("sdmx-subject", SDMX_SUBJECT)
    g.bind("dct", DCTERMS)

    for ds in dataset:
        if ds == "care-providers":
            cp = CareProviders(save(CARE_PROVIDERS_URL))
            cp.add_to_graph(g)
        elif ds == "population-2021":
            p = Population(save(POPULATION_2021_URL))
            p.add_to_graph(g)
        elif ds == "regions+counties":
            tu = TerritorialUnits()
            tu.load_data(save(REGIONS_URL), save(COUNTIES_URL))
            tu.add_to_graph(g)
        else:
            click.echo(f"[!] unknown dataset '{ds}'", err=True)

    click.echo_via_pager(g.serialize(format=format))


@main.command(help="Validate data cubes.")
@click.argument("file", nargs=-1, type=click.Path(dir_okay=False))
@click.option("-v", "--verbose", is_flag=True, help="Make unittest more talkative.")
@click.pass_context
def validate(ctx, verbose, file):
    factory = IntegrityConstraintsFactory()
    for f in file:
        factory.load_graph(f)
    suite = factory.get_test_suite()
    result = unittest.TextTestRunner(verbosity=2 if verbose else 1).run(suite)

    if not result.wasSuccessful():
        ctx.exit(1)


if __name__ == "__main__":
    main()
