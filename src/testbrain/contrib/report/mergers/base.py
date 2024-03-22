import abc
import logging
import pathlib
import typing as t

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa


logger = logging.getLogger(__name__)


class ReportMerger(abc.ABC):
    _reports: t.List[str] = []
    _target: t.Any
    _parser: t.Any = None

    @classmethod
    def from_directory(cls, directory: pathlib.Path):
        reports = []
        for file in directory.iterdir():
            if file.is_file():
                if not cls._parser:
                    continue

                try:
                    parser = cls._parser.fromstring(
                        file.read_text(encoding="utf-8"), ignore_errors=False
                    )
                except Exception as exc:
                    logger.error(f"Could not parse: {file} ({exc})", exc_info=False)
                    continue

                parser.parse()
                report = parser.result

                reports.append(report)
        logger.info(f"Merging {len(reports)} files")
        return cls.from_reports(reports=reports)

    @classmethod
    def from_reports(cls, reports: t.List[t.Any]):
        return cls(reports=reports)

    def __init__(self, reports: t.List[t.Any]):
        self._reports = reports

    @abc.abstractmethod
    def merge(self):
        ...

    @property
    def result(self) -> t.Any:
        return self._target

    @property
    def result_json(self) -> str:
        return self._target.model_dump_json(indent=2)

    @property
    def result_xml(self) -> str:
        return self._target.model_dump_xml()
