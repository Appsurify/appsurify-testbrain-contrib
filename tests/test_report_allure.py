import pytest
import pathlib

from testbrain.contrib.report.parsers import AllureReportParser
from testbrain.contrib.report.converters import (
    Allure2TestbrainReportConverter,
    Allure2JUnitReportConverter,
)

base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture()
def directory_resource_samples_allure():
    directory = base_dir / "resources" / "samples" / "allure"
    return directory


def test_parse_allure_report_use_file(directory_resource_samples_allure):
    report_filepath = directory_resource_samples_allure.joinpath("allure_report_c")

    with pytest.raises(AssertionError):
        AllureReportParser.fromfile(
            report_filepath.joinpath("data").joinpath("suites.json")
        )


def test_parse_allure_report_use_not_root(directory_resource_samples_allure):
    report_filepath = directory_resource_samples_allure.joinpath("allure_report_c")
    with pytest.raises(AssertionError):
        AllureReportParser.fromfile(report_filepath.joinpath("data"))


@pytest.mark.parametrize(
    ("report_filepath", "suites"),
    [
        ("allure_report_a", 94),
        ("allure_report_b", 59),
        ("allure_report_c", 51),
    ],
)
def test_parse_allure_report_dir(
    directory_resource_samples_allure, report_filepath, suites
):
    allure_parser = AllureReportParser.fromfile(
        directory_resource_samples_allure.joinpath(report_filepath)
    )
    allure_parser.parse()
    allure_report = allure_parser.result
    assert len(allure_report.children) == suites


@pytest.mark.parametrize(
    ("report_filepath", "testruns"),
    [
        ("allure_report_a", 94),
        ("allure_report_b", 59),
        ("allure_report_c", 51),
    ],
)
def test_convert_allure_2_testbrain(
    directory_resource_samples_allure, report_filepath, testruns
):
    allure_parser = AllureReportParser.fromfile(
        directory_resource_samples_allure.joinpath(report_filepath)
    )
    allure_parser.parse()
    allure_report = allure_parser.result

    allure_2_testbrain = Allure2TestbrainReportConverter(source=allure_report)
    allure_2_testbrain.convert()

    testbrain_report = allure_2_testbrain.result

    assert len(testbrain_report.testruns) == testruns


@pytest.mark.parametrize(
    ("report_filepath", "testsuites"),
    [
        ("allure_report_a", 94),
        ("allure_report_b", 59),
        ("allure_report_c", 51),
    ],
)
def test_convert_allure_2_junit(
    directory_resource_samples_allure, report_filepath, testsuites
):
    allure_parser = AllureReportParser.fromfile(
        directory_resource_samples_allure.joinpath(report_filepath)
    )
    allure_parser.parse()
    allure_report = allure_parser.result

    allure_2_junit = Allure2JUnitReportConverter(source=allure_report)
    allure_2_junit.convert()

    junit_report = allure_2_junit.result

    assert len(junit_report.testsuites) == testsuites


def test_convert_allure_2_junit_time(directory_resource_samples_allure):
    allure_parser = AllureReportParser.fromfile(
        directory_resource_samples_allure.joinpath("allure_report_b")
    )
    allure_parser.parse()
    allure_report = allure_parser.result

    allure_2_junit = Allure2JUnitReportConverter(source=allure_report)
    allure_2_junit.convert()

    junit_report = allure_2_junit.result

    assert len(junit_report.testsuites) == 59
