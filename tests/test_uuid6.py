import re
import pytest
import typing as t
from time import time_ns
from unittest.mock import patch, Mock
from testbrain.contrib.uuid6 import *

REGEX_UUID6 = re.compile(
    "^[0-9a-f]{8}-[0-9a-f]{4}-6[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
REGEX_UUID7 = re.compile(
    "^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
REGEX_UUID8 = re.compile(
    "^[0-9a-f]{8}-[0-9a-f]{4}-8[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
YEAR_IN_NS = 3600 * 24 * 36525 * 10**7


def test_uuid6_generation():
    uuid6_1 = uuid6()
    assert uuid6_1.version == 6
    for _ in range(1000):
        assert REGEX_UUID6.match(str(uuid6_1))
        uuid6_2 = uuid6()
        assert uuid6_1 < uuid6_2
        uuid6_1 = uuid6_2


def test_uuid7_generation():
    uuid7_1 = uuid7()
    assert uuid7_1.version == 7
    for _ in range(1000):
        assert REGEX_UUID7.match(str(uuid7_1))
        uuid7_2 = uuid7()
        assert uuid7_1 < uuid7_2
        uuid7_1 = uuid7_2


def test_uuid8_generation():
    uuid8_1 = uuid8()
    assert uuid8_1.version == 8
    for _ in range(1000):
        assert REGEX_UUID8.match(str(uuid8_1))
        uuid8_2 = uuid8()
        assert uuid8_1 < uuid8_2
        uuid8_1 = uuid8_2


def test_uuid1_to_uuid6_generation():
    uuid6_1 = None
    for _ in range(1000):
        uuid_1 = uuid1()
        uuid6_2 = uuid1_to_uuid6(uuid_1)
        assert uuid6_2.version == 6
        assert uuid6_2.node == uuid_1.node
        assert uuid6_2.clock_seq == uuid_1.clock_seq
        assert uuid6_2.time == uuid_1.time
        if uuid6_1 is not None:
            assert uuid6_1 < uuid6_2
        uuid6_1 = uuid6_2


def test_invalid_int():
    with pytest.raises(ValueError):
        _ = UUID(int=-1)
    with pytest.raises(ValueError):
        _ = UUID(int=1 << 128)


def test_valid_int():
    test_uuid = UUID(int=0)
    assert test_uuid.version is None
    assert test_uuid.time == 0
    test_uuid = UUID(int=(1 << 128) - 1)
    assert test_uuid.version is None


def test_invalid_version():
    with pytest.raises(ValueError):
        _ = UUID(int=1, version=420)


def test_uuid7_same_nanosecond(monkeypatch):
    monkeypatch.setattr("testbrain.contrib.uuid6._last_v7_timestamp", 1)
    monkeypatch.setattr("time.time_ns", lambda: 1234)
    uuid7_1 = uuid7()
    for _ in range(1000):
        uuid7_2 = uuid7()
        assert uuid7_1 < uuid7_2
        uuid7_1 = uuid7_2


def test_uuid8_same_nanosecond(monkeypatch):
    monkeypatch.setattr("testbrain.contrib.uuid6._last_v8_timestamp", 1)
    monkeypatch.setattr("time.time_ns", lambda: 1234)
    uuid8_1 = uuid8()
    for _ in range(1000):
        uuid8_2 = uuid8()
        assert uuid8_1 < uuid8_2
        uuid8_1 = uuid8_2


def test_uuid6_fields_without_randomness(monkeypatch):
    monkeypatch.setattr("testbrain.contrib.uuid6._last_v6_timestamp", 1)
    monkeypatch.setattr("secrets.randbits", lambda _: 678)
    monkeypatch.setattr("time.time_ns", lambda: 12345)

    uuid6_1 = uuid6(clock_seq=123)
    for _ in range(10):
        uuid6_2 = uuid6(clock_seq=123)
        assert uuid6_1 < uuid6_2
        assert uuid6_1.fields[0] == uuid6_2.fields[0]
        assert uuid6_1.fields[1] == uuid6_2.fields[1]
        assert uuid6_1.fields[2] == uuid6_2.fields[2] - 1
        assert uuid6_1.fields[3] == uuid6_2.fields[3]
        assert uuid6_1.fields[4] == uuid6_2.fields[4]
        assert uuid6_1.fields[5] == uuid6_2.fields[5]

        uuid6_1 = uuid6_2


def test_uuid6_far_in_future(monkeypatch):
    monkeypatch.setattr("testbrain.contrib.uuid6._last_v6_timestamp", 1)
    monkeypatch.setattr("time.time_ns", lambda: 1)
    uuid_prev = uuid6()
    for i in range(1, 3260, 10):
        monkeypatch.setattr("time.time_ns", lambda: i * YEAR_IN_NS)
        uuid_cur = uuid6()
        assert uuid_prev < uuid_cur
        uuid_prev = uuid_cur

    # Overflow
    monkeypatch.setattr("time.time_ns", lambda: 3270 * YEAR_IN_NS)
    uuid_3270y_from_epoch = uuid6()
    assert uuid_3270y_from_epoch < uuid_prev


def test_uuid7_far_in_future(monkeypatch):
    monkeypatch.setattr("testbrain.contrib.uuid6._last_v7_timestamp", 1)
    monkeypatch.setattr("time.time_ns", lambda: 1)
    uuid_prev = uuid7()
    for i in range(1, 8000, 10):
        monkeypatch.setattr("time.time_ns", lambda: i * YEAR_IN_NS)
        uuid_cur = uuid7()
        assert uuid_prev < uuid_cur
        uuid_prev = uuid_cur


def test_uuid8_far_in_future(monkeypatch):
    monkeypatch.setattr("testbrain.contrib.uuid6._last_v8_timestamp", 1)
    monkeypatch.setattr("time.time_ns", lambda: 1)
    uuid_prev = uuid8()
    for i in range(1, 8000, 10):
        monkeypatch.setattr("time.time_ns", lambda: i * YEAR_IN_NS)
        uuid_cur = uuid8()
        assert uuid_prev < uuid_cur
        uuid_prev = uuid_cur


def test_time():
    uuid_1 = uuid1()
    uuid_6 = uuid6()
    assert uuid_6.time / 10**7 == pytest.approx(uuid_1.time / 10**7, 3)
    cur_time = time_ns()
    uuid_7 = uuid7()
    assert uuid_7.time / 10**3 == pytest.approx(cur_time / 10**9, 2)
    uuid_8 = uuid8()
    assert uuid_8.time / 10**9 == pytest.approx(cur_time / 10**9, 3)


def test_zero_time():
    uuid_6 = UUID(hex="00000000-0000-6000-8000-000000000000")
    assert uuid_6.time == 0
    uuid_7 = UUID(hex="00000000-0000-7000-8000-000000000000")
    assert uuid_7.time == 0
    uuid_8 = UUID(hex="00000000-0000-8000-8000-000000000000")
    assert uuid_8.time == 0


def test_max_time():
    uuid_6 = UUID(hex="ffffffff-ffff-6fff-bfff-ffffffffffff")
    assert uuid_6.time == 1152921504606846975
    uuid_7 = UUID(hex="ffffffff-ffff-7fff-bfff-ffffffffffff")
    assert uuid_7.time == 281474976710655
    uuid_8 = UUID(hex="ffffffff-ffff-8fff-bfff-ffffffffffff")
    assert uuid_8.time == 281474976710656000000


def test_multiple_arguments():
    with pytest.raises(TypeError):
        _ = UUID(int=0, hex="061d0edc-bea0-75cc-9892-f6295fd7d295")


def test_convert_invalid_version():
    with pytest.raises(ValueError):
        _ = uuid1_to_uuid6(uuid7())
