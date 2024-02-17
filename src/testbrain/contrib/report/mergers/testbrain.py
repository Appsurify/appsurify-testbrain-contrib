import typing as t

from ..models.testbrain import TestbrainTestSuite
from .base import ReportMerger


class TestbrainReportMerger(ReportMerger):
    _reports: t.List[TestbrainTestSuite]
    _target: TestbrainTestSuite
    _parser: t.Any = None

    @classmethod
    def from_reports(cls, reports: t.List[TestbrainTestSuite]):
        return super().from_reports(reports=reports)

    def __init__(self, reports: t.List[TestbrainTestSuite]):
        super().__init__(reports=reports)

    @property
    def result(self) -> TestbrainTestSuite:
        return self._target

    def merge(self):
        self._target = TestbrainTestSuite()

        for report in self._reports:
            self._target.add_testruns(report.testruns)

        self._target.update_statistics()

        return self.result
