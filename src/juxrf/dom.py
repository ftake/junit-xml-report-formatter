from datetime import datetime
from dataclasses import dataclass


@dataclass
class TestCase:
    name: str
    classname: str
    time: float


@dataclass
class TestSuite:
    name: str
    timestamp: datetime | None
    hostname: str | None
    time: float | None
    system_out: str
    system_err: str
    test_cases: list[TestCase]
    nested: list["TestSuite"]

    @property
    def is_nested(self) -> bool:
        return get_outer_class_name(self.name) is not None


def get_outer_class_name(fqcn: str) -> str | None:
    dot_pos = fqcn.rfind(".")
    dollar_pos = fqcn.rfind("$")
    if dot_pos < dollar_pos:
        return fqcn[:dollar_pos]
    else:
        return None


class AbstractTestSuiteRepository:
    def lists_test_suite(self) -> list[TestSuite]:
        return []

    def find_by_name(self, class_name: str) -> TestSuite | None:
        return None
