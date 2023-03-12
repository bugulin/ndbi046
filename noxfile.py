import json

import nox

src_dir = "datacube"


@nox.session(tags=["code-style"])
def black(session):
    session.install("black")
    session.run("black", src_dir)


@nox.session(tags={"code-style"})
def isort(session):
    session.install("isort")
    session.run("isort", src_dir)


@nox.session(tags=["code-style"])
def mypy(session):
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
    else:
        session.debug("Skipping installation of dependencies.")

    session.run("mypy", src_dir)


@nox.session
def setup(session):
    """Test that the project can be installed and used."""
    session.install(".")
