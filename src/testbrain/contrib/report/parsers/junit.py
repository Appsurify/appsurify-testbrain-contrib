import datetime
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa

from .. import utils
from ..models.junit import (
    JUnitTestCase,
    JUnitTestCaseResult,
    JUnitTestCaseStatus,
    JUnitTestSuite,
    JUnitTestSuiteProperty,
    JUnitTestSuites,
)
from .base import XMLReportParser


class JUnitReportParser(XMLReportParser):
    _test: JUnitTestSuites

    def __init__(self, xml):
        super().__init__(xml)
        self._test = JUnitTestSuites()

    @classmethod
    def from_root(cls, root: "etree.Element"):
        instance = super().from_root(root=root)
        return instance

    @property
    def result(self) -> JUnitTestSuites:
        return self._test

    def parse(self) -> JUnitTestSuites:
        self.read_root()
        self.read_testsuites()
        return self.result

    def read_root(self):
        if self._xml.tag == f"{self._namespace}testsuites":
            self._test = JUnitTestSuites(
                id=self._xml.attrib.get("id", ""),
                name=self._xml.attrib.get("name", ""),
                errors=self._xml.attrib.get("errors", 0),
                failures=self._xml.attrib.get("failures", 0),
                skipped=self._xml.attrib.get("skipped", 0),
                passed=self._xml.attrib.get("passed", 0),
                tests=self._xml.attrib.get("tests", 0),
                time=self._xml.attrib.get("time", 0.0),
            )

    def read_testsuites(self):
        if self._xml.tag == f"{self._namespace}testsuite":
            testsuite_elements = [
                self._xml,
            ]
        else:
            testsuite_elements = self._xml.findall(f"{self._namespace}testsuite")

        for testsuite_element in testsuite_elements:
            junit_testsuite = JUnitTestSuite(
                id=testsuite_element.attrib.get("id", ""),
                name=testsuite_element.attrib.get("name", ""),
                hostname=testsuite_element.attrib.get("hostname", ""),
                errors=testsuite_element.attrib.get("errors", 0),
                failures=testsuite_element.attrib.get("failures", 0),
                skipped=testsuite_element.attrib.get("skipped", 0),
                passed=testsuite_element.attrib.get("passed", 0),
                tests=testsuite_element.attrib.get("tests", 0),
                time=testsuite_element.attrib.get("time", 0.0),
                timestamp=utils.string_to_datetime(
                    testsuite_element.attrib.get("timestamp", "")
                ),
                system_out=testsuite_element.findtext(
                    f"{self._namespace}system-out", default=""
                ),
                system_err=testsuite_element.findtext(
                    f"{self._namespace}system-err", default=""
                ),
            )
            self._test.add_testsuite(junit_testsuite)

            testsuite_properties_element = testsuite_element.find(
                f"{self._namespace}properties"
            )
            if testsuite_properties_element is not None:
                for prop_element in testsuite_properties_element.findall(
                    f"{self._namespace}property"
                ):
                    junit_testsuite_property = JUnitTestSuiteProperty(
                        name=prop_element.attrib.get("name", ""),
                        value=prop_element.attrib.get("value", ""),
                    )
                    junit_testsuite.add_property(junit_testsuite_property)

            for testcase_element in testsuite_element.findall(
                f"{self._namespace}testcase"
            ):
                junit_testcase = self._parse_testcase(testcase_element)
                junit_testsuite.add_testcase(junit_testcase)

            junit_testsuite.update_statistics()

        self._test.update_statistics()

    def _parse_testcase(self, testcase_element: "etree.Element") -> JUnitTestCase:
        junit_testcase = JUnitTestCase(
            id=testcase_element.attrib.get("id", ""),
            name=testcase_element.attrib.get("name", ""),
            classname=testcase_element.attrib.get("classname", ""),
            file=testcase_element.attrib.get("file", ""),
            line=testcase_element.attrib.get("line", ""),
            time=testcase_element.attrib.get("time", 0.0),
            system_out=testcase_element.findtext(
                f"{self._namespace}system-out", default=""
            ),
            system_err=testcase_element.findtext(
                f"{self._namespace}system-err", default=""
            ),
        )

        junit_result = self._parse_testcase_result(testcase_element)
        junit_testcase.result = junit_result
        return junit_testcase

    @staticmethod
    def _parse_testcase_result(
        testcase_element: "etree.Element",
    ) -> JUnitTestCaseResult:
        skipped_element = testcase_element.find("skipped")
        failure_element = testcase_element.find("failure")
        error_element = testcase_element.find("error")

        if skipped_element is not None:
            junit_result = JUnitTestCaseResult(
                status=JUnitTestCaseStatus.skipped,
                type=skipped_element.attrib.get("type", ""),
                message=skipped_element.attrib.get("message", ""),
                stacktrace=skipped_element.text or "",
            )
        elif failure_element is not None:
            junit_result = JUnitTestCaseResult(
                status=JUnitTestCaseStatus.failure,
                type=failure_element.attrib.get("type", ""),
                message=failure_element.attrib.get("message", ""),
                stacktrace=failure_element.text or "",
            )
        elif error_element is not None:
            junit_result = JUnitTestCaseResult(
                status=JUnitTestCaseStatus.error,
                type=error_element.attrib.get("type", ""),
                message=error_element.attrib.get("message", ""),
                stacktrace=error_element.text or "",
            )
        else:
            junit_result = JUnitTestCaseResult(
                status=JUnitTestCaseStatus.passed,
                type="",
                message="",
                stacktrace="",
            )
        return junit_result
