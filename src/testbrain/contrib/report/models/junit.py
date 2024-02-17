import datetime
import enum
import typing as t

from pydantic import BaseModel

from .. import utils

if t.TYPE_CHECKING:
    try:
        from lxml import etree
    except ImportError:
        from xml.etree import ElementTree as etree  # noqa


class JUnitTestCaseStatus(str, enum.Enum):
    passed = "passed"
    skipped = "skipped"
    failure = "failure"
    error = "error"
    warning = "warning"

    @classmethod
    def _missing_(cls, value: str):
        for member in cls:  # noqa
            if member.lower() == value.lower():
                return member
        return None


class JUnitTestCaseResult(BaseModel):
    status: t.Optional[JUnitTestCaseStatus] = JUnitTestCaseStatus.passed
    type: t.Optional[str] = ""
    message: t.Optional[str] = ""
    stacktrace: t.Optional[str] = ""


class JUnitTestCase(BaseModel):
    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    classname: t.Optional[str] = ""
    file: t.Optional[str] = ""
    line: t.Optional[str] = ""
    time: t.Optional[float] = 0.0
    system_out: t.Optional[str] = ""
    system_err: t.Optional[str] = ""
    result: t.Optional[JUnitTestCaseResult] = None


class JUnitTestSuiteProperty(BaseModel):
    name: t.Optional[str] = ""
    value: t.Optional[str] = ""


class JUnitTestSuite(BaseModel):
    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    errors: t.Optional[int] = 0
    failures: t.Optional[int] = 0
    skipped: t.Optional[int] = 0
    passed: t.Optional[int] = 0
    tests: t.Optional[int] = 0
    time: t.Optional[float] = 0.0
    timestamp: t.Optional[datetime.datetime] = datetime.datetime.now()
    hostname: t.Optional[str] = ""
    system_out: t.Optional[str] = ""
    system_err: t.Optional[str] = ""
    testcases: t.Optional[t.List[JUnitTestCase]] = []
    properties: t.Optional[t.List[JUnitTestSuiteProperty]] = []

    def add_testcase(self, testcase: JUnitTestCase):
        self.testcases.append(testcase)

    def update_statistics(self):
        tests = errors = failures = skipped = passed = 0
        time = 0.0
        for testcase in self.testcases:
            tests += 1
            time += testcase.time

            if testcase.result.status == "passed":
                passed += 1
            elif testcase.result.status == "error":
                errors += 1
            elif testcase.result.status == "failure":
                failures += 1
            elif testcase.result.status == "skipped":
                skipped += 1

        self.tests = tests
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.passed = passed
        self.time = round(time, 3)

    def add_property(self, prop: JUnitTestSuiteProperty):
        self.properties.append(prop)


class JUnitTestSuites(BaseModel):
    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    errors: t.Optional[int] = 0
    failures: t.Optional[int] = 0
    skipped: t.Optional[int] = 0
    passed: t.Optional[int] = 0
    tests: t.Optional[int] = 0
    time: t.Optional[float] = 0.0
    testsuites: t.Optional[t.List[JUnitTestSuite]] = []

    def add_testsuite(self, testsuite: JUnitTestSuite):
        self.testsuites.append(testsuite)

    def add_testsuites(self, testsuites: t.List[JUnitTestSuite]):
        self.testsuites.extend(testsuites)

    def update_statistics(self):
        tests = errors = failures = skipped = passed = 0
        time = 0.0
        for testsuite in self.testsuites:
            tests += testsuite.tests
            time += testsuite.time

            passed += testsuite.passed
            errors += testsuite.errors
            failures += testsuite.failures
            skipped += testsuite.skipped

        self.tests = tests
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.passed = passed
        self.time = round(time, 3)

    def model_dump_xml(self) -> str:
        elem = utils.to_xml(
            tag="testsuites",
            attrib={
                "id": self.id,
                "name": self.name,
                "time": str(self.time),
                "tests": str(self.tests),
                "errors": str(self.errors),
                "failures": str(self.failures),
                "skipped": str(self.skipped),
                "passed": str(self.passed),
            },
        )
        for testsuite in self.testsuites:
            ts_elem = utils.to_xml(
                tag="testsuite",
                attrib={
                    "id": testsuite.id,
                    "name": testsuite.name,
                    "time": str(testsuite.time),
                    "tests": str(testsuite.tests),
                    "errors": str(testsuite.errors),
                    "failures": str(testsuite.failures),
                    "skipped": str(testsuite.skipped),
                    "passed": str(testsuite.passed),
                    "hostname": str(testsuite.hostname),
                    "timestamp": utils.datetime_to_string(testsuite.timestamp),
                },
            )
            props_elem = utils.to_xml(tag="properties", attrib={})

            for prop in testsuite.properties:
                prop_elem = utils.to_xml(
                    tag="property",
                    attrib={"name": prop.name, "value": str(prop.value)},
                )
                props_elem.append(prop_elem)

            ts_elem.append(props_elem)

            if testsuite.system_out:
                system_out_elem = utils.to_xml(
                    tag="system-out", text=str(testsuite.system_out)
                )
                ts_elem.append(system_out_elem)

            if testsuite.system_err:
                system_err_elem = utils.to_xml(
                    tag="system-err", text=str(testsuite.system_err)
                )
                ts_elem.append(system_err_elem)

            for testcase in testsuite.testcases:
                tc_elem = utils.to_xml(
                    tag="testcase",
                    attrib={
                        "id": testcase.id,
                        "name": testcase.name,
                        "classname": testcase.classname,
                        "file": testcase.file,
                        "line": testcase.line,
                        "time": str(testcase.time),
                    },
                )
                if testcase.result is not None:
                    res_elem = utils.to_xml(
                        tag=testcase.result.status,
                        attrib={
                            "message": testcase.result.message,
                            "type": testcase.result.type,
                        },
                        text=testcase.result.stacktrace,
                    )
                    tc_elem.append(res_elem)

                if testcase.system_out:
                    system_out_elem = utils.to_xml(
                        tag="system-out", text=str(testcase.system_out)
                    )
                    tc_elem.append(system_out_elem)

                if testcase.system_err:
                    system_err_elem = utils.to_xml(
                        tag="system-err", text=str(testcase.system_err)
                    )
                    tc_elem.append(system_err_elem)

                ts_elem.append(tc_elem)

            elem.append(ts_elem)

        xml_string = utils.xml_to_string(elem)
        return xml_string
