import json

import nox

src_dirs = ["datacube", "airflow/dags"]


@nox.session(tags=["code-style"])
def black(session):
    session.install("black")
    session.run("black", *src_dirs)


@nox.session(tags={"code-style"})
def isort(session):
    session.install("isort")
    session.run("isort", *src_dirs)


@nox.session(tags=["code-style"])
@nox.parametrize("airflow", ["2.5.1"])
@nox.parametrize("python", ["3.10"])
def mypy(session, airflow, python):
    # Avoid expensive installation when possible
    installed_packages = {
        package["name"]
        for package in json.loads(
            session.run("pip", "list", "--format=json", silent=True)
        )
    }
    if "mypy" not in installed_packages:
        session.install("-e", ".")
        session.install("mypy", "types-requests")
        session.install(
            f"apache-airflow=={airflow}",
            "--constraint=https://raw.githubusercontent.com/apache/airflow/"
            f"constraints-{airflow}/constraints-{python}.txt",
        )
    else:
        session.debug("Skipping installation of dependencies.")

    session.run("mypy", *src_dirs)


@nox.session
def setup(session):
    """Test that the project can be installed and used."""
    session.install(".")
    session.run("datacube", "generate", "care-providers", silent=True)
