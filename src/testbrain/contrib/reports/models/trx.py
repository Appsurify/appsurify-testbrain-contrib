import datetime
import typing as t

from pydantic import BaseModel, Field


class TrxUnitTestResult(BaseModel):
    execution_id: t.Optional[str] = ""
    test_id: t.Optional[str] = ""
    test_name: t.Optional[str] = ""
    duration: t.Optional[float] = 0.0
    start_time: t.Optional[datetime.datetime] = datetime.datetime.now()
    end_time: t.Optional[datetime.datetime] = datetime.datetime.now()

    outcome: t.Optional[str] = ""
    computer_name: t.Optional[str] = ""
    message: t.Optional[str] = ""
    stacktrace: t.Optional[str] = ""
    std_out: t.Optional[str] = ""
    std_err: t.Optional[str] = ""

    @property
    def run_time(self) -> float:
        return (self.end_time - self.start_time).total_seconds()


class TrxTimes(BaseModel):
    creation: t.Optional[datetime.datetime] = datetime.datetime.now()
    queuing: t.Optional[datetime.datetime] = datetime.datetime.now()
    start: t.Optional[datetime.datetime] = datetime.datetime.now()
    finish: t.Optional[datetime.datetime] = datetime.datetime.now()

    @property
    def run_time(self):
        return (self.finish - self.creation).total_seconds()


class TrxTestDefinition(BaseModel):
    id: t.Optional[str] = ""
    execution_id: t.Optional[str] = ""
    name: t.Optional[str] = ""
    test_class: t.Optional[str] = ""
    test_method: t.Optional[str] = ""


class TrxResultSummary(BaseModel):
    outcome: t.Optional[str] = ""
    std_out: t.Optional[str] = ""
    total: t.Optional[int] = 0
    executed: t.Optional[int] = 0
    passed: t.Optional[int] = 0
    failed: t.Optional[int] = 0
    errors: t.Optional[int] = 0


class TrxTestRun(BaseModel):
    times: t.Optional[TrxTimes] = None
    result_summary: t.Optional[TrxResultSummary] = None
    test_definitions: t.List[TrxTestDefinition] = []
    unit_test_results: t.List[TrxUnitTestResult] = []
