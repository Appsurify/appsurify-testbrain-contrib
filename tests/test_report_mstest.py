import pytest
import pathlib

from testbrain.contrib.report.mergers.junit import JUnitReportMerger
from testbrain.contrib.report.parsers import MSTestReportParser
from testbrain.contrib.report.converters import (
    MSTest2TestbrainReportConverter,
    MSTest2JUnitReportConverter,
)


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture(scope="module")
def trx_buildagent():
    filename = (
        base_dir / "resources" / "samples" / "trx-buildagent-2021-11-02-09-31-24.trx"
    )
    return filename


@pytest.fixture(scope="module")
def trx_buildagent_bom():
    filename = (
        base_dir
        / "resources"
        / "samples"
        / "trx-buildagent-2021-11-02-09-31-24-BOM.trx"
    )
    return filename


@pytest.fixture(scope="module")
def trx_philips():
    filename = base_dir / "resources" / "samples" / "trx-philips-demo-report.trx"
    return filename


def test_parse_trx_normal(trx_buildagent):
    report = trx_buildagent.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    result = trx_parser.parse()
    assert True


def test_parse_trx_normal_bom(trx_buildagent_bom):
    report = trx_buildagent_bom.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    result = trx_parser.parse()
    assert True


def test_parse_trx_big(trx_philips):
    report = trx_philips.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    result = trx_parser.parse()
    assert True


def test_convert_mstest_2_testbrain(trx_buildagent):
    report = trx_buildagent.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    trx_testrun = trx_parser.parse()

    trx_2_testbrain = MSTest2TestbrainReportConverter(source=trx_testrun)
    testbrain_report = trx_2_testbrain.convert()

    assert len(trx_testrun.test_definitions) == testbrain_report.total


def test_convert_trx_2_testbrain_big(trx_philips):
    report = trx_philips.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    trx_testrun = trx_parser.parse()

    trx_2_testbrain = MSTest2TestbrainReportConverter(source=trx_testrun)
    testbrain_report = trx_2_testbrain.convert()

    assert len(trx_testrun.test_definitions) == testbrain_report.total


def test_convert_trx_2_junit(trx_buildagent):
    report = trx_buildagent.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    trx_testrun = trx_parser.parse()

    trx_2_junit = MSTest2JUnitReportConverter(source=trx_testrun)
    junit_report = trx_2_junit.convert()

    assert len(trx_testrun.test_definitions) == junit_report.tests


def test_convert_trx_2_junit_min(trx_philips):
    report = trx_philips.read_text(encoding="utf-8")
    trx_parser = MSTestReportParser.fromstring(text=report)
    trx_testrun = trx_parser.parse()

    trx_2_junit = MSTest2JUnitReportConverter(source=trx_testrun)
    junit_report = trx_2_junit.convert()

    assert len(trx_testrun.test_definitions) == junit_report.tests


def test_convert_and_merge_two_mstest(trx_philips, trx_buildagent):
    reports = []
    expect_tests = 0
    expect_passed = 0
    expect_time = 0
    expect_testsuites = 0

    for infile in [trx_philips, trx_buildagent]:
        parser = MSTestReportParser.fromstring(text=infile.read_text(encoding="utf-8"))
        parser.parse()
        report = parser.result
        converter = MSTest2JUnitReportConverter(source=report)
        converter.convert()
        junit_report = converter.result
        reports.append(junit_report)

        expect_tests += junit_report.tests
        expect_passed += junit_report.passed
        expect_time += junit_report.time
        expect_testsuites += len(junit_report.testsuites)

    junit_merger = JUnitReportMerger.from_reports(reports=reports)
    junit_merger.merge()

    junit_merged_report = junit_merger.result
    junit_merged_report_xml = junit_merger.result_xml

    assert len(junit_merged_report.testsuites) == expect_testsuites
    assert junit_merged_report.time == expect_time
    assert junit_merged_report.passed == expect_passed
    assert junit_merged_report.tests == expect_tests
