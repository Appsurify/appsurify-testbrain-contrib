import pathlib

from testbrain.contrib.report.parsers import *
from testbrain.contrib.report.converters import *


trx_report_filename = pathlib.Path(
    "../resources/samples/trx-buildagent-2021-11-02-09-31-24.trx"
)
# junit_report_filename = pathlib.Path("../resources/samples/junit-out-err.xml")
junit_report_filename = pathlib.Path("../resources/samples/junit-no-suites-tag.xml")


junit_parser = JUnitReportParser.fromstring(text=junit_report_filename.read_text())
junit_parser.parse()
junit_report = junit_parser.result


junit_converter = JUnit2TestbrainReportConverter(junit_report)
junit_converter.convert()
testbrain_report = junit_converter.result

testbrain_report_json = junit_converter.result_json

print("Success")
