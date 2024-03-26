import abc
import json
import logging
import pathlib
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa

from .. import utils

logger = logging.getLogger(__name__)


class ReportParser(abc.ABC):
    _source: t.Any
    _target: t.Any

    def __init__(self, source):
        self._source = source

    @property
    def source(self) -> t.Any:
        return self._source

    @property
    def target(self) -> t.Any:
        return self._target

    @property
    def result(self) -> t.Any:
        return self._target

    @property
    def result_json(self) -> str:
        return self._target.model_dump_json(indent=2)

    @property
    def result_xml(self) -> str:
        return self._target.model_dump_xml()

    @abc.abstractmethod
    def fromstring(cls, text: t.AnyStr, ignore_errors: t.Optional[bool] = True):
        ...

    @abc.abstractmethod
    def fromfile(cls, filename: pathlib.Path):
        ...

    @abc.abstractmethod
    def parse(self) -> t.Any:
        ...


class JsonReportParser(ReportParser):
    _source: dict

    @classmethod
    def fromstring(cls, text: t.AnyStr, ignore_errors: t.Optional[bool] = True):
        text = utils.normalize_xml_text(text)
        try:
            tree = json.loads(text)
        except Exception as exc:
            logger.error(f"Error parsing with: {exc}", exc_info=False)
            if not ignore_errors:
                raise exc
            text = utils.normalize_xml_text("""{}""")
            tree = json.loads(text)
        return cls.from_root(root=tree)

    @classmethod
    def fromfile(cls, filename: pathlib.Path):
        file_text = filename.read_bytes()
        text = utils.normalize_xml_text(file_text)
        return cls.fromstring(text=text)

    @classmethod
    def from_root(cls, root: dict):
        return cls(source=root)

    @abc.abstractmethod
    def parse(self) -> t.Any:
        ...


class XMLReportParser(ReportParser):
    _source: etree.Element
    _namespace: str = ""

    # _parser = etree.XMLParser(recover=True)
    @property
    def xml(self) -> etree.Element:
        return self._source

    @property
    def namespace(self) -> str:
        return self._namespace

    @classmethod
    def fromstring(cls, text: t.AnyStr, ignore_errors: t.Optional[bool] = True):
        text = utils.normalize_xml_text(text)
        try:
            tree = etree.fromstring(text)
        except Exception as exc:
            logger.error(f"Error parsing with: {exc}", exc_info=False)
            if not ignore_errors:
                raise exc
            text = utils.normalize_xml_text("""<testsuites></testsuites>""")
            tree = etree.fromstring(text)
        return cls.from_root(root=tree)

    @classmethod
    def fromfile(cls, filename: pathlib.Path):
        file_text = filename.read_bytes()
        text = utils.normalize_xml_text(file_text)
        return cls.fromstring(text=text)

    @classmethod
    def from_root(cls, root: etree.Element):
        cls._namespace = utils.get_namespace(root)
        return cls(source=root)

    @abc.abstractmethod
    def parse(self) -> t.Any:
        ...
