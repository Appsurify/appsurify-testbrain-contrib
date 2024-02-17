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


class TestbrainTestResultStatus(str, enum.Enum):
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


class TestbrainTestResult(BaseModel):
    """
    From <testcase> attr name etc.
    """

    status: t.Optional[TestbrainTestResultStatus] = TestbrainTestResultStatus.passed
    type: t.Optional[str] = ""
    message: t.Optional[str] = ""
    stacktrace: t.Optional[str] = ""


class TestbrainTest(BaseModel):
    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    classname: t.Optional[str] = ""
    file: t.Optional[str] = ""
    line: t.Optional[str] = ""
    time: t.Optional[float] = 0.0

    system_out: t.Optional[str] = ""
    system_err: t.Optional[str] = ""
    result: t.Optional[TestbrainTestResult] = TestbrainTestResult(
        status=TestbrainTestResultStatus.passed
    )


class TestbrainTestRunProperty(BaseModel):
    name: t.Optional[str] = ""
    value: t.Optional[str] = ""


class TestbrainTestRun(BaseModel):
    """
    From <testsuite> attr name etc.
    """

    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    errors: t.Optional[int] = 0
    failures: t.Optional[int] = 0
    skipped: t.Optional[int] = 0
    passed: t.Optional[int] = 0
    total: t.Optional[int] = 0
    time: t.Optional[float] = 0.0
    timestamp: t.Optional[datetime.datetime] = datetime.datetime.now()
    hostname: t.Optional[str] = ""
    system_out: t.Optional[str] = ""
    system_err: t.Optional[str] = ""
    tests: t.Optional[t.List[TestbrainTest]] = []
    properties: t.Optional[t.List[TestbrainTestRunProperty]] = []

    def add_test(self, test: TestbrainTest):
        self.tests.append(test)

    def update_statistics(self):
        total = errors = failures = skipped = passed = 0
        time = 0.0
        for test in self.tests:
            total += 1
            time += test.time

            if test.result.status == "passed":
                passed += 1
            elif test.result.status == "error":
                errors += 1
            elif test.result.status == "failure":
                failures += 1
            elif test.result.status == "skipped":
                skipped += 1

        self.total = total
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.passed = passed
        self.time = round(time, 3)

    def add_property(self, prop: TestbrainTestRunProperty):
        self.properties.append(prop)


class TestbrainTestSuite(BaseModel):
    """
    From <testsuites> attr name or from env
    """

    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    errors: t.Optional[int] = 0
    failures: t.Optional[int] = 0
    skipped: t.Optional[int] = 0
    passed: t.Optional[int] = 0
    total: t.Optional[int] = 0
    time: t.Optional[float] = 0.0
    testruns: t.Optional[t.List[TestbrainTestRun]] = []

    def add_testrun(self, testrun: TestbrainTestRun):
        self.testruns.append(testrun)

    def add_testruns(self, testruns: t.List[TestbrainTestRun]):
        self.testruns.extend(testruns)

    def update_statistics(self):
        total = errors = failures = skipped = passed = 0
        time = 0.0
        for testrun in self.testruns:
            total += testrun.total
            time += testrun.time

            passed += testrun.passed
            errors += testrun.errors
            failures += testrun.failures
            skipped += testrun.skipped

        self.total = total
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.passed = passed
        self.time = round(time, 3)

    def model_dump_xml(self) -> str:
        elem = utils.to_xml(
            tag="testsuite",
            attrib={
                "id": self.id,
                "name": self.name,
                "time": str(self.time),
                "total": str(self.total),
                "errors": str(self.errors),
                "failures": str(self.failures),
                "skipped": str(self.skipped),
                "passed": str(self.passed),
            },
        )
        for testrun in self.testruns:
            tr_elem = utils.to_xml(
                tag="testsuite",
                attrib={
                    "id": testrun.id,
                    "name": testrun.name,
                    "time": str(testrun.time),
                    "total": str(testrun.total),
                    "errors": str(testrun.errors),
                    "failures": str(testrun.failures),
                    "skipped": str(testrun.skipped),
                    "passed": str(testrun.passed),
                    "hostname": str(testrun.hostname),
                    "timestamp": utils.datetime_to_string(testrun.timestamp),
                },
            )
            props_elem = utils.to_xml(tag="properties", attrib={})

            for prop in testrun.properties:
                prop_elem = utils.to_xml(
                    tag="property",
                    attrib={"name": prop.name, "value": str(prop.value)},
                )
                props_elem.append(prop_elem)

            tr_elem.append(props_elem)

            if testrun.system_out:
                system_out_elem = utils.to_xml(
                    tag="system-out", text=str(testrun.system_out)
                )
                tr_elem.append(system_out_elem)

            if testrun.system_err:
                system_err_elem = utils.to_xml(
                    tag="system-err", text=str(testrun.system_err)
                )
                tr_elem.append(system_err_elem)

            for test in testrun.tests:
                test_elem = utils.to_xml(
                    tag="testcase",
                    attrib={
                        "id": test.id,
                        "name": test.name,
                        "classname": test.classname,
                        "file": test.file,
                        "line": test.line,
                        "time": str(test.time),
                    },
                )
                if test.result is not None:
                    res_elem = utils.to_xml(
                        tag=test.result.status,
                        attrib={
                            "message": test.result.message,
                            "type": test.result.type,
                        },
                        text=test.result.stacktrace,
                    )
                    test_elem.append(res_elem)

                if test.system_out:
                    system_out_elem = utils.to_xml(
                        tag="system-out", text=str(test.system_out)
                    )
                    test_elem.append(system_out_elem)

                if test.system_err:
                    system_err_elem = utils.to_xml(
                        tag="system-err", text=str(test.system_err)
                    )
                    test_elem.append(system_err_elem)

                tr_elem.append(test_elem)

            elem.append(tr_elem)

        xml_string = utils.xml_to_string(elem)
        return xml_string
