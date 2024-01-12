import datetime
import pytest
import pathlib
from testbrain.contrib.reports.parsers.trx import TrxParser
from testbrain.contrib.reports.converters.trx import Trx2JunitConverter


base_dir = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture(scope="module")
def trx_buildagent():
    filename = (
        base_dir / "resources" / "samples" / "trx-buildagent-2021-11-02-09-31-24.trx"
    )
    return filename.read_text()


@pytest.fixture(scope="module")
def trx_philips():
    filename = base_dir / "resources" / "samples" / "trx-philips-demo-report.trx"
    return filename.read_text()


def test_convert_trx_2_junit(trx_buildagent):
    report = trx_buildagent
    trx_parser = TrxParser(string=report)
    trx_testrun = trx_parser.parse()

    trx_2_junit = Trx2JunitConverter(source=trx_testrun)
    junit_report = trx_2_junit.convert()

    assert True


def test_convert_trx_2_junit_min(trx_philips):
    report = trx_philips
    trx_parser = TrxParser(string=report)
    trx_testrun = trx_parser.parse()

    trx_2_junit = Trx2JunitConverter(source=trx_testrun)
    junit_report = trx_2_junit.convert()

    assert True
