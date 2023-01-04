from .dom import AbstractTestSuiteRepository, TestSuite
from pathlib import Path
from typing import TextIO


class FormatAsHTMLService:
    def __init__(self, repository: AbstractTestSuiteRepository) -> None:
        self._repository = repository

    def format_report(self, output_file: Path):
        with open(output_file, "w", encoding="utf8") as f:
            self._write_header(f)
            for ts in self._repository.lists_test_suite():
                if not ts.is_nested:
                    self._write_test_suite(ts, 2, f)
            self._write_footer(f)

    def _write_header(self, f: TextIO) -> None:
        print("<!DOCTYPE html>", file=f)
        print("<html>", file=f)
        print("<body>", file=f)

    def _write_footer(self, f: TextIO) -> None:
        print("</body>", file=f)
        print("</html>", file=f)

    def _write_test_suite(self, test_suite: TestSuite, level: int, f: TextIO) -> None:
        print("<section>", file=f)
        print(f"<header><h{level}>{test_suite.name}</h{level}></header>", file=f)
        if len(test_suite.test_cases) > 0:
            print("<ul>", file=f)
            for tc in test_suite.test_cases:
                print(f"<li>{tc.name}</li>", file=f)
            print("</ul>", file=f)

        for ts in test_suite.nested:
            self._write_test_suite(ts, level + 1, f)

        print("</section>", file=f)
