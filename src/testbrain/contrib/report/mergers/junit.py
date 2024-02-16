import pathlib

from ..models.junit import JUnitTestCase, JUnitTestSuites
from ..models.testbrain import (
    TestbrainTest,
    TestbrainTestResult,
    TestbrainTestRun,
    TestbrainTestRunProperty,
    TestbrainTestSuite,
)
from ..parsers.junit import JUnitReportParser
from .base import ReportMerger


class JUnitReportMerger(ReportMerger):
    _target: JUnitTestSuites

    def merge(self):
        self._target = JUnitTestSuites()

        for report in self.reports:
            junit_parser = JUnitReportParser.fromstring(text=report)
            result = junit_parser.parse()
            self._target.add_testsuites(result.testsuites)

        self._target.update_statistics()
