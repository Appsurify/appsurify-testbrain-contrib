from ..models.testbrain import TestbrainTestSuite
from .base import ReportMerger


class TestbrainReportMerger(ReportMerger):
    _target: TestbrainTestSuite

    @property
    def result(self) -> TestbrainTestSuite:
        return self._target

    def merge(self):
        self._target = TestbrainTestSuite()

        for report in self.reports:
            self._target.add_testruns(report.testruns)

        self._target.update_statistics()

        return self.result
