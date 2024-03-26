import datetime
import enum
import typing as t

from pydantic import BaseModel, Field

from .. import utils

if t.TYPE_CHECKING:
    try:
        from lxml import etree
    except ImportError:
        from xml.etree import ElementTree as etree  # noqa


class AllureStatus(str, enum.Enum):
    passed = "passed"
    skipped = "skipped"
    failed = "failed"
    broken = "broken"
    unknown = "unknown"

    @classmethod
    def _missing_(cls, value: str):
        for member in cls:  # noqa
            if member.lower() == value.lower():
                return member
        return None


class AllureKV(BaseModel):
    name: t.Optional[str] = ""
    value: t.Optional[str] = ""


class AllureTime(BaseModel):
    start: t.Optional[int] = 0
    stop: t.Optional[int] = 0
    duration: t.Optional[int] = 0


class AllureTestcase(BaseModel):
    uid: t.Optional[str] = ""
    name: t.Optional[str] = ""
    full_name: t.Optional[str] = ""
    description: t.Optional[str] = ""
    start: t.Optional[int] = 0
    stop: t.Optional[int] = 0
    status: t.Optional[AllureStatus] = AllureStatus.unknown
    status_message: t.Optional[str] = ""
    status_trace: t.Optional[str] = ""
    time: t.Optional[AllureTime] = AllureTime()
    labels: t.Optional[t.List[AllureKV]] = []
    # parameters: t.Optional[t.List[AllureKV]] = []
    parameters: t.Optional[t.List[t.Union[AllureKV, str]]] = []


class AllureSuite(BaseModel):
    uid: t.Optional[str] = ""
    name: t.Optional[str] = ""
    children: t.Optional[t.List[AllureTestcase]] = []


class AllureReport(BaseModel):
    uid: t.Optional[str] = ""
    name: t.Optional[str] = ""
    children: t.Optional[t.List[AllureSuite]] = []
