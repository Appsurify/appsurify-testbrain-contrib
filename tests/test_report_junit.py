import pytest
import pathlib

from testbrain.contrib.report.mergers.junit import JUnitReportMerger
from testbrain.contrib.report.parsers import JUnitReportParser
from testbrain.contrib.report.converters import JUnit2TestbrainReportConverter


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture()
def directory_resource_samples_junit():
    directory = base_dir / "resources" / "samples" / "junit"
    return directory


@pytest.mark.xfail(reason="Currently the parser cannot read nested testsuites")
def test_parse_junit_report_jenkins(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath(
        "junit-custom-jenkins"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 3


@pytest.mark.parametrize(
    ("report_filepath", "tests"),
    [
        ("junit-common-wellformed-encoding", 1),
        ("junit-common-wellformed-tag", 1),
        ("junit-common-wellformed-empty", 0),
    ],
)
def test_parse_junit_report_well_formed(
    directory_resource_samples_junit, report_filepath, tests
):
    report_filepath = directory_resource_samples_junit.joinpath(
        report_filepath
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == tests


@pytest.mark.parametrize(
    ("report_filepath", "tests"),
    [
        ("junit-common-legacy", 18),
        ("junit-common-named", 2),
        ("junit-common-nofails", 3),
        ("junit-common-normal", 3),
        ("junit-common-nosuites-tag", 3),
        ("junit-common-outputs", 11),
    ],
)
def test_parse_junit_report_common(
    directory_resource_samples_junit, report_filepath, tests
):
    report_filepath = directory_resource_samples_junit.joinpath(
        report_filepath
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == tests


@pytest.mark.parametrize(
    ("report_filepath", "tests"),
    [
        ("junit-custom-android", 2),
        ("junit-custom-ibm", 1),
        ("junit-custom-jenkins", 1),
        ("junit-custom-mocha", 1),
        ("junit-custom-multi-result", 1),
        ("junit-custom-multi-testsuite", 10),
        ("junit-custom-props", 1),
    ],
)
def test_parse_junit_report_custom(
    directory_resource_samples_junit, report_filepath, tests
):
    report_filepath = directory_resource_samples_junit.joinpath(
        report_filepath
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == tests


@pytest.mark.parametrize(
    ("report_filepath", "tests"),
    [
        ("junit-attr-encoding-iso-8859-1", 11),
        ("junit-attr-encoding-utf-8", 11),
        ("junit-attr-encoding-utf-8-bom", 11),
        ("junit-attr-encoding-windows-1251", 11),
        ("junit-encoding-iso-8859-1", 11),
        ("junit-encoding-utf-8", 11),
        ("junit-encoding-utf-8-bom", 11),
        ("junit-encoding-utf-16be", 11),
        ("junit-encoding-utf-16be-bom", 11),
        ("junit-encoding-utf-16le", 11),
        ("junit-encoding-utf-16le-bom", 11),
        ("junit-encoding-windows-1251", 11),
    ],
)
def test_parse_junit_report_encodings(
    directory_resource_samples_junit, report_filepath, tests
):
    report_filepath = directory_resource_samples_junit.joinpath(
        report_filepath
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == tests


def test_parse_junit_report_encoding_unknown(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath(
        "junit-encoding-unknown.xml"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 126


def test_parse_junit_report_fromstring(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath(
        "junit-common-normal"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromstring(report_filepath.read_text())
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 3


def test_parse_junit_report_props(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath(
        "junit-custom-props"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 1
    testsuite = junit_report.testsuites[0]
    assert len(testsuite.properties) == 3

    expect_props = {
        "environment": "Linux",
        "platform": "PY-3.12.1",
        "machine": "aarch64",
    }
    actual_props = {}
    for prop in testsuite.properties:
        actual_props[prop.name] = prop.value

    assert actual_props == expect_props


def test_parse_junit_report_quoted(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath(
        "junit-custom-quoted"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 2
    assert junit_report.testsuites[0].testcases[0].name == "test_ok ” is missing"
    assert junit_report.testsuites[0].testcases[1].name == 'test_bad " is missing'


def test_merge_junit_report_from_directory(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath("many")
    junit_merger = JUnitReportMerger.from_directory(directory=report_filepath)
    junit_merger.merge()
    result = junit_merger.result
    assert result.tests == 35993


def test_merge_junit_report_from_reports(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath("many")
    files = report_filepath.iterdir()
    reports = []
    for file in files:
        if file.is_file():
            parser = JUnitReportParser.fromstring(file.read_text())
            parser.parse()
            report = parser.result
            reports.append(report)
    junit_merger = JUnitReportMerger.from_reports(reports)
    junit_merger.merge()
    result = junit_merger.result
    assert result.tests == 35993


def test_convert_junit_to_testbrain(directory_resource_samples_junit):
    report_filepath = directory_resource_samples_junit.joinpath(
        "junit-common-normal"
    ).with_suffix(".xml")
    junit_parser = JUnitReportParser.fromfile(report_filepath)
    junit_parser.parse()
    junit_report = junit_parser.result
    assert junit_report.tests == 3
    junit2testbrain = JUnit2TestbrainReportConverter(source=junit_report)
    junit2testbrain.convert()
    testbrain_report = junit2testbrain.result
    assert testbrain_report.total == 3
