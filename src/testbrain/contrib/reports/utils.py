import datetime
import typing as t

# from datetime import datetime, timedelta
from dateutil import parser as datetime_parser


def string_to_datetime(string: t.Optional[str] = None) -> datetime.datetime:
    if string is None or string == "":
        return datetime.datetime.now(datetime.UTC)
    return datetime_parser.parse(string)


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
