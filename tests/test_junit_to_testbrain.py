import datetime
import pytest
import pathlib
from testbrain.contrib.reports.parsers.junit import JUnitParser
from testbrain.contrib.reports.converters.junit import JUnit2TestbrainConverter


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture(scope="module")
def xml_junit_normal():
    filename = base_dir / "resources" / "samples" / "junit-normal.xml"
    return filename


@pytest.fixture()
def xml_junit_legacy():
    filename = base_dir / "resources" / "samples" / "junit-legacy.xml"
    return filename


def test_convert_junit_2_testbrain_normal(xml_junit_normal):
    report = xml_junit_normal.read_text()
    junit_parser = JUnitParser(string=report)
    junit_report = junit_parser.parse()

    junit_2_testbrain = JUnit2TestbrainConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    assert True


def test_convert_junit_2_testbrain_legacy(xml_junit_legacy):
    report = xml_junit_legacy.read_text()
    junit_parser = JUnitParser(string=report)
    junit_report = junit_parser.parse()

    junit_2_testbrain = JUnit2TestbrainConverter(source=junit_report)
    testbrain_report = junit_2_testbrain.convert()

    assert True
