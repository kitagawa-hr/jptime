import re
import unicodedata
from datetime import datetime
from typing import Pattern, Tuple

from dateutil import parser
import jnc


__version__ = "1.0.0"


class JPTimeError(Exception):
    """Base class for all jptime exceptions."""


class ParseError(JPTimeError):
    """Cannot parse to JPTime"""


class ValidationError(JPTimeError):
    """Invalid date format."""


class JPEra:
    def __init__(self, name: str, code: int, symbol_pattern: Pattern, begin: datetime, end: datetime,) -> None:
        self.name = name
        self.code = code
        self.symbol_pattern = symbol_pattern
        self.begin = begin
        self.end = end


Meiji = JPEra("明治", 1, re.compile(r"明治|M|\u337e"), datetime(1868, 1, 25), datetime(1912, 7, 29))
Taisho = JPEra("大正", 2, re.compile(r"大正|T|\u337d"), datetime(1912, 7, 30), datetime(1926, 12, 24))
Showa = JPEra("昭和", 3, re.compile(r"昭和|S|\u337c"), datetime(1926, 12, 25), datetime(1989, 1, 7))
Heisei = JPEra("平成", 4, re.compile(r"平成|H|\u337b"), datetime(1989, 1, 8), datetime(2019, 4, 30))
Reiwa = JPEra("令和", 5, re.compile(r"令和|R|\u32ff"), datetime(2019, 5, 1), datetime.max)

ALL_ERAS = [
    Meiji,
    Taisho,
    Showa,
    Heisei,
    Reiwa,
]


class JPTime:
    def __init__(self, era_code: int, jp_year: int, month: int, day: int) -> None:
        if era_code <= 0 or era_code > len(ALL_ERAS):
            raise ValidationError(f"{era_code} is out of range.")
        self.era_code = era_code
        self.jp_year = jp_year
        self.month = month
        self.day = day
        try:
            self.jp_era = ALL_ERAS[era_code - 1]
            assert self.to_datetime() <= self.jp_era.end
        except (IndexError, AssertionError):
            raise ValidationError(f"{self} is invalid.")

    def __repr__(self) -> str:
        return "JPTime" + str(self.to_tuple())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JPTime):
            return NotImplemented
        return self.to_tuple() == other.to_tuple()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, JPTime):
            return NotImplemented
        return self.to_tuple() > other.to_tuple()

    def __hash__(self) -> int:
        return hash(self.to_datetime())

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return self.era_code, self.jp_year, self.month, self.day

    def to_datetime(self) -> datetime:
        christian_year = self.jp_year + self.jp_era.begin.year - 1
        return datetime(christian_year, self.month, self.day)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "JPTime":
        return from_datetime(dt)

    @classmethod
    def from_str(cls, s: str) -> "JPTime":
        return from_str(s)


def from_datetime(dt: datetime) -> "JPTime":
    """datetime -> JPTime"""
    for era in ALL_ERAS:
        if era.begin <= dt <= era.end:
            jp_year = dt.year - era.begin.year + 1
            return JPTime(era.code, jp_year, dt.month, dt.day)
    raise ParseError(f"Cannot convert {dt} to jp format.")


def from_str(date: str) -> "JPTime":
    """str -> JPTime

    Supported formats:
        - japanese era
            - era_symbol/yy/mm/dd (allow kanji number)
            - era_code + yymmdd
        - christian era (delegate to dateutil.parser)

    Examples:
        >>> from_str("平成３年３月２３日")
        JPTime(4, 3, 3, 23)
        >>> from_str("平成三年三月二十三日")
        JPTime(4, 3, 3, 23)
        >>> from_str("40323")
        JPTime(4, 3, 3, 23)
        >>> from_str("19910323")
        JPTime(4, 3, 3, 23)
        >>> from_str("1991-3-23")
        JPTime(4, 3, 3, 23)

    """
    normalized_date = unicodedata.normalize("NFKC", date)
    converters = (_from_japanese_era_with_symbol, _from_japanese_era_with_code, _from_christian_era)
    for converter in converters:
        try:
            return converter(normalized_date)
        except JPTimeError:
            continue
    raise ParseError(f"Cannot parse {normalized_date} to JPTime.")


def parse_japanese_number(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        return jnc.ja_to_arabic(s)


def _from_japanese_era_with_symbol(s: str) -> JPTime:
    """symbol + year/month/day format -> JPTime
    e.g. 平成元年三月二十三日, 昭和5年3月23日, S22.9.11
    """
    for era in ALL_ERAS:
        if era.symbol_pattern.match(s):
            try:
                y, m, d = map(
                    parse_japanese_number,
                    re.findall(r"(\d+|[〇一二三四五六七八九十]+)", s.replace("元年", "一年"))
                )
                return JPTime(era.code, y, m, d)
            except ValueError :
                continue
    raise ParseError(f"{s} is invalid format.")


def _from_japanese_era_with_code(s: str) -> JPTime:
    """gyymmdd format -> JPTime"""
    try:
        g, yymmdd = divmod(int(s), 1000000)
        return JPTime(g, *_yymmdd2ymd(yymmdd))
    except (ValueError, IndexError):
        raise ParseError(f"{s} is invalid format.")


def _yymmdd2ymd(yymmdd: int) -> Tuple[int, int, int]:
    """yymmdd -> (year, month, day)

    Examples:
        >>> _yymmdd2ymd(321123)
        (32, 11, 23)
        >>> _yymmdd2ymd(320323)
        (32, 3, 23)
    """
    year, mmdd = divmod(yymmdd, 10000)
    month, day = divmod(mmdd, 100)
    return year, month, day


def _from_christian_era(s: str) -> JPTime:
    """christian era format -> JPTime

    using dateutil.parser
    """

    try:
        dt = parser.parse(s)
        return from_datetime(dt)
    except ValueError:
        raise ParseError(f"Cannot parse {s}.")
