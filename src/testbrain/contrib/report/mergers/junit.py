import typing as t

from ..models.junit import JUnitTestSuites
from ..parsers.junit import JUnitReportParser
from .base import ReportMerger


class JUnitReportMerger(ReportMerger):
    _reports: t.List[JUnitTestSuites]
    _target: JUnitTestSuites
    _parser: JUnitReportParser = JUnitReportParser

    @classmethod
    def from_reports(cls, reports: t.List[JUnitTestSuites]):
        return super().from_reports(reports=reports)

    def __init__(self, reports: t.List[JUnitTestSuites]):
        super().__init__(reports=reports)

    @property
    def result(self) -> JUnitTestSuites:
        return self._target

    def merge(self):
        self._target = JUnitTestSuites()

        for report in self._reports:
            self._target.add_testsuites(report.testsuites)

        self._target.update_statistics()

        return self.result
