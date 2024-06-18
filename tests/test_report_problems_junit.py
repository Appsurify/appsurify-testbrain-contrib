import pytest
import pathlib

from testbrain.contrib.report.mergers.junit import JUnitReportMerger
from testbrain.contrib.report.parsers import JUnitReportParser
from testbrain.contrib.report.converters import JUnit2TestbrainReportConverter


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture()
def directory_resource_samples_problems_junit():
    directory = base_dir / "resources" / "samples" / "problems"
    return directory


def test_parse_junit_report_common(directory_resource_samples_problems_junit):
    report_filepath = directory_resource_samples_problems_junit.joinpath(
        "junit-maybe-cucumber-report"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 163


#
# def test_convert_junit_to_testbrain(directory_resource_samples_problems_junit):
#     report_filepath = directory_resource_samples_problems_junit.joinpath(
#         "junit-common-normal"
#     ).with_suffix(".xml")
#     junit_parser = JUnitReportParser.fromfile(report_filepath)
#     junit_parser.parse()
#     junit_report = junit_parser.result
#     assert junit_report.tests == 3
#     junit2testbrain = JUnit2TestbrainReportConverter(source=junit_report)
#     junit2testbrain.convert()
#     testbrain_report = junit2testbrain.result
#     assert testbrain_report.total == 3
