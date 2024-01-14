import datetime
import enum
import typing as t

from pydantic import BaseModel


class JUnitTestCaseStatus(str, enum.Enum):
    passed = "passed"
    skipped = "skipped"
    failure = "failure"
    error = "error"
    warning = "warning"

    @classmethod
    def _missing_(cls, value: str):
        for member in cls:
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
