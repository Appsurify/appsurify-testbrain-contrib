import datetime
import pytest
import pathlib
from testbrain.contrib.reports.parsers import junit


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


def test_parse_junit_normal(xml_junit_normal):
    report = xml_junit_normal.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2

    assert result.testsuites[0].name == "JUnitXmlReporter"
    assert result.testsuites[0].errors == 0
    assert result.testsuites[0].skipped == 0
    assert result.testsuites[0].tests == 0
    assert result.testsuites[0].failures == 0
    assert result.testsuites[0].time == 0.0
    assert result.testsuites[0].timestamp == "2013-05-24T10:23:58"

    assert result.testsuites[1].name == "JUnitXmlReporter.constructor"
    assert result.testsuites[1].errors == 0
    assert result.testsuites[1].skipped == 1
    assert result.testsuites[1].tests == 3
    assert result.testsuites[1].failures == 1
    assert result.testsuites[1].time == 0.006
    assert result.testsuites[1].timestamp == "2013-05-24T10:23:58"

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
    junit_parser = junit.JUnitParser(filename=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2


def test_parse_junit_no_fails(xml_junit_no_fails):
    report = xml_junit_no_fails.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 2


def test_parse_junit_no_suites_tag(xml_junit_no_suites_tag):
    report = xml_junit_no_suites_tag.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 1


def test_parse_junit_sample_out_err(xml_junit_sample_out_err):
    report = xml_junit_sample_out_err.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()
    assert result.name == ""


def test_parse_junit_android_robolectric_success(xml_junit_android_robolectric_success):
    report = xml_junit_android_robolectric_success.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()
    assert result.name == ""


def test_parse_junit_ibm(xml_junit_ibm):
    report = xml_junit_ibm.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()
    assert result.id == "20140612_170519"
    assert result.name == "New_configuration (14/06/12 17:05:19)"


def test_parse_junit_multi_testsuites_min(xml_junit_multi_testsuites_min):
    report = xml_junit_multi_testsuites_min.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 3


def test_parse_junit_jenkins(xml_junit_jenkins):
    report = xml_junit_jenkins.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 4


def test_parse_junit_legacy(xml_junit_legacy):
    report = xml_junit_legacy.read_text()
    junit_parser = junit.JUnitParser(string=report)
    result = junit_parser.parse()

    assert result.name == ""
    assert len(result.testsuites) == 1
