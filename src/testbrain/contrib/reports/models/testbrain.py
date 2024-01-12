import datetime
import typing as t

from pydantic import BaseModel


class TestbrainTest(BaseModel):
    """
    From <testcase> attr name etc.
    """

    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    classname: t.Optional[str] = ""
    file: t.Optional[str] = ""
    line: t.Optional[str] = ""
    time: t.Optional[float] = 0.0
    system_out: t.Optional[str] = ""
    system_err: t.Optional[str] = ""

    status: t.Optional[str] = ""
    type: t.Optional[str] = ""
    message: t.Optional[str] = ""
    stacktrace: t.Optional[str] = ""


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
    timestamp: t.Optional[datetime.datetime] = datetime.datetime.now(datetime.UTC)
    hostname: t.Optional[str] = ""
    system_out: t.Optional[str] = ""
    system_err: t.Optional[str] = ""
    tests: t.Optional[t.List[TestbrainTest]] = []

    def add_test(self, test: TestbrainTest) -> None:
        self.tests.append(test)

    def update_statistics(self) -> None:
        total = errors = failures = skipped = passed = 0
        time = 0.0
        for test in self.tests:
            total += 1
            time += test.time

            if test.status == "passed":
                passed += 1
            elif test.status == "error":
                errors += 1
            elif test.status == "failure":
                failures += 1
            elif test.status == "skipped":
                skipped += 1

        self.total = total
        self.errors = errors
        self.failures = failures
        self.skipped = skipped
        self.passed = passed
        self.time = round(time, 3)


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

    def add_testrun(self, testrun: TestbrainTestRun) -> None:
        self.testruns.append(testrun)

    def update_statistics(self) -> None:
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
