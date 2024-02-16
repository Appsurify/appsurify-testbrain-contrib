from ..models.testbrain import TestbrainTestSuite
from .base import ReportMerger


class TestbrainReportMerger(ReportMerger):
    _target: TestbrainTestSuite

    def merge(self):
        self._target = TestbrainTestSuite()

        for report in self.reports:
            self._target.add_testruns(report.testruns)

        self._target.update_statistics()
