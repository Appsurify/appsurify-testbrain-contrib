import datetime
import typing as t

from .. import utils
from ..models.allure import (
    AllureKV,
    AllureReport,
    AllureStatus,
    AllureSuite,
    AllureTestcase,
    AllureTime,
)
from ..models.junit import (
    JUnitTestCase,
    JUnitTestCaseResult,
    JUnitTestCaseStatus,
    JUnitTestSuite,
    JUnitTestSuiteProperty,
    JUnitTestSuites,
)
from ..models.testbrain import (
    TestbrainTest,
    TestbrainTestResult,
    TestbrainTestResultStatus,
    TestbrainTestRun,
    TestbrainTestRunProperty,
    TestbrainTestSuite,
)
from .base import ReportConverter


class Allure2TestbrainReportConverter(ReportConverter):
    _source: AllureReport
    _target: TestbrainTestSuite

    def __init__(self, source: AllureReport):
        super().__init__(source)
        self._target = TestbrainTestSuite()

    @property
    def result(self) -> TestbrainTestSuite:
        return self._target

    def convert(self) -> TestbrainTestSuite:
        self.convert_root()
        self.convert_suites()
        return self.result

    def convert_root(self):
        self._target.id = self._source.uid
        self._target.name = self._source.name

    def convert_suites(self):
        for suite in self._source.children:
            testbrain_testrun = TestbrainTestRun(
                id=suite.uid,
                name=suite.name,
                hostname=self.get_kv_value(
                    "host", suite.children[0].labels, default="unknown"
                ),
            )

            all_times = [tc.time.start for tc in suite.children]
            min_time = min(all_times)
            if int(min_time) == 0:
                min_time = datetime.datetime.now().timestamp() * 1000
            testbrain_testrun.timestamp = utils.timestamp_to_datetime(min_time / 1000)

            for testcase in suite.children:
                testbrain_test = self._convert_testcase(testcase)
                testbrain_test.classname = self.get_kv_value(
                    "package", testcase.labels, default=suite.name
                )
                testbrain_testrun.add_test(testbrain_test)

            for suite_property in suite.children[0].parameters:
                testbrain_testrun_property = TestbrainTestRunProperty(**suite_property)
                testbrain_testrun.add_property(testbrain_testrun_property)

            for suite_label in suite.children[0].labels:
                testbrain_testrun_property = TestbrainTestRunProperty(**suite_label)
                testbrain_testrun.add_property(testbrain_testrun_property)

            testbrain_testrun.update_statistics()

            self._target.add_testrun(testbrain_testrun)
        self._target.update_statistics()

    def _convert_testcase(self, testcase: AllureTestcase) -> TestbrainTest:
        testbrain_test = TestbrainTest(
            id=testcase.uid,
            name=testcase.name,
            classname=self.get_kv_value("package", testcase.labels),
            time=float(testcase.time.duration / 1000),
        )

        testbrain_test.result = TestbrainTestResult(
            status=self.resolve_status(testcase.status),
            message=testcase.status_message,
            stacktrace=testcase.status_trace,
        )

        return testbrain_test

    @staticmethod
    def get_kv_value(
        name: str, kv_list: t.List[AllureKV], default: t.Optional[str] = ""
    ) -> str:
        value = default
        for kv in kv_list:
            try:
                if kv["name"] == name:
                    value = kv["value"]
                    break
            except AttributeError:
                ...
        return value

    @staticmethod
    def resolve_status(
        status: AllureStatus,
    ) -> TestbrainTestResultStatus:
        if status == AllureStatus.passed:
            status = TestbrainTestResultStatus.passed
        elif status == AllureStatus.skipped:
            status = TestbrainTestResultStatus.skipped
        elif status == AllureStatus.failed:
            status = TestbrainTestResultStatus.failure
        elif status == AllureStatus.broken:
            status = TestbrainTestResultStatus.error
        elif status == AllureStatus.unknown:
            status = TestbrainTestResultStatus.unknown
        return status


class Allure2JUnitReportConverter(ReportConverter):
    _source: AllureReport
    _target: JUnitTestSuites

    def __init__(self, source: AllureReport):
        super().__init__(source)
        self._target = JUnitTestSuites()

    @property
    def result(self) -> JUnitTestSuites:
        return self._target

    def convert(self) -> JUnitTestSuites:
        self.convert_root()
        self.convert_suites()
        return self.result

    def convert_root(self):
        self._target.id = self._source.uid
        self._target.name = self._source.name

    def convert_suites(self):
        for suite in self._source.children:
            junit_testsuite = JUnitTestSuite(
                id=suite.uid,
                name=suite.name,
                hostname=self.get_kv_value(
                    "host", suite.children[0].labels, default="unknown"
                ),
            )

            all_times = [tc.time.start for tc in suite.children]
            min_time = min(all_times)
            if int(min_time) == 0:
                min_time = datetime.datetime.now().timestamp() * 1000
            junit_testsuite.timestamp = utils.timestamp_to_datetime(min_time / 1000)

            for testcase in suite.children:
                junit_testcase = self._convert_testcase(testcase)
                junit_testcase.classname = self.get_kv_value(
                    "package", testcase.labels, default=suite.name
                )

                junit_testsuite.add_testcase(junit_testcase)

            for suite_property in suite.children[0].parameters:
                junit_testsuite_property = JUnitTestSuiteProperty(**suite_property)
                junit_testsuite.add_property(junit_testsuite_property)

            for suite_label in suite.children[0].labels:
                junit_testsuite_property = JUnitTestSuiteProperty(**suite_label)
                junit_testsuite.add_property(junit_testsuite_property)

            junit_testsuite.update_statistics()

            self._target.add_testsuite(junit_testsuite)
        self._target.update_statistics()

    def _convert_testcase(self, testcase: AllureTestcase) -> JUnitTestCase:
        junit_testcase = JUnitTestCase(
            id=testcase.uid,
            name=testcase.name,
            time=float(testcase.time.duration / 1000),
        )

        junit_testcase.result = TestbrainTestResult(
            status=self.resolve_status(testcase.status),
            message=testcase.status_message,
            stacktrace=testcase.status_trace,
        )

        return junit_testcase

    @staticmethod
    def get_kv_value(
        name: str, kv_list: t.List[AllureKV], default: t.Optional[str] = ""
    ) -> str:
        value = default
        for kv in kv_list:
            try:
                if kv["name"] == name:
                    value = kv["value"]
                    break
            except AttributeError:
                ...
        return value

    @staticmethod
    def resolve_status(
        status: AllureStatus,
    ) -> TestbrainTestResultStatus:
        if status == AllureStatus.passed:
            status = TestbrainTestResultStatus.passed
        elif status == AllureStatus.skipped:
            status = TestbrainTestResultStatus.skipped
        elif status == AllureStatus.failed:
            status = TestbrainTestResultStatus.failure
        elif status == AllureStatus.broken:
            status = TestbrainTestResultStatus.error
        elif status == AllureStatus.unknown:
            status = TestbrainTestResultStatus.unknown
        return status
