import codecs
import datetime
import re
import typing as t
from io import BytesIO

from dateutil import parser as datetime_parser

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa


RE_NS = re.compile(r"\{.*\}")


def nested_itemgetter(*path):
    def browse(xs):
        for i in path:
            xs = xs[i]
        return xs

    return browse


def get_namespace(element):
    m = RE_NS.match(element.tag)
    return m.group(0) if m else ""


def string_to_datetime(string: t.Optional[str] = None) -> datetime.datetime:
    if string is None or string == "":
        return datetime.datetime.now()
    return datetime_parser.parse(string)


def datetime_to_string(time: t.Optional[datetime.datetime] = None) -> str:
    if time is None or time == "":
        time = datetime.datetime.now()
    string = time.strftime("%Y-%m-%dT%H:%M:%S.%f")
    return string


def timespan_to_float(timespan: t.Optional[str] = None) -> float:
    if timespan is None or timespan == "":
        return 0.0
    ts = datetime_parser.parse(timespan)
    dt = datetime.timedelta(
        hours=ts.hour,
        minutes=ts.minute,
        seconds=ts.second,
        microseconds=ts.microsecond,
    )
    return dt.total_seconds()


def strip_type_info(name: str):
    idx = name.rfind(".")
    if idx == -1:
        return name
    return name[: idx + 1]


def parse_type_info(name: str) -> str:
    span = name
    parent_index = span.find("(")
    if parent_index == -1:
        span = strip_type_info(span)
    pre_parent = span[:parent_index]
    parent_content = span[parent_index:]
    pre_parent = strip_type_info(pre_parent)
    return pre_parent + parent_content


def normalize_xml_text(text: t.AnyStr) -> bytes:
    if isinstance(text, str):
        text = text.encode("utf-8")

    if text.startswith(codecs.BOM_UTF8):
        text = text.decode("utf-8-sig").encode("utf-8")

    return text


def to_xml(
    tag: str, attrib: t.Optional[t.Dict] = None, text: t.Optional[str] = None
) -> etree.Element:
    if attrib is None:
        attrib = dict()
    elem = etree.Element(tag, attrib=attrib)
    if text:
        elem.text = text
    return elem


def xml_string_to_fileobject(
    xml: t.AnyStr, filename: t.Optional[str] = None
) -> BytesIO:
    xml_content = normalize_xml_text(xml)
    file_obj = BytesIO(xml_content)
    file_obj.name = filename or "merged-report.xml"
    return file_obj
