import datetime
import pytest
import pathlib

from testbrain.contrib.report import utils
from testbrain.contrib.report.mergers.junit import JUnitReportMerger
from testbrain.contrib.report.mergers.testbrain import TestbrainReportMerger
from testbrain.contrib.report.models.testbrain import TestbrainTestSuite
from testbrain.contrib.report.parsers import JUnitReportParser
from testbrain.contrib.report.converters import JUnit2TestbrainReportConverter


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture()
def junit_report_directory_for_testbrain():
    dir = base_dir / "resources" / "samples" / "directory"
    return dir


def test_merge_testbrain_reports(junit_report_directory_for_testbrain):
    files = [f for f in junit_report_directory_for_testbrain.iterdir() if f.is_file()]
    reports = []
    for file in files:
        if file.is_file():
            reports.append(file.read_text(encoding="utf-8"))

    testbrain_reports = []

    for report in reports:
        junit_parser = JUnitReportParser.fromstring(report)
        junit_parser.parse()
        junit_2_testbrain_converter = JUnit2TestbrainReportConverter(
            source=junit_parser.result
        )
        junit_2_testbrain_converter.convert()
        testbrain_reports.append(junit_2_testbrain_converter.result)

    testbrain_merger = TestbrainReportMerger.from_reports(testbrain_reports)
    testbrain_merger.merge()

    result_report = testbrain_merger.result
    result_report_xml = testbrain_merger.result_xml
    assert len(result_report.testruns) == 4
    assert result_report_xml is not None
