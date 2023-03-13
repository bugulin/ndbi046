import re
import unittest
from dataclasses import dataclass, field
from enum import Enum
from typing import Type

import rdflib
from importlib_resources import files
from rdflib.namespace import QB, RDF, SKOS


class ParserPhase(int, Enum):
    DOCS = 0
    QUERY = 1


@dataclass
class ParserState:
    test_name: str = ""
    docstring: list[str] = field(default_factory=list)
    queries: list[list[str]] = field(default_factory=list)
    phase: ParserPhase = ParserPhase.QUERY


class IntegrityConstrains(unittest.TestCase):
    """
    Test case for integrity constraints of well-formed data cubes.
    :see: https://www.w3.org/TR/vocab-data-cube/#wf-rules
    """

    graph = rdflib.Graph()  # Shared between all test runs (for better performance)
    namespace = {
        "rdf": RDF,
        "skos": SKOS,
        "qb": QB,
    }

    @classmethod
    def add_graph(cls: Type, path: str):
        cls.graph.parse(path)
        cls._normalize_graph()

    @classmethod
    def _normalize_graph(cls: Type):
        normalization_script = files("datacube.tests").joinpath("normalization.sparql")
        with normalization_script.open() as fp:
            buffer: list[str] = []
            for line in fp:
                buffer.append(line)
                if line.strip() == "};":
                    cls.graph.update("".join(buffer), initNs=cls.namespace)
                    buffer.clear()

    def test_ic20(self):
        """
        IC-20. Codes from hierarchy

        If a dimension property has a qb:HierarchicalCodeList with a non-blank
        qb:parentChildProperty then the value of that dimension property on every qb:Observation
        must be reachable from a root of the hierarchy using zero or more hops along the
        qb:parentChildProperty links.
        """
        ps = self.graph.query(
            """
            SELECT ?p WHERE {
                ?hierarchy a qb:HierarchicalCodeList ;
                             qb:parentChildProperty ?p .
                FILTER ( isIRI(?p) )
            }
            """,
            initNs=self.namespace,
        )
        for p in ps:
            query = self.graph.query(
                f"""
                ASK {{
                    ?obs qb:dataSet/qb:structure/qb:component/qb:componentProperty ?dim .
                    ?dim a qb:DimensionProperty ;
                        qb:codeList ?list .
                    ?list a qb:HierarchicalCodeList .
                    ?obs ?dim ?v .
                    FILTER NOT EXISTS {{ ?list qb:hierarchyRoot/<{p}>* ?v }}
                }}
                """,
                initNs=self.namespace,
            )
            self.assertFalse(query)

    def test_ic21(self):
        """
        IC-21. Codes from hierarchy (inverse)

        If a dimension property has a qb:HierarchicalCodeList with an inverse qb:parentChildProperty
        then the value of that dimension property on every qb:Observation must be reachable from
        a root of the hierarchy using zero or more hops along the inverse qb:parentChildProperty
        links.
        """

        ps = self.graph.query(
            """
            SELECT ?p WHERE {
                ?hierarchy a qb:HierarchicalCodeList;
                             qb:parentChildProperty ?pcp .
                FILTER( isBlank(?pcp) )
                ?pcp  owl:inverseOf ?p .
                FILTER( isIRI(?p) )
            }
            """,
            initNs=self.namespace,
        )
        for p in ps:
            query = self.graph.query(
                f"""
                ASK {{
                    ?obs qb:dataSet/qb:structure/qb:component/qb:componentProperty ?dim .
                    ?dim a qb:DimensionProperty ;
                         qb:codeList ?list .
                    ?list a qb:HierarchicalCodeList .
                    ?obs ?dim ?v .
                    FILTER NOT EXISTS {{ ?list qb:hierarchyRoot/(^<{p}>)* ?v }}
                }}
                """,
                initNs=self.namespace,
            )
            self.assertFalse(query)


class IntegrityConstraintsFactory:
    """Test factory that loads tests from a definition file."""

    test_head = re.compile(r"^(?:# )(?P<type>\w+)-(?P<id>\d+)\.")

    def __init__(self, template: Type = IntegrityConstrains):
        self.cls = template

    def load_file(self, path: str):
        """Load file with tests."""
        state = ParserState()
        with open(path) as f:
            for line in f:
                self._parse_line(line.rstrip(), state)
            self._parse_line("# EOF-0.", state)  # termination token

    def load_graph(self, path: str):
        """Set which graph to test."""
        self.cls.add_graph(path)

    def get_test_suite(self):
        """Get test suite with all the generated tests."""
        return unittest.TestSuite(unittest.makeSuite(self.cls))

    def add_query_test(self, name: str, docstring: str, queries: list[str]):
        """Register a test that executes a SPARQL query."""

        @unittest.skipIf(len(queries) == 0, "not an automated test")
        def test(testcase_self):
            for query in queries:
                ret = testcase_self.graph.query(query, initNs=testcase_self.namespace)
                testcase_self.assertFalse(ret.askAnswer)

        test.__doc__ = docstring

        setattr(self.cls, name, test)

    def _parse_line(self, line: str, state: ParserState):
        if state.phase == ParserPhase.QUERY:
            if match := self.test_head.match(line):
                self.add_query_test(
                    name=state.test_name,
                    docstring="\n".join(state.docstring),
                    queries=["\n".join(query) for query in state.queries],
                )
                state.test_name = self._get_test_name(match)
                state.queries.clear()
                state.docstring.clear()
                state.phase = ParserPhase.DOCS
            else:
                if line.startswith("ASK"):
                    state.queries.append([])
                state.queries[-1].append(line)

        if state.phase == ParserPhase.DOCS:
            if len(line) == 0:
                state.phase = ParserPhase.QUERY
            elif line.startswith("# "):
                state.docstring.append(line[2:])

    @staticmethod
    def _get_test_name(match: re.Match):
        return "test_{}{:02d}".format(
            match.group("type").lower(), int(match.group("id"))
        )
