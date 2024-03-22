import typing as t

from .. import utils
from ..models.mstest import (
    MSTestExecution,
    MSTestOutcome,
    MSTestResultSummary,
    MSTestTestMethod,
    MSTestTestRun,
    MSTestTimes,
    MSTestUnitTest,
    MSTestUnitTestResult,
)
from .base import XMLReportParser

if t.TYPE_CHECKING:
    try:
        from lxml import etree
    except ImportError:
        from xml.etree import ElementTree as etree  # noqa


class MSTestReportParser(XMLReportParser):
    _test: MSTestTestRun

    def __init__(self, xml):
        super().__init__(xml)
        self._test = MSTestTestRun()

    @classmethod
    def from_root(cls, root: "etree.Element"):
        instance = super().from_root(root=root)
        if instance.xml.tag != f"{instance.namespace}TestRun":
            raise ValueError("Incorrect Report Format")
        return instance

    @property
    def result(self) -> MSTestTestRun:
        return self._test

    def parse(self) -> MSTestTestRun:
        self.read_root()
        self.read_times()
        self.read_result_summary()
        self.read_test_definitions()
        self.read_unit_test_results()
        return self.result

    def read_root(self):
        self._test.id = self._xml.attrib.get("id")
        self._test.name = self._xml.attrib.get("name")
        self._test.run_user = self._xml.attrib.get("runUser")

    def read_times(self):
        times_element = self._xml.find(f"{self._namespace}Times")
        if times_element is not None:
            self._test.times = MSTestTimes(
                creation=times_element.attrib.get("creation"),
                queuing=times_element.attrib.get("queuing"),
                start=times_element.attrib.get("start"),
                finish=times_element.attrib.get("finish"),
            )

    def read_result_summary(self):
        result_summary_element = self._xml.find(f"{self._namespace}ResultSummary")
        if result_summary_element is not None:
            counters_element = result_summary_element.find(f"{self._namespace}Counters")
            output_element = result_summary_element.find(f"{self._namespace}Output")

            outcome = result_summary_element.attrib.get("outcome")
            errors = executed = passed = failed = total = None
            std_out = None

            if counters_element is not None:
                errors = counters_element.attrib.get("errors")
                executed = counters_element.attrib.get("executed")
                passed = counters_element.attrib.get("passed")
                failed = counters_element.attrib.get("failed")
                total = counters_element.attrib.get("total")

            if output_element is not None:
                std_out = result_summary_element.findtext(
                    f"{self._namespace}StdOut", default=""
                )

            self._test.result_summary = MSTestResultSummary(
                outcome=outcome,
                errors=errors,
                executed=executed,
                passed=passed,
                failed=failed,
                total=total,
                std_out=std_out,
            )

    def read_test_definitions(self):
        test_definitions_element = self._xml.find(f"{self._namespace}TestDefinitions")

        if test_definitions_element is not None:
            for unit_test_element in test_definitions_element.findall(
                f"{self._namespace}UnitTest"
            ):
                trx_unit_test = MSTestUnitTest(
                    id=unit_test_element.attrib.get("id"),
                    name=unit_test_element.attrib.get("name"),
                    storage=unit_test_element.attrib.get("storage"),
                )

                self._test.test_definitions.append(trx_unit_test)

                execution_element = unit_test_element.find(
                    f"{self._namespace}Execution"
                )
                testmethod_element = unit_test_element.find(
                    f"{self._namespace}TestMethod"
                )

                if testmethod_element is not None:
                    trx_unit_test.execution = MSTestExecution(
                        id=execution_element.attrib.get("id")
                    )

                if testmethod_element is not None:
                    trx_unit_test.testmethod = MSTestTestMethod(
                        class_name=testmethod_element.attrib.get("className"),
                        code_base=testmethod_element.attrib.get("codeBase"),
                        adapter_type_name=testmethod_element.attrib.get(
                            "adapterTypeName"
                        ),
                        name=utils.parse_type_info(
                            testmethod_element.attrib.get("name")
                        ),
                    )

    def _get_result_items(
        self, result_element: "etree.Element"
    ) -> t.List["etree.Element"]:
        utr = result_element.findall(f"{self._namespace}UnitTestResult")
        tra = result_element.findall(f"{self._namespace}TestResultAggregation")
        gtr = result_element.findall(f"{self._namespace}GenericTestResult")
        tr = result_element.findall(f"{self._namespace}TestResult")
        mtr = result_element.findall(f"{self._namespace}ManualTestResult")
        return utr + tra + gtr + tr + mtr

    def read_unit_test_results(self):
        results_element = self._xml.find(f"{self._namespace}Results")

        if results_element is not None:
            for result_element in self._get_result_items(results_element):
                inner_results_element = result_element.find(
                    f"{self._namespace}InnerResults"
                )

                if inner_results_element is None:
                    trx_unit_test_result = self._parse_unit_test_result(result_element)
                    self._test.unit_test_results.append(trx_unit_test_result)
                else:
                    has_failed = False

                    for inner_result_element in inner_results_element.findall(
                        f"{self._namespace}UnitTestResult"
                    ):
                        trx_unit_test_result = self._parse_unit_test_result(
                            inner_result_element
                        )
                        self._test.unit_test_results.append(trx_unit_test_result)

                        if trx_unit_test_result.outcome == MSTestOutcome.failed:
                            has_failed = True

                    # MsTest counts the wrapper test, but we won't count it
                    # https://github.com/gfoidl/trx2junit/pull/40#issuecomment-484682771
                    if self._test.result_summary is not None:
                        self._test.result_summary.total -= 1

                        if has_failed:
                            self._test.result_summary.failed -= 1

    def _parse_unit_test_result(
        self, result_element: "etree.Element"
    ) -> MSTestUnitTestResult:
        trx_unit_test_result = MSTestUnitTestResult(
            execution_id=result_element.attrib.get("executionId"),
            test_id=result_element.attrib.get("testId"),
            test_name=result_element.attrib.get("testName"),
            computer_name=result_element.attrib.get("computerName"),
            duration=utils.timespan_to_float(result_element.attrib.get("duration")),
            start_time=utils.string_to_datetime(result_element.attrib.get("startTime")),
            end_time=utils.string_to_datetime(result_element.attrib.get("endTime")),
            test_type=result_element.attrib.get("testType"),
            outcome=result_element.attrib.get("outcome"),
            test_list_id=result_element.attrib.get("testListId"),
            relative_results_directory=result_element.attrib.get(
                "relativeResultsDirectory"
            ),
        )

        output_element = result_element.find(f"{self._namespace}Output")
        if output_element is not None:
            error_info_element = output_element.find(f"{self._namespace}ErrorInfo")
            if error_info_element is not None:
                message_element = error_info_element.find(f"{self._namespace}Message")
                stacktrace_element = error_info_element.find(
                    f"{self._namespace}StackTrace"
                )

                if message_element is not None:
                    trx_unit_test_result.message = message_element.text

                if stacktrace_element is not None:
                    trx_unit_test_result.stacktrace = stacktrace_element.text

            trx_unit_test_result.std_out = output_element.findtext(
                f"{self._namespace}StdOut", default=""
            )
            trx_unit_test_result.std_err = output_element.findtext(
                f"{self._namespace}StdErr", default=""
            )

        if trx_unit_test_result.duration == 0.0:
            trx_unit_test_result.duration = trx_unit_test_result.run_time

        return trx_unit_test_result
