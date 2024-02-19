import datetime
import enum
import typing as t

from pydantic import BaseModel

from .. import utils

if t.TYPE_CHECKING:
    try:
        from lxml import etree
    except ImportError:
        from xml.etree import ElementTree as etree  # noqa


class MSTestOutcome(str, enum.Enum):
    aborted = "Aborted"
    completed = "Completed"
    disconnected = "Disconnected"
    error = "Error"
    failed = "Failed"
    inconclusive = "Inconclusive"
    in_progress = "InProgress"
    not_executed = "NotExecuted"
    not_runnable = "NotRunnable"
    passed = "Passed"
    passed_but_run_aborted = "PassedButRunAborted"
    pending = "Pending"
    timeout = "Timeout"
    warning = "Warning"

    @classmethod
    def _missing_(cls, value: str):
        for member in cls:  # noqa
            if member.lower() == value.lower():
                return member
        return None


class MSTestUnitTestResult(BaseModel):
    execution_id: t.Optional[str] = ""
    test_id: t.Optional[str] = ""
    test_name: t.Optional[str] = ""
    computer_name: t.Optional[str] = ""
    duration: t.Optional[float] = 0.0
    start_time: t.Optional[datetime.datetime] = datetime.datetime.now()
    end_time: t.Optional[datetime.datetime] = datetime.datetime.now()
    test_type: t.Optional[str] = ""
    outcome: t.Optional[MSTestOutcome] = None
    test_list_id: t.Optional[str] = ""
    relative_results_directory: t.Optional[str] = ""
    message: t.Optional[str] = ""
    stacktrace: t.Optional[str] = ""
    std_out: t.Optional[str] = ""
    std_err: t.Optional[str] = ""

    @property
    def run_time(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class MSTestExecution(BaseModel):
    id: t.Optional[str] = ""


class MSTestTestMethod(BaseModel):
    name: t.Optional[str] = ""
    class_name: t.Optional[str] = ""
    code_base: t.Optional[str] = ""
    adapter_type_name: t.Optional[str] = ""


class MSTestUnitTest(BaseModel):
    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    storage: t.Optional[str] = ""
    execution: t.Optional[MSTestExecution] = None
    testmethod: t.Optional[MSTestTestMethod] = None

    @property
    def key(self) -> t.Optional[str]:
        return self.testmethod.class_name


class MSTestResultSummary(BaseModel):
    outcome: t.Optional[MSTestOutcome] = MSTestOutcome.passed
    std_out: t.Optional[str] = ""
    total: t.Optional[int] = 0
    executed: t.Optional[int] = 0
    passed: t.Optional[int] = 0
    failed: t.Optional[int] = 0
    errors: t.Optional[int] = 0


class MSTestTimes(BaseModel):
    creation: t.Optional[datetime.datetime] = datetime.datetime.now()
    queuing: t.Optional[datetime.datetime] = datetime.datetime.now()
    start: t.Optional[datetime.datetime] = datetime.datetime.now()
    finish: t.Optional[datetime.datetime] = datetime.datetime.now()

    @property
    def run_time(self):
        return (self.finish - self.creation).total_seconds()


class MSTestTestRun(BaseModel):
    id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    run_user: t.Optional[str] = ""
    times: t.Optional[MSTestTimes] = None
    result_summary: t.Optional[MSTestResultSummary] = None
    test_definitions: t.List[MSTestUnitTest] = []
    unit_test_results: t.List[MSTestUnitTestResult] = []

    def model_dump_xml(self) -> str:
        raise NotImplementedError()
