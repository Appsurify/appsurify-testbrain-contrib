import typing as t
from itertools import groupby
from operator import itemgetter

from ..models.junit import JUnitResult, JUnitTestCase, JUnitTestSuite, JUnitTestSuites
from ..models.testbrain import TestbrainTest, TestbrainTestRun, TestbrainTestSuite
from ..models.trx import TrxTestDefinition, TrxTestRun, TrxUnitTestResult


class TrxConverter(object):
    _source: TrxTestRun
    _destination: t.Union[JUnitTestSuites, TestbrainTestSuite]
    _counters: "Counters"
    _test_id: int = 0
    _trx_test_definition_lookup: t.Dict[str, TrxUnitTestResult] = {}
    _test_definitions: t.Iterable

    class Counters:  # noqa
        test_count = 0
        failures = 0
        errors = 0
        skipped = 0
        passed = 0
        time = 0.0
        timestamp = None

    def __init__(self, source: TrxTestRun):
        self._source = source
        self.prepare_trx()

    @property
    def source(self) -> TrxTestRun:
        return self._source

    @property
    def destination(self) -> t.Union[JUnitTestSuites, TestbrainTestSuite]:
        return self._destination

    def reset_counters(self) -> None:
        self._counters = self.Counters()

    def prepare_trx(self):
        for unit_test_result in self._source.unit_test_results:
            self._trx_test_definition_lookup[
                unit_test_result.test_id
            ] = unit_test_result

        self._test_definitions = [
            item.model_dump() for item in self._source.test_definitions
        ]
        self._test_definitions = sorted(
            self._test_definitions, key=itemgetter("test_class")
        )

    def resolve_status(self, trx_unit_test_result: TrxUnitTestResult) -> str:  # noqa
        status = "unknown"
        if trx_unit_test_result.outcome in (
            "Completed",
            "Passed",
            "PassedButRunAborted",
        ):
            status = "passed"
        elif trx_unit_test_result.outcome in [
            "NotExecuted",
            "NotRunnable",
            "Disconnected",
        ]:
            status = "skipped"
        elif trx_unit_test_result.outcome in [
            "Error",
        ]:
            status = "error"
        elif trx_unit_test_result.outcome in ["Aborted", "Failed", "Timeout"]:
            status = "failure"
        return status

    def convert(self) -> t.Union[JUnitTestSuites, TestbrainTestSuite]:
        raise NotImplementedError


class Trx2JunitConverter(TrxConverter):
    def __init__(self, source: TrxTestRun):
        super().__init__(source=source)
        self._destination = JUnitTestSuites()

    def convert(self) -> JUnitTestSuites:
        for testsuite_name, trx_test_definitions in groupby(
            self._test_definitions, key=itemgetter("test_class")
        ):
            self._add_testsuite(testsuite_name, trx_test_definitions)

        self._destination.update_statistics()
        return self._destination

    def _add_testsuite(
        self, testsuite_name: str, trx_test_definitions: t.List[TrxTestDefinition]
    ) -> None:
        # reset_counter
        self.reset_counters()

        junit_testsuite = JUnitTestSuite()
        self._destination.add_testsuite(junit_testsuite)

        junit_testsuite.name = testsuite_name
        junit_testsuite.id = self._test_id
        self._test_id += 1

        for trx_test_definition in list(trx_test_definitions):
            self._add_testcase(
                junit_testsuite, TrxTestDefinition.model_validate(trx_test_definition)
            )

        junit_testsuite.tests = self._counters.test_count
        junit_testsuite.failures = self._counters.failures
        junit_testsuite.errors = self._counters.errors
        junit_testsuite.skipped = self._counters.skipped
        junit_testsuite.passed = self._counters.passed
        junit_testsuite.time = self._counters.time
        junit_testsuite.timestamp = self._counters.timestamp

        junit_testsuite.update_statistics()

    def _add_testcase(
        self, junit_testsuite: JUnitTestSuite, trx_test_definition: TrxTestDefinition
    ) -> None:
        trx_unit_test_result: TrxUnitTestResult = self._trx_test_definition_lookup.get(
            trx_test_definition.id, None
        )
        if trx_unit_test_result is not None:
            self._counters.test_count += 1
            junit_testcase = JUnitTestCase()
            junit_testsuite.add_testcase(testcase=junit_testcase)
            junit_testsuite.hostname = trx_unit_test_result.computer_name
            junit_testcase.name = trx_unit_test_result.test_name
            junit_testcase.classname = trx_test_definition.test_class

            junit_testcase.system_out = trx_unit_test_result.std_out
            junit_testcase.system_err = trx_unit_test_result.std_err

            if self._counters.timestamp is None:
                self._counters.timestamp = trx_unit_test_result.start_time

            if trx_unit_test_result.duration is not None:
                duration = trx_unit_test_result.duration
                self._counters.time += duration
                junit_testcase.time = duration

            junit_result = JUnitResult()
            junit_result.status = self.resolve_status(trx_unit_test_result)
            junit_result.type = ""
            junit_result.message = trx_unit_test_result.message
            junit_result.stacktrace = trx_unit_test_result.stacktrace

            junit_testcase.result = junit_result
