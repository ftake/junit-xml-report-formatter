from .dom import AbstractTestSuiteRepository, TestSuite, TestCase, get_outer_class_name
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

import logging


class TestSuiteRepository(AbstractTestSuiteRepository):
    def __init__(self, src_dir: Path) -> None:
        super().__init__()
        self._test_suites: dict[str, TestSuite] = {}
        self._logger = logging.getLogger("repository")
        self._src_dir = src_dir

    def load(self):
        for f in self._src_dir.glob("**/*.xml"):
            if f.is_file:
                self._load_file(f)

        self._build_nested_test_suite_def()

    def _load_file(self, path: Path):
        self._logger.debug(f"Loading: {path}")
        try:
            dom = ET.parse(path)
            testsuite_tag = dom.getroot()

            if testsuite_tag.tag != "testsuite":
                raise InvalidDocumentError()

            # test cases
            test_cases = self._find_test_cases(testsuite_tag)

            # test suites
            name = testsuite_tag.attrib["name"]
            timestamp = datetime.fromisoformat(testsuite_tag.attrib["timestamp"])
            hostname = testsuite_tag.attrib["hostname"]
            time = float(testsuite_tag.attrib["time"])

            system_out_tag = testsuite_tag.find("system-out")
            if system_out_tag is not None and system_out_tag.text is not None:
                system_out = system_out_tag.text
            else:
                system_out = ""

            system_err_tag = testsuite_tag.find("system-err")
            if system_err_tag is not None and system_err_tag.text is not None:
                system_err = system_err_tag.text
            else:
                system_err = ""

            test_suite = TestSuite(
                name, timestamp, hostname, time, system_out, system_err, test_cases, []
            )
            self._test_suites[name] = test_suite

        except IOError:
            self._logger.error("Error while loading file: %s", path)
        except Exception:
            self._logger.error("Unexpected test report file: %s", path)

    def _find_test_cases(self, testsuite_tag: ET.Element) -> list[TestCase]:
        result = []
        for testcase_tag in testsuite_tag.findall("./testcase"):
            name = testcase_tag.attrib["name"]
            classname = testcase_tag.attrib["classname"]
            time = float(testcase_tag.attrib["time"])
            testcase = TestCase(name, classname, time)
            result.append(testcase)
        return result

    def _build_nested_test_suite_def(self):
        test_suites = list(self._test_suites.values())
        for test_suite in test_suites:
            while True:
                outer_class_name = get_outer_class_name(test_suite.name)
                if outer_class_name:
                    outer_test_suite = self.find_by_name(outer_class_name)
                    if not outer_test_suite:
                        # If a test class has only nested classes and no test method,
                        # there is no XML file generated for the test class.
                        outer_test_suite = TestSuite(
                            outer_class_name, None, None, None, "", "", [], [test_suite]
                        )
                        self._test_suites[outer_class_name] = outer_test_suite
                        test_suite = outer_test_suite
                    else:
                        outer_test_suite.nested.append(test_suite)
                        break
                else:
                    # No more outer class
                    break

    def lists_test_suite(self) -> list[TestSuite]:
        return list(self._test_suites.values())

    def find_by_name(self, class_name: str) -> TestSuite | None:
        return self._test_suites.get(class_name)


class InvalidDocumentError(RuntimeError):
    pass
