import typing as t
from itertools import groupby
from operator import itemgetter

from ..models.junit import JUnitResult, JUnitTestCase, JUnitTestSuite, JUnitTestSuites
from ..models.testbrain import TestbrainTest, TestbrainTestRun, TestbrainTestSuite
from ..models.trx import TrxTestDefinition, TrxTestRun, TrxUnitTestResult


class JUnitConverter(object):
    _source: JUnitTestSuites
    _destination: t.Union[TrxTestRun, TestbrainTestSuite]

    def __init__(self, source: JUnitTestSuites):
        self._source = source

    @property
    def source(self) -> JUnitTestSuites:
        return self._source

    @property
    def destination(self) -> t.Union[TrxTestRun, TestbrainTestSuite]:
        return self._destination

    def convert(self) -> t.Union[JUnitTestSuites, TestbrainTestSuite]:
        raise NotImplementedError


class JUnit2TestbrainConverter(JUnitConverter):
    def __init__(self, source: JUnitTestSuites):
        super().__init__(source=source)
        self._destination = TestbrainTestSuite()

    def convert(self) -> TestbrainTestSuite:
        self.destination.id = self.source.id
        self.destination.name = self.source.name
        self.destination.errors = self.source.errors
        self.destination.failures = self.source.failures
        self.destination.skipped = self.source.skipped
        self.destination.passed = self.source.passed
        self.destination.total = self.source.tests
        self.destination.time = self.source.time

        for junit_testsuite in self.source.testsuites:
            self._add_testrun(testsuite=junit_testsuite)

        # Ensure total statistics
        self.destination.update_statistics()
        return self.destination

    def _add_testrun(self, testsuite: JUnitTestSuite) -> None:
        tb_testrun = TestbrainTestRun()
        self._destination.add_testrun(testrun=tb_testrun)

        tb_testrun.id = testsuite.id
        tb_testrun.name = testsuite.name
        tb_testrun.errors = testsuite.errors
        tb_testrun.failures = testsuite.failures
        tb_testrun.skipped = testsuite.skipped
        tb_testrun.passed = testsuite.passed
        tb_testrun.total = testsuite.tests
        tb_testrun.time = testsuite.time
        tb_testrun.timestamp = testsuite.timestamp
        tb_testrun.hostname = testsuite.hostname
        tb_testrun.system_out = testsuite.system_out
        tb_testrun.system_err = testsuite.system_err

        for junit_testcase in testsuite.testcases:
            self._add_test(tb_testrun, junit_testcase)

        tb_testrun.update_statistics()

    def _add_test(  # noqa
        self, tb_testrun: TestbrainTestRun, testcase: JUnitTestCase
    ) -> None:
        tb_test = TestbrainTest()
        tb_testrun.add_test(tb_test)

        tb_test.id = testcase.id
        tb_test.name = testcase.name
        tb_test.classname = testcase.classname
        tb_test.file = testcase.file
        tb_test.line = testcase.line
        tb_test.time = testcase.time
        tb_test.system_out = testcase.system_out
        tb_test.system_err = testcase.system_err
        tb_test.status = testcase.result.status
        tb_test.type = testcase.result.type
        tb_test.message = testcase.result.message
        tb_test.stacktrace = testcase.result.stacktrace
