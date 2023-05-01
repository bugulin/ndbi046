# Introduction to Data Engineering

Homework repository for the Introduction to Data Engineering (NDBI046) course.


## Data cubes

Python package for creation and validation of data cubes.

### System requirements

* Python3 (3.10+)
* Internet connection (to download dependencies and datasets)

### Installation instructions

Simply put, run following command in the root directory of this repository:

```console
$ pip install .
```

After the command succeeds, you should be able to use the `datacube` utility
– try `datacube --help` for more information.

### Usage

Command to create the first data cube:
```console
$ datacube generate care-providers regions+counties
```

Command to create the second data cube:
```console
$ datacube generate population-2021 regions+counties
```

Command for data cubes validation using integrity constraints:
```console
$ datacube validate FILE
```


## Deploy to Apache Airflow

Yes, you can deploy the data cube creation process to Apache Airflow! All you
need to do is install the `ndbi046` package and merge
[airflow/dags](airflow/dags) directory with your `dags_folder`.

```console
$ pip install git+https://github.com/bugulin/ndbi046.git
$ [ -n "${AIRFLOW_HOME+x}" ] && wget -P "$AIRFLOW_HOME/dags" https://raw.githubusercontent.com/bugulin/ndbi046/main/airflow/dags/data_cubes.py
```

The DAG scripts were tested with Python 3.10 and Apache Airflow 2.5.1.

For information about Apache Airflow configuration and deployment, see
[Apache Airflow documentation](https://airflow.apache.org/docs/apache-airflow/stable/index.html).


## Provenance

A provenance document can be automatically generated when using Apache Airflow
deployment described above. Just download the
[provenance definition file](assets/provenance.ttl) and link it as `provenance`
parameter of the _data-cubes_ DAG (using _Trigger DAG w/ config_ in Airflow's
web interface). After triggering the DAG, the provenance document should show up
as `provenance.trig` file in the `output_path` directory.

By default (when no `provenance` parameter passed), the provenance document
creation task is skipped.


## Metadata

Territorial units code list is described using a SKOS hierarchy. This separate
concept scheme can be obtained by following command:

```console
$ datacube generate regions+counties
```

Population 2021 dataset metadata are located in
[assets/population.metadata.ttl](assets/population.metadata.ttl).


## Data sources

* [Národní registr poskytovatelů zdravotních služeb](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00024341%2Faa4c99d9f1480cca59807389cf88d4dc)
* [Pohyb obyvatel za ČR, kraje, okresy, SO ORP a obce - rok 2021](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00025593%2F12032e1445fd74fa08da79b14137fc29)
* [Kraje](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00551023%2F61963903d713a0173320878b215395f5)
* [Okresy](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00551023%2F04e0a699be153c780a0dde2c38dc3b13)
* [Vazba mezi číselníky ČSÚ: OKRES_NUTS (kód 101) - OKRES_LAU (kód 109)](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00025593%2Ffca64742da3a7acb284fe9591a563873)

The exact URLs used can be configured in [datacube/config.py](datacube/config.py).
