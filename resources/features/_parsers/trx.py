import pathlib

import typing as t

# from lxml import etree
# try:
#     from lxml import etree
# except ImportError:
#     from xml.etree import ElementTree as etree
from xml.etree import ElementTree as etree


from testbrain.contrib.report import utils
from testbrain.contrib.report.models import trx


class TrxParser(object):
    _namespace: str = ""
    _data: t.AnyStr = None
    _report: etree.Element = None
    _result: trx.TrxTestRun = None

    def __init__(
        self, string: t.Optional[str] = None, filename: t.Optional[pathlib.Path] = None
    ):
        if string and filename:
            raise AssertionError("both string and filename")

        if string:
            self._fromstring(string=string)
        elif filename:
            self._fromfile(filename=filename)

        self.namespace = utils.get_namespace(self._report)

        self._result = trx.TrxTestRun()

    def _fromfile(self, filename: pathlib.Path):
        self._data = filename.read_bytes()
        self._report = etree.fromstring(text=self._data)

    def _fromstring(self, string: t.AnyStr):
        if isinstance(string, str):
            string = string.encode(encoding="utf-8")
        self._data = string
        self._report = etree.fromstring(text=self._data)

    @property
    def result(self) -> trx.TrxTestRun:
        return self._result

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, ns: t.Optional[str] = None):
        if ns:
            self._namespace = ns
        else:
            self._namespace = "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"

    def read_times(self) -> None:
        trx_times = trx.MSTestTimes()
        times_element = self._report.find(self.namespace + "Times")
        if times_element is not None:
            trx_times.creation = times_element.attrib.get("creation", "")
            trx_times.queuing = times_element.attrib.get("queuing", "")
            trx_times.start = times_element.attrib.get("start", "")
            trx_times.finish = times_element.attrib.get("finish", "")
        self._result.times = trx_times

    def read_result_summary(self) -> None:
        trx_result_summary = trx.MSTestResultSummary()
        result_summary_element = self._report.find(self.namespace + "ResultSummary")
        if result_summary_element is not None:
            trx_result_summary.outcome = result_summary_element.attrib.get(
                "outcome", ""
            )
            counters_element = result_summary_element.find(self.namespace + "Counters")
            if counters_element is not None:
                trx_result_summary.errors = int(
                    counters_element.attrib.get("errors", 0)
                )
                trx_result_summary.executed = int(
                    counters_element.attrib.get("executed", 0)
                )
                trx_result_summary.passed = int(
                    counters_element.attrib.get("passed", 0)
                )
                trx_result_summary.failed = int(
                    counters_element.attrib.get("failed", 0)
                )
                trx_result_summary.total = int(counters_element.attrib.get("total", 0))
            output_element = result_summary_element.find(self.namespace + "Output")
            if output_element is not None:
                std_out = output_element.findtext(self.namespace + "StdOut", default="")
                trx_result_summary.std_out = std_out
        self._result.result_summary = trx_result_summary

    def read_test_definitions(self) -> None:
        trx_test_definitions = []

        test_definitions_element = self._report.find(self.namespace + "TestDefinitions")
        if test_definitions_element is not None:
            for test_definition_element in test_definitions_element.findall(
                self.namespace + "UnitTest"
            ):
                trx_test_definition = trx.TrxTestDefinition()
                trx_test_definition.id = test_definition_element.attrib.get("id", "")
                trx_test_definition.name = test_definition_element.attrib.get(
                    "name", ""
                )
                execution_element = test_definition_element.find(
                    self.namespace + "Execution"
                )
                if execution_element is not None:
                    trx_test_definition.execution_id = execution_element.attrib.get(
                        "id", ""
                    )
                test_method_element = test_definition_element.find(
                    self.namespace + "TestMethod"
                )
                if test_method_element is not None:
                    trx_test_definition.test_class = test_method_element.attrib.get(
                        "className", ""
                    )
                    name = test_method_element.attrib.get("name", "")
                    trx_test_definition.test_method = parse_type_info(name)

                trx_test_definitions.append(trx_test_definition)

        self._result.test_definitions = trx_test_definitions

    def parse_unit_test_result(
        self, unit_test_result_element: etree.Element
    ) -> trx.MSTestUnitTestResult:
        trx_unit_test_result = trx.MSTestUnitTestResult()

        trx_unit_test_result.duration = utils.timespan_to_float(
            unit_test_result_element.attrib.get("duration", "")
        )
        trx_unit_test_result.start_time = unit_test_result_element.attrib.get(
            "startTime", ""
        )
        trx_unit_test_result.end_time = unit_test_result_element.attrib.get(
            "endTime", ""
        )
        trx_unit_test_result.execution_id = unit_test_result_element.attrib.get(
            "executionId", ""
        )

        trx_unit_test_result.test_id = unit_test_result_element.attrib.get("testId", "")
        trx_unit_test_result.test_name = unit_test_result_element.attrib.get(
            "testName", ""
        )
        trx_unit_test_result.computer_name = unit_test_result_element.attrib.get(
            "computerName", ""
        )

        trx_unit_test_result.outcome = unit_test_result_element.attrib.get(
            "outcome", ""
        )

        output_element = unit_test_result_element.find(self.namespace + "Output")
        if output_element is not None:
            error_info_element = output_element.find(self.namespace + "ErrorInfo")
            if error_info_element is not None:
                message_element = error_info_element.find(self.namespace + "Message")
                if message_element is not None:
                    trx_unit_test_result.message = message_element.text
                stacktrace_element = error_info_element.find(
                    self.namespace + "StackTrace"
                )
                if stacktrace_element is not None:
                    trx_unit_test_result.stacktrace = stacktrace_element.text

            trx_unit_test_result.std_out = output_element.findtext(
                self.namespace + "StdOut"
            )
            trx_unit_test_result.std_err = output_element.findtext(
                self.namespace + "StdErr"
            )

        # if not duration ... need calculate
        if trx_unit_test_result.duration == 0.0:
            trx_unit_test_result.duration = trx_unit_test_result.run_time
        return trx_unit_test_result

    def read_unit_test_results(self) -> None:
        trx_unit_test_results = []

        unit_test_results_element = self._report.find(self.namespace + "Results")

        unit_test_results_a = unit_test_results_element.findall(
            f"{self.namespace}UnitTestResult"
        )
        unit_test_results_b = unit_test_results_element.findall(
            f"{self.namespace}TestResultAggregation"
        )
        unit_test_results_c = unit_test_results_element.findall(
            f"{self.namespace}GenericTestResult"
        )
        unit_test_results_d = unit_test_results_element.findall(
            f"{self.namespace}TestResult"
        )
        unit_test_results_e = unit_test_results_element.findall(
            f"{self.namespace}ManualTestResult"
        )

        unit_test_results_items = (
            unit_test_results_a
            + unit_test_results_b
            + unit_test_results_c
            + unit_test_results_d
            + unit_test_results_e
        )

        for unit_test_results_item in unit_test_results_items:
            inner_results_element = unit_test_results_item.find(
                f"{self.namespace}InnerResults"
            )
            if inner_results_element is not None:
                has_failed = False
                for inner_result in inner_results_element.findall(
                    f"{self.namespace}UnitTestResult"
                ):
                    trx_unit_test_result = self.parse_unit_test_result(
                        unit_test_result_element=inner_result
                    )
                    if trx_unit_test_result.outcome == "Failed":
                        has_failed = True
                    trx_unit_test_results.append(trx_unit_test_result)

                # MsTest counts the wrapper test, but we won't count it
                # https://github.com/gfoidl/trx2junit/pull/40#issuecomment-484682771
                self._result.result_summary.total -= 1
                if has_failed:
                    self._result.result_summary.failed -= 1

            else:
                trx_unit_test_result = self.parse_unit_test_result(
                    unit_test_result_element=unit_test_results_item
                )
                trx_unit_test_results.append(trx_unit_test_result)

        self._result.unit_test_results = trx_unit_test_results

    def parse(self) -> trx.TrxTestRun:
        self.read_times()
        self.read_result_summary()
        self.read_test_definitions()
        self.read_unit_test_results()
        return self.result
