import abc
import pathlib
import typing as t
from itertools import groupby
from operator import itemgetter

from .. import utils
from ..models.junit import (
    JUnitTestCase,
    JUnitTestCaseResult,
    JUnitTestCaseStatus,
    JUnitTestSuite,
    JUnitTestSuites,
)
from ..models.mstest import (
    MSTestExecution,
    MSTestOutcome,
    MSTestResultSummary,
    MSTestTestMethod,
    MSTestTestRun,
    MSTestTimes,
    MSTestUnitTest,
    MSTestUnitTestResult,
)
from ..models.testbrain import (
    TestbrainTest,
    TestbrainTestResult,
    TestbrainTestResultStatus,
    TestbrainTestRun,
    TestbrainTestSuite,
)
from .base import ReportConverter


class MSTestReportConverter(ReportConverter):
    _source: MSTestTestRun
    _target: t.Union[TestbrainTestSuite, JUnitTestSuites]

    _mstest_test_definitions: t.Iterable
    _mstest_test_definition_lookup: t.Dict[str, MSTestUnitTestResult] = {}

    _test_id: int = 0

    _counters: "Counters"

    class Counters:  # noqa
        total = 0
        failures = 0
        errors = 0
        skipped = 0
        passed = 0
        time = 0.0
        timestamp = None

    def __init__(self, source: MSTestTestRun):
        super().__init__(source=source)
        self._test_id = 0
        self._reset_counters()

    def convert(self) -> TestbrainTestSuite:
        ...

    def _reset_counters(self):
        self._counters = self.Counters()

    def _load_test_definitions(self):
        for unit_test_result in self._source.unit_test_results:
            self._mstest_test_definition_lookup[
                unit_test_result.test_id
            ] = unit_test_result

        mstest_test_definitions = [
            mstest_unit_test for mstest_unit_test in self._source.test_definitions
        ]

        mstest_test_definitions = sorted(
            mstest_test_definitions,
            key=lambda x: x.testmethod.class_name
            # key=utils.nested_itemgetter("testmethod", "class_name"),
        )

        self._mstest_test_definitions = groupby(
            mstest_test_definitions,
            key=lambda x: x.testmethod.class_name
            # key=utils.nested_itemgetter("testmethod", "class_name"),
        )

    @staticmethod
    def resolve_status(
        mstest_unit_test_result: MSTestUnitTestResult,
    ) -> t.Union[TestbrainTestResultStatus, JUnitTestCaseStatus]:
        status = TestbrainTestResultStatus.passed
        if mstest_unit_test_result.outcome in [
            MSTestOutcome.completed,
            MSTestOutcome.passed,
            MSTestOutcome.passed_but_run_aborted,
        ]:
            status = TestbrainTestResultStatus.passed
        elif mstest_unit_test_result.outcome in [
            MSTestOutcome.not_executed,
            MSTestOutcome.not_runnable,
            MSTestOutcome.disconnected,
        ]:
            status = TestbrainTestResultStatus.skipped
        elif mstest_unit_test_result.outcome in [
            MSTestOutcome.error,
        ]:
            status = TestbrainTestResultStatus.error
        elif mstest_unit_test_result.outcome in [
            MSTestOutcome.aborted,
            MSTestOutcome.failed,
            MSTestOutcome.timeout,
        ]:
            status = TestbrainTestResultStatus.failure
        return status


class MSTest2TestbrainReportConverter(MSTestReportConverter):
    _target: TestbrainTestSuite

    def __init__(self, source: MSTestTestRun):
        super().__init__(source)
        self._target = TestbrainTestSuite()

    @property
    def result(self) -> TestbrainTestSuite:
        return self._target

    def convert(self) -> TestbrainTestSuite:
        self.convert_root()
        self.convert_test_definitions()
        return self.result

    def convert_root(self):
        self._target.id = self._source.id
        self._target.name = self._source.name

    def convert_test_definitions(self):
        self._load_test_definitions()
        for (
            mstest_unit_test_test_class,
            mstest_unit_tests,
        ) in self._mstest_test_definitions:
            testbrain_testrun = self._convert_unit_tests(
                mstest_unit_test_test_class, mstest_unit_tests
            )
            self._target.add_testrun(testbrain_testrun)

        self._target.update_statistics()

    def _convert_unit_tests(
        self,
        mstest_unit_test_test_class: str,
        mstest_unit_tests: t.List[MSTestUnitTest],
    ) -> TestbrainTestRun:
        self._reset_counters()

        testbrain_testrun = TestbrainTestRun(
            id=str(self._test_id), name=mstest_unit_test_test_class
        )
        self._test_id += 1

        for mstest_unit_test in mstest_unit_tests:
            testbrain_test = self._convert_unit_test(mstest_unit_test)
            testbrain_testrun.add_test(testbrain_test)

        testbrain_testrun.total = self._counters.total
        testbrain_testrun.failures = self._counters.failures
        testbrain_testrun.errors = self._counters.errors
        testbrain_testrun.skipped = self._counters.skipped
        testbrain_testrun.passed = self._counters.passed
        testbrain_testrun.time = self._counters.time
        testbrain_testrun.timestamp = self._counters.timestamp

        testbrain_testrun.update_statistics()

        return testbrain_testrun

    def _convert_unit_test(self, mstest_unit_test: MSTestUnitTest) -> TestbrainTest:
        mstest_unit_test_result = self._mstest_test_definition_lookup.get(
            mstest_unit_test.id
        )

        if mstest_unit_test_result is not None:
            self._counters.total += 1

            testbrain_test = TestbrainTest(
                id=mstest_unit_test_result.test_id,
                name=mstest_unit_test_result.test_name,
                classname=mstest_unit_test.testmethod.class_name,
                file="",
                line="",
                system_out=mstest_unit_test_result.std_out,
                system_err=mstest_unit_test_result.std_err,
            )
            # testbrain_test.model_dump_json()
            if self._counters.timestamp is None:
                self._counters.timestamp = mstest_unit_test_result.start_time

            if mstest_unit_test_result.duration is None:
                mstest_unit_test_result.duration = mstest_unit_test_result.run_time

            self._counters.time += mstest_unit_test_result.duration
            testbrain_test.time = mstest_unit_test_result.duration

            testbrain_test.result = TestbrainTestResult(
                status=self.resolve_status(mstest_unit_test_result),
                type="",
                message=mstest_unit_test_result.message,
                stacktrace=mstest_unit_test_result.stacktrace,
            )
        else:
            testbrain_test = TestbrainTest()

        return testbrain_test


class MSTest2JUnitReportConverter(MSTestReportConverter):
    _target: JUnitTestSuites

    def __init__(self, source: MSTestTestRun):
        super().__init__(source)
        self._target = JUnitTestSuites()

    @property
    def result(self) -> JUnitTestSuites:
        return self._target

    def convert(self) -> JUnitTestSuites:
        self.convert_root()
        self.convert_test_definitions()
        return self.result

    def convert_root(self):
        self._target.id = self._source.id
        self._target.name = self._source.name

    def convert_test_definitions(self):
        self._load_test_definitions()
        for (
            mstest_unit_test_test_class,
            mstest_unit_tests,
        ) in self._mstest_test_definitions:
            junit_testsuite = self._convert_unit_tests(
                mstest_unit_test_test_class, mstest_unit_tests
            )
            self._target.add_testsuite(junit_testsuite)

        self._target.update_statistics()

    def _convert_unit_tests(
        self,
        mstest_unit_test_test_class: str,
        mstest_unit_tests: t.List[MSTestUnitTest],
    ) -> JUnitTestSuite:
        self._reset_counters()

        junit_testsuite = JUnitTestSuite(
            id=str(self._test_id), name=mstest_unit_test_test_class
        )

        self._test_id += 1

        for mstest_unit_test in mstest_unit_tests:
            junit_testcase = self._convert_unit_test(mstest_unit_test)
            junit_testsuite.add_testcase(junit_testcase)

        junit_testsuite.tests = self._counters.total
        junit_testsuite.failures = self._counters.failures
        junit_testsuite.errors = self._counters.errors
        junit_testsuite.skipped = self._counters.skipped
        junit_testsuite.passed = self._counters.passed
        junit_testsuite.time = self._counters.time
        junit_testsuite.timestamp = self._counters.timestamp

        junit_testsuite.update_statistics()

        return junit_testsuite

    def _convert_unit_test(self, mstest_unit_test: MSTestUnitTest) -> JUnitTestCase:
        mstest_unit_test_result = self._mstest_test_definition_lookup.get(
            mstest_unit_test.id
        )

        if mstest_unit_test_result is not None:
            self._counters.total += 1

            junit_testcase = JUnitTestCase(
                id=mstest_unit_test_result.test_id,
                name=mstest_unit_test_result.test_name,
                classname=mstest_unit_test.testmethod.class_name,
                file="",
                line="",
                system_out=mstest_unit_test_result.std_out,
                system_err=mstest_unit_test_result.std_err,
            )
            # testbrain_test.model_dump_json()
            if self._counters.timestamp is None:
                self._counters.timestamp = mstest_unit_test_result.start_time

            if mstest_unit_test_result.duration is None:
                mstest_unit_test_result.duration = mstest_unit_test_result.run_time

            self._counters.time += mstest_unit_test_result.duration
            junit_testcase.time = mstest_unit_test_result.duration

            junit_testcase.result = JUnitTestCaseResult(
                status=self.resolve_status(mstest_unit_test_result),
                type="",
                message=mstest_unit_test_result.message,
                stacktrace=mstest_unit_test_result.stacktrace,
            )
        else:
            junit_testcase = JUnitTestCase()

        return junit_testcase
