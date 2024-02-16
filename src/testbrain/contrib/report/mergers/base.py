import abc
import pathlib
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa

from .. import utils


class ReportMerger(abc.ABC):
    _files: t.List[pathlib.Path] = []
    _reports: t.List[str] = []
    _target: t.Any

    @classmethod
    def from_directory(cls, directory: pathlib.Path):
        instance = cls()
        for file in directory.iterdir():
            if file.is_file():
                instance.files.append(file)
                instance.reports.append(file.read_text(encoding="utf-8"))
        return instance

    @classmethod
    def from_reports(cls, reports: t.List[str]):
        instance = cls()
        instance.reports = reports
        return instance

    def __init__(self, files: t.Optional[t.List[pathlib.Path]] = None):
        if files is None:
            files = []
        self._files = files

    @abc.abstractmethod
    def merge(self):
        ...

    @property
    def files(self):
        return self._files

    @property
    def reports(self):
        return self._reports

    @reports.setter
    def reports(self, value):
        self._reports = value

    @property
    def result(self) -> t.Any:
        return self._target

    @property
    def result_json(self) -> str:
        return self._target.model_dump_json(indent=2)

    @property
    def result_xml(self) -> str:
        result_xml = self._target.model_dump_xml()
        result_str = etree.tostring(result_xml)
        result = result_str.decode("utf-8")
        return result
