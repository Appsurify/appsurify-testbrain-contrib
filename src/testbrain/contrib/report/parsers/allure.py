import datetime
import json
import pathlib
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa

from .. import utils
from ..models.allure import AllureReport, AllureSuite, AllureTestcase
from .base import JsonReportParser


class AllureReportParser(JsonReportParser):
    _target: AllureReport
    _report_dir: pathlib.Path

    def __init__(self, source):
        super().__init__(source)
        self._target = AllureReport()

    @classmethod
    def fromfile(cls, filename: pathlib.Path):
        filename = filename.resolve()

        assert filename.is_dir(), "Allure report directory is not a directory"

        if filename.parts[-1] == "data":
            raise AssertionError("Please use root allure report directory")

        cls._report_dir = filename.joinpath("data")

        filename = cls._report_dir.joinpath("suites.json")

        assert filename.exists(), "Allure report have no suites.json file"

        file_text = filename.read_bytes()
        text = utils.normalize_xml_text(file_text)
        return cls.fromstring(text=text)

    @classmethod
    def from_root(cls, root: dict):
        instance = super().from_root(root=root)
        return instance

    @property
    def result(self) -> AllureReport:
        return self._target

    def parse(self) -> AllureReport:
        self.read_root()
        self.read_suites()
        return self.result

    def read_root(self):
        self._target.uid = self._source.get("uid", "")
        self._target.name = self._source.get("name", "")
        self._target.children = [
            AllureSuite(**children) for children in self.source["children"]
        ]

    def read_suites(self):
        for suite in self._target.children:
            for testcase in suite.children:
                self.read_testcase(testcase=testcase)

    def read_testcase(self, testcase: AllureTestcase):
        try:
            filename = (
                self._report_dir.joinpath("test-cases")
                .joinpath(testcase.uid)
                .with_suffix(".json")
            )
            file_text = filename.read_bytes()
            text = utils.normalize_xml_text(file_text)
            data = json.loads(text)
        except FileNotFoundError:
            data = {}
        testcase.full_name = data.get("fullName", "")
        testcase.description = data.get("description", "")
        testcase.status_message = data.get("statusMessage", "")
        testcase.status_trace = data.get("statusTrace", "")
        testcase.labels = data.get("labels", [])
        testcase.parameters = data.get("parameters", [])
