import abc
import typing as t


class ReportConverter(abc.ABC):
    _source: t.Any
    _target: t.Any

    @property
    def result(self):
        return self._target

    @property
    def result_json(self) -> t.AnyStr:
        return self._target.model_dump_json()

    def __init__(self, source: t.Any):
        self._source = source

    @abc.abstractmethod
    def convert(self):
        ...
