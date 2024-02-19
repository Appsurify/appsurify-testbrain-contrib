from ..models.junit import JUnitTestCase, JUnitTestSuites
from ..models.testbrain import (
    TestbrainTest,
    TestbrainTestResult,
    TestbrainTestRun,
    TestbrainTestRunProperty,
    TestbrainTestSuite,
)
from .base import ReportConverter


class JUnit2TestbrainReportConverter(ReportConverter):
    _source: JUnitTestSuites
    _target: TestbrainTestSuite

    def __init__(self, source: JUnitTestSuites):
        super().__init__(source)
        self._target = TestbrainTestSuite()

    @property
    def result(self) -> TestbrainTestSuite:
        return self._target

    def convert(self) -> TestbrainTestSuite:
        self.convert_root()
        self.convert_testsuites()
        return self.result

    def convert_root(self):
        self._target.id = self._source.id
        self._target.name = self._source.name
        self._target.errors = self._source.errors
        self._target.failures = self._source.failures
        self._target.skipped = self._source.skipped
        self._target.passed = self._source.passed
        self._target.total = self._source.tests
        self._target.time = self._source.time

    def convert_testsuites(self):
        for testsuite in self._source.testsuites:
            testbrain_testrun = TestbrainTestRun(
                id=testsuite.id,
                name=testsuite.name,
                errors=testsuite.errors,
                failures=testsuite.failures,
                skipped=testsuite.skipped,
                passed=testsuite.passed,
                total=testsuite.tests,
                time=testsuite.time,
                timestamp=testsuite.timestamp,
                hostname=testsuite.hostname,
                system_out=testsuite.system_out,
                system_err=testsuite.system_err,
            )

            self._target.add_testrun(testbrain_testrun)

            for testsuite_property in testsuite.properties:
                testbrain_testrun_property = TestbrainTestRunProperty(
                    name=testsuite_property.name, value=testsuite_property.value
                )
                testbrain_testrun.add_property(testbrain_testrun_property)

            for testcase in testsuite.testcases:
                testbrain_test = self._convert_testcase(testcase)
                testbrain_testrun.add_test(testbrain_test)

            testbrain_testrun.update_statistics()

        self._target.update_statistics()

    @staticmethod
    def _convert_testcase(testcase: JUnitTestCase) -> TestbrainTest:
        testbrain_test = TestbrainTest(
            id=testcase.id,
            name=testcase.name,
            classname=testcase.classname,
            file=testcase.file,
            line=testcase.line,
            time=testcase.time,
            system_out=testcase.system_out,
            system_err=testcase.system_err,
        )

        testbrain_test.result = TestbrainTestResult(
            status=testcase.result.status,
            type=testcase.result.type,
            message=testcase.result.message,
            stacktrace=testcase.result.stacktrace,
        )

        return testbrain_test
