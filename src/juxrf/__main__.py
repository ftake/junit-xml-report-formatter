import argparse
from .infra import TestSuiteRepository
from pathlib import Path
from .app import FormatAsHTMLService
import logging


def main():
    parser = argparse.ArgumentParser(
        prog="JUnit XML Report Formatter",
        description="Convert JUnit XML report to a printable format",
    )

    parser.add_argument("--srcdir")
    parser.add_argument("-o", "--output")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    repository = TestSuiteRepository(Path(args.srcdir))
    repository.load()
    service = FormatAsHTMLService(repository)
    service.format_report(Path(args.output))

    return 0


if __name__ == "__main__":
    main()
