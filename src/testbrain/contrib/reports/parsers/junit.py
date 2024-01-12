import datetime
import pathlib
import typing as t

from dateutil import parser as datetime_parser
from lxml import etree

from ..models import junit


class JUnitParser(object):
    _xml: etree.Element = None
    _data: t.AnyStr = None
    _namespace: t.Optional[str] = None
    _result: junit.JUnitTestSuites = None

    def __init__(
        self, string: t.Optional[str] = None, filename: t.Optional[pathlib.Path] = None
    ):
        if string and filename:
            raise AssertionError("both string and filename")

        if string:
            self._fromstring(string=string)
        elif filename:
            self._fromfile(filename=filename)

        self.read_namespace()

        self._result = junit.JUnitTestSuites()

    def _fromfile(self, filename: pathlib.Path):
        self._data = filename.read_bytes()
        self._xml = etree.fromstring(self._data)

    def _fromstring(self, string: t.AnyStr):
        if isinstance(string, str):
            string = string.encode(encoding="utf-8")
        self._data = string
        self._xml = etree.fromstring(text=self._data)

    @property
    def result(self) -> junit.JUnitTestSuites:
        return self._result

    @property
    def namespace(self):
        if self._namespace and self._namespace != "":
            return "{%s}" % self._namespace
        return None

    @namespace.setter
    def namespace(self, ns: t.Optional[str] = None):
        if ns:
            self._namespace = ns
        else:
            self._namespace = None

    def read_namespace(self):
        _namespace = None
        if self._xml is not None:
            _namespace = self._xml.nsmap.get(None, "")
        self.namespace = _namespace

    def read_testcase_result(  # noqa
        self, testcase_element: etree.Element
    ) -> junit.JUnitResult:
        junit_result = junit.JUnitResult()
        skipped_element = testcase_element.find("skipped")
        failure_element = testcase_element.find("failure")
        error_element = testcase_element.find("error")
        if skipped_element is not None:
            junit_result.status = "skipped"
            junit_result.type = skipped_element.attrib.get("type", "")
            junit_result.message = skipped_element.attrib.get("message", "")
            junit_result.stacktrace = skipped_element.text or ""
        elif failure_element is not None:
            junit_result.status = "failure"
            junit_result.type = failure_element.attrib.get("type", "")
            junit_result.message = failure_element.attrib.get("message", "")
            junit_result.stacktrace = failure_element.text or ""
        elif error_element is not None:
            junit_result.status = "error"
            junit_result.type = error_element.attrib.get("type", "")
            junit_result.message = error_element.attrib.get("message", "")
            junit_result.stacktrace = error_element.text or ""
        else:
            junit_result.status = "passed"
            junit_result.type = ""
            junit_result.message = ""
            junit_result.stacktrace = ""
        return junit_result

    def read_testcase(  # noqa
        self, testcase_element: etree.Element
    ) -> junit.JUnitTestCase:
        junit_testcase = junit.JUnitTestCase(**testcase_element.attrib)
        junit_testcase.system_out = testcase_element.findtext("system-out", default="")
        junit_testcase.system_err = testcase_element.findtext("system-err", default="")
        return junit_testcase

    def read_testsuites(self) -> None:
        junit_testsuites = []

        for testsuite_element in self._xml.getiterator("testsuite"):
            junit_testsuite = junit.JUnitTestSuite()
            junit_testsuite.id = testsuite_element.attrib.get("id", "")
            junit_testsuite.name = testsuite_element.attrib.get("name", "")

            junit_testsuite.errors = int(testsuite_element.attrib.get("errors", 0))
            junit_testsuite.failures = int(testsuite_element.attrib.get("failures", 0))
            junit_testsuite.skipped = int(testsuite_element.attrib.get("skipped", 0))
            junit_testsuite.passed = int(testsuite_element.attrib.get("passed", 0))
            junit_testsuite.tests = int(testsuite_element.attrib.get("tests", 0))
            junit_testsuite.time = float(testsuite_element.attrib.get("time", 0.0))

            junit_testsuite.timestamp = testsuite_element.attrib.get("timestamp")
            junit_testsuite.hostname = testsuite_element.attrib.get("hostname", "")

            junit_testsuite.system_out = testsuite_element.findtext(
                "system-out", default=""
            )
            junit_testsuite.system_err = testsuite_element.findtext(
                "system-err", default=""
            )

            for testcase_element in testsuite_element.getiterator("testcase"):
                junit_testcase = self.read_testcase(testcase_element=testcase_element)
                junit_testcase.result = self.read_testcase_result(
                    testcase_element=testcase_element
                )
                junit_testsuite.add_testcase(testcase=junit_testcase)

            # Ensure correct stats
            junit_testsuite.update_statistics()
            junit_testsuites.append(junit_testsuite)

        # Ensure update total stats
        self._result.testsuites = junit_testsuites
        self._result.update_statistics()

    def read_root(self) -> None:
        if self._xml.tag == "testsuites":
            self._result.id = self._xml.attrib.get("id", "")
            self._result.name = self._xml.attrib.get("name", "")

            self._result.errors = int(self._xml.attrib.get("errors", 0))
            self._result.failures = int(self._xml.attrib.get("failures", 0))
            self._result.skipped = int(self._xml.attrib.get("skipped", 0))
            self._result.passed = int(self._xml.attrib.get("passed", 0))
            self._result.tests = int(self._xml.attrib.get("tests", 0))
            self._result.time = float(self._xml.attrib.get("time", 0.0))

        elif self._xml.tag == "testsuite":
            ...
        else:
            raise ValueError("Incorrect JUnit XML format")

    def parse(self) -> junit.JUnitTestSuites:
        self.read_root()
        self.read_testsuites()
        return self.result
