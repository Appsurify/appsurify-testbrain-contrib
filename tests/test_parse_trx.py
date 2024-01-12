import datetime
import pytest
import pathlib
from testbrain.contrib.reports.parsers import trx


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


def test_parse_trx_normal(trx_buildagent):
    report = trx_buildagent
    trx_parser = trx.TrxParser(string=report)
    result = trx_parser.parse()
    assert True


def test_parse_trx_big(trx_philips):
    report = trx_philips
    trx_parser = trx.TrxParser(string=report)
    result = trx_parser.parse()
    assert True
