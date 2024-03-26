import codecs
import datetime
import re
import typing as t
from io import BytesIO

import chardet
from dateutil import parser as datetime_parser

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree  # noqa


RE_NS = re.compile(r"\{.*\}")
RE_HIDDEN = re.compile(r"^.*?(?=<\?)", flags=re.DOTALL)


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


def timestamp_to_datetime(timestamp: t.Union[int, float]) -> datetime.datetime:
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    return dt_object


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


def float_to_timespan(seconds: t.Union[int, float]):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return hours, minutes, seconds


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
    if isinstance(text, bytes):
        result = chardet.detect(text)
        encoding = result["encoding"]

        encodings = ["utf-8"]
        decoded_text = None

        if encoding is not None:
            encodings.insert(0, encoding)
            # try:
            #     text = text.decode(encoding)
            # except UnicodeDecodeError:
            #     text = text.decode("utf-8", "ignore")
            # else:
            #     raise Exception("Problem with encoding detection")

        for encoding in encodings:
            try:
                decoded_text = text.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if decoded_text is None:
            raise UnicodeDecodeError(
                "Unable to decode text with any of the specified encodings: {}".format(
                    encodings
                )
            )

        text = decoded_text
    if isinstance(text, str):
        text = RE_HIDDEN.sub("", text)
        text = text.encode("utf-8")
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


def xml_to_string(elem: etree.Element) -> str:
    xml_string = etree.tostring(elem)
    return xml_string.decode("utf-8")


def string_to_fileobject(
    content: t.AnyStr, filename: t.Optional[str] = None
) -> BytesIO:
    content = normalize_xml_text(content)
    file_obj = BytesIO(content)
    file_obj.name = filename or "report.xml"
    return file_obj


def xml_string_to_fileobject(
    xml: t.AnyStr, filename: t.Optional[str] = None
) -> BytesIO:
    return string_to_fileobject(xml, filename=filename)
