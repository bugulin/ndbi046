# Introduction to Data Engineering <sup>[NDBI046]</sup>

Command to create the first data cube:
```console
datacube generate care-providers regions+counties
```

Command to create the second data cube:
```console
datacube generate population-2021 regions+counties
```

Command for data cubes validation using integrity constraints:
```console
datacube validate FILE
```

## System requirements

* Python3 (>=3.10)
* Internet connection (to download dependencies and datasets)

## Installation instructions

Simply put, run following command in the root directory of this repository:

```console
pip install .
```

Then you are free to use the `datacube` utility – just type `datacube --help`
for more information.

## Data sources

* [Národní registr poskytovatelů zdravotních služeb](https://data.gov.cz/datová-sada?iri=https://data.gov.cz/zdroj/datové-sady/https---opendata.mzcr.cz-api-3-action-package_show-id-nrpzs)
* [Pohyb obyvatel za ČR, kraje, okresy, SO ORP a obce - rok 2021](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00025593%2F12032e1445fd74fa08da79b14137fc29)
* [Kraje](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00551023%2F61963903d713a0173320878b215395f5)
* [Okresy](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00551023%2F04e0a699be153c780a0dde2c38dc3b13)
* [Vazba mezi číselníky ČSÚ: OKRES_NUTS (kód 101) - OKRES_LAU (kód 109)](https://data.gov.cz/datová-sada?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatové-sady%2F00025593%2Ffca64742da3a7acb284fe9591a563873)

The exact URLs of the data can be configured in [datacube/config.py](datacube/config.py).
