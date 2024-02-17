import abc
import pathlib
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa

from .. import utils


class XMLReportParser(abc.ABC):
    _xml: etree.Element
    _test: t.Any
    _namespace: str = ""

    @property
    def xml(self) -> etree.Element:
        return self._xml

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def result(self) -> t.Any:
        return self._test

    @property
    def result_json(self) -> str:
        return self._test.model_dump_json(indent=2)

    @property
    def result_xml(self) -> str:
        return self._test.model_dump_xml()

    @classmethod
    def fromstring(cls, text: t.AnyStr):
        text = utils.normalize_xml_text(text)
        tree = etree.fromstring(text)
        return cls.from_root(root=tree)

    @classmethod
    def fromfile(cls, filename: pathlib.Path):
        text = utils.normalize_xml_text(filename.read_text(encoding="utf-8"))
        tree = etree.fromstring(text)
        return cls.from_root(root=tree)

    @classmethod
    def from_root(cls, root: etree.Element):
        cls._namespace = utils.get_namespace(root)
        return cls(xml=root)

    def __init__(self, xml):
        self._xml = xml

    @abc.abstractmethod
    def parse(self) -> t.Any:
        ...
