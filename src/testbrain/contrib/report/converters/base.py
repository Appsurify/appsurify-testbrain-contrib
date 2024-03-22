import abc
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa

from .. import utils


class ReportConverter(abc.ABC):
    _source: t.Any
    _target: t.Any

    @property
    def result(self) -> t.Any:
        return self._target

    @property
    def result_json(self) -> str:
        return self._target.model_dump_json(indent=2)

    @property
    def result_xml(self) -> str:
        return self._target.model_dump_xml()

    def __init__(self, source: t.Any):
        self._source = source

    @abc.abstractmethod
    def convert(self):
        ...
