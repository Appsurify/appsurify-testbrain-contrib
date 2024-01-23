import datetime
import pytest
import pathlib

from testbrain.contrib.report import utils
from testbrain.contrib.report.models.testbrain import TestbrainTestSuite
from testbrain.contrib.report.parsers import JUnitReportParser
from testbrain.contrib.report.converters import JUnit2TestbrainReportConverter


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture()
def xml_junit_android_robolectric_success():
    filename = (
        base_dir / "resources" / "samples" / "junit-android-robolectric-success.xml"
    )
    return filename


@pytest.fixture()
def xml_junit_ibm():
    filename = base_dir / "resources" / "samples" / "junit-ibm.xml"
    return filename


@pytest.fixture()
def xml_junit_multi_testsuites_min():
    filename = (
        base_dir
        / "resources"
        / "samples"
        / "trx-buildagent-2021-11-02-09-31-24-min.xml"
    )
    return filename


@pytest.fixture()
def xml_junit_sample_out_err():
    filename = base_dir / "resources" / "samples" / "junit-out-err.xml"
    return filename


@pytest.fixture()
def xml_junit_normal():
    filename = base_dir / "resources" / "samples" / "junit-normal.xml"
    return filename


@pytest.fixture()
def xml_junit_legacy():
    filename = base_dir / "resources" / "samples" / "junit-legacy.xml"
    return filename


@pytest.fixture()
def xml_junit_no_fails():
    filename = base_dir / "resources" / "samples" / "junit-no-fails.xml"
    return filename


@pytest.fixture()
def xml_junit_no_suites_tag():
    filename = base_dir / "resources" / "samples" / "junit-no-suites-tag.xml"
    return filename


@pytest.fixture()
def xml_junit_jenkins():
    filename = base_dir / "resources" / "samples" / "junit-jenkins.xml"
    return filename


@pytest.fixture()
def xml_junit_with_props_big():
    filename = (
        base_dir / "resources" / "samples" / "junit_vector_suite_z3_lib_path_linux.xml"
    )
    return filename


def test_parse_junit_normal(xml_junit_normal):
    report = xml_junit_normal.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2

    assert result.testsuites[0].name == "JUnitXmlReporter"
    assert result.testsuites[0].errors == 0
    assert result.testsuites[0].skipped == 0
    assert result.testsuites[0].tests == 0
    assert result.testsuites[0].failures == 0
    assert result.testsuites[0].time == 0.0
    assert result.testsuites[0].timestamp == utils.string_to_datetime(
        "2013-05-24T10:23:58"
    )

    assert result.testsuites[1].name == "JUnitXmlReporter.constructor"
    assert result.testsuites[1].errors == 0
    assert result.testsuites[1].skipped == 1
    assert result.testsuites[1].tests == 3
    assert result.testsuites[1].failures == 1
    assert result.testsuites[1].time == 0.006
    assert result.testsuites[1].timestamp == utils.string_to_datetime(
        "2013-05-24T10:23:58"
    )

    assert len(result.testsuites[1].testcases) == 3
    assert (
        result.testsuites[1].testcases[0].name
        == "should default path to an empty string"
    )
    assert result.testsuites[1].testcases[0].classname == "JUnitXmlReporter.constructor"
    assert result.testsuites[1].testcases[0].time == 0.006
    assert result.testsuites[1].testcases[0].result.status == "failure"
    assert result.testsuites[1].testcases[0].result.message == "test failure"
    assert result.testsuites[1].testcases[0].result.stacktrace == "Assertion failed"

    assert (
        result.testsuites[1].testcases[1].name == "should default consolidate to true"
    )
    assert result.testsuites[1].testcases[1].classname == "JUnitXmlReporter.constructor"
    assert result.testsuites[1].testcases[1].time == 0.0
    assert result.testsuites[1].testcases[1].result.status == "skipped"
    assert result.testsuites[1].testcases[1].result.message == ""
    assert result.testsuites[1].testcases[1].result.stacktrace == ""

    assert (
        result.testsuites[1].testcases[2].name
        == "should default useDotNotation to true"
    )
    assert result.testsuites[1].testcases[2].classname == "JUnitXmlReporter.constructor"
    assert result.testsuites[1].testcases[2].time == 0.0
    assert result.testsuites[1].testcases[2].result.status == "passed"
    assert result.testsuites[1].testcases[2].result.message == ""
    assert result.testsuites[1].testcases[2].result.stacktrace == ""


def test_parse_junit_normal_from_file(xml_junit_normal):
    report = xml_junit_normal
    junit_parser = JUnitReportParser.fromfile(filename=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2

    assert len(result.testsuites[1].properties) == 3


def test_parse_junit_with_props_big(xml_junit_with_props_big):
    report = xml_junit_with_props_big
    junit_parser = JUnitReportParser.fromfile(filename=report)
    result = junit_parser.parse()

    assert len(result.testsuites[0].properties) == 1

    prop = result.testsuites[0].properties[0]
    assert prop.name == "platform"
    assert prop.value == "linux64"


def test_parse_junit_no_fails(xml_junit_no_fails):
    report = xml_junit_no_fails.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2


def test_parse_junit_no_suites_tag(xml_junit_no_suites_tag):
    report = xml_junit_no_suites_tag.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 1


def test_parse_junit_sample_out_err(xml_junit_sample_out_err):
    report = xml_junit_sample_out_err.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()
    assert result.name == ""


def test_parse_junit_android_robolectric_success(xml_junit_android_robolectric_success):
    report = xml_junit_android_robolectric_success.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()
    assert result.name == ""


def test_parse_junit_ibm(xml_junit_ibm):
    report = xml_junit_ibm.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()
    assert result.id == "20140612_170519"
    assert result.name == "New_configuration (14/06/12 17:05:19)"


def test_parse_junit_multi_testsuites_min(xml_junit_multi_testsuites_min):
    report = xml_junit_multi_testsuites_min.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 3


def test_parse_junit_jenkins(xml_junit_jenkins):
    report = xml_junit_jenkins.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2


def test_parse_junit_legacy(xml_junit_legacy):
    report = xml_junit_legacy.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 1


def test_convert_junit_2_testbrain_normal(xml_junit_normal):
    report = xml_junit_normal.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    junit_report = junit_parser.parse()

    junit_2_testbrain = JUnit2TestbrainReportConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    assert testbrain_report.total == junit_report.tests


def test_convert_junit_2_testbrain_legacy(xml_junit_legacy):
    report = xml_junit_legacy.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    junit_report = junit_parser.parse()

    assert junit_report.tests == 18

    junit_2_testbrain = JUnit2TestbrainReportConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    assert testbrain_report.total == junit_report.tests


def test_convert_junit_2_testbrain_no_suites_tag(xml_junit_no_suites_tag):
    report = xml_junit_no_suites_tag.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    junit_report = junit_parser.parse()

    junit_2_testbrain = JUnit2TestbrainReportConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    assert testbrain_report.total == junit_report.tests


def test_convert_junit_2_testbrain_with_props_big(xml_junit_with_props_big):
    report = xml_junit_with_props_big
    junit_parser = JUnitReportParser.fromfile(filename=report)
    junit_report = junit_parser.parse()

    junit_2_testbrain = JUnit2TestbrainReportConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    assert len(testbrain_report.testruns[0].properties) == 1

    prop = testbrain_report.testruns[0].properties[0]
    assert prop.name == "platform"
    assert prop.value == "linux64"


def test_convert_junit_2_testbrain_legacy_and_back(xml_junit_legacy):
    report = xml_junit_legacy.read_text(encoding="utf-8")
    junit_parser = JUnitReportParser.fromstring(text=report)
    junit_report = junit_parser.parse()

    assert junit_report.tests == 18

    junit_2_testbrain = JUnit2TestbrainReportConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    testbrain_report_json = junit_2_testbrain.result_json

    from_json = TestbrainTestSuite.model_validate_json(testbrain_report_json)

    assert testbrain_report == from_json
