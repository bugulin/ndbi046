import nox

@nox.session(tags=["code-style"])
def black(session):
    session.install("black")
    session.run("black", "datacube")

@nox.session(tags={"code-style"})
def isort(session):
    session.install("isort")
    session.run("isort", "datacube")

@nox.session(tags=["code-style"])
def mypy(session):
    session.install("mypy")
    session.run("mypy", "datacube")

@nox.session
def setup(session):
    """Test that the project can be installed and used."""
    session.install(".")
