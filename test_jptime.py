from datetime import datetime

import pytest

import jptime

# Valid cases
jp_symbol_cases = [
    # normal cases
    ("明治10年3月23日", jptime.JPTime(1, 10, 3, 23)),
    ("大正10年4月2日", jptime.JPTime(2, 10, 4, 2)),
    ("昭和60年9月27日", jptime.JPTime(3, 60, 9, 27)),
    ("平成24年11月2日", jptime.JPTime(4, 24, 11, 2)),
    ("令和1年1月3日", jptime.JPTime(5, 1, 1, 3)),
    # various symbols and delimtiers
    ("昭和45年3月23日", jptime.JPTime(3, 45, 3, 23)),
    ("昭和45年03月23日", jptime.JPTime(3, 45, 3, 23)),
    ("㍼45年03月23日", jptime.JPTime(3, 45, 3, 23)),
    ("S45年03月23日", jptime.JPTime(3, 45, 3, 23)),
    ("S45.3.23", jptime.JPTime(3, 45, 3, 23)),
    # kanji cases
    ("平成三年三月二十三日", jptime.JPTime(4, 3, 3, 23)),
    ("平成元年三月二十三日", jptime.JPTime(4, 1, 3, 23)),
    ("平成元年三月二三日", jptime.JPTime(4, 1, 3, 23)),
    # corner cases
    ("明治1年1月25日", jptime.JPTime(1, 1, 1, 25)),  # Meiji begin day
    ("明治45年7月29日", jptime.JPTime(1, 45, 7, 29)),  # MEiji end day
    ("大正1年7月30日", jptime.JPTime(2, 1, 7, 30)),  # Taisho begin day
    ("大正15年12月24日", jptime.JPTime(2, 15, 12, 24)),  # Taisho end day
    ("昭和1年12月25日", jptime.JPTime(3, 1, 12, 25)),  # Showa begin day
    ("昭和64年1月7日", jptime.JPTime(3, 64, 1, 7)),  # Showa end day
    ("平成1年1月8日", jptime.JPTime(4, 1, 1, 8)),  # Heisei begin day
    ("平成31年4月30日", jptime.JPTime(4, 31, 4, 30)),  # Heisei end day
    ("令和1年5月1日", jptime.JPTime(5, 1, 5, 1)),  # Reiwa begin day
]
jp_code_cases = [
    # normal cases
    ("1100323", jptime.JPTime(1, 10, 3, 23)),
    ("2100402", jptime.JPTime(2, 10, 4, 2)),
    ("3600927", jptime.JPTime(3, 60, 9, 27)),
    ("4241102", jptime.JPTime(4, 24, 11, 2)),
    ("5010103", jptime.JPTime(5, 1, 1, 3)),
    # corner cases
    ("1010125", jptime.JPTime(1, 1, 1, 25)),  # Meiji begin day
    ("1450729", jptime.JPTime(1, 45, 7, 29)),  # MEiji end day
    ("2010730", jptime.JPTime(2, 1, 7, 30)),  # Taisho begin day
    ("2151224", jptime.JPTime(2, 15, 12, 24)),  # Taisho end day
    ("3011225", jptime.JPTime(3, 1, 12, 25)),  # Showa begin day
    ("3640107", jptime.JPTime(3, 64, 1, 7)),  # Showa end day
    ("4010108", jptime.JPTime(4, 1, 1, 8)),  # Heisei begin day
    ("4310430", jptime.JPTime(4, 31, 4, 30)),  # Heisei end day
    ("5010501", jptime.JPTime(5, 1, 5, 1)),  # Reiwa begin day
]
christian_cases = [
    ("1927-9-11", jptime.JPTime(3, 2, 9, 11)),
    ("1930/03/23", jptime.JPTime(3, 5, 3, 23)),
    ("1947.09.11", jptime.JPTime(3, 22, 9, 11)),
    ("1970.3.23", jptime.JPTime(3, 45, 3, 23)),
]
str_and_jptimes = jp_symbol_cases + jp_code_cases + christian_cases

dt_and_jptimes = [
    (datetime(1927, 9, 11), jptime.JPTime(3, 2, 9, 11)),
    (datetime(1930, 3, 23), jptime.JPTime(3, 5, 3, 23)),
    (datetime(1947, 9, 11), jptime.JPTime(3, 22, 9, 11)),
    (datetime(1970, 3, 23), jptime.JPTime(3, 45, 3, 23)),
    (datetime(1991, 3, 23), jptime.JPTime(4, 3, 3, 23)),
]


@pytest.mark.parametrize("s, jpt", jp_symbol_cases)
def test_from_jp_symbol(s, jpt):
    assert jptime._from_japanese_era_with_symbol(s) == jpt


@pytest.mark.parametrize("s, jpt", jp_code_cases)
def test_from_jp_code(s, jpt):
    assert jptime._from_japanese_era_with_code(s) == jpt


@pytest.mark.parametrize("s, jpt", str_and_jptimes)
def test_from_str(s, jpt):
    assert jptime.from_str(s) == jpt


@pytest.mark.parametrize("dt, jpt", dt_and_jptimes)
def test_from_datetime(dt, jpt):
    assert jptime.from_datetime(dt) == jpt


@pytest.mark.parametrize("dt, jpt", dt_and_jptimes)
def test_to_datetime(dt, jpt):
    assert jpt.to_datetime() == dt


# Invalid Cases
jp_symbol_invalid_cases = [
    "明治45年7月30日",  # 1day after Meiji end
    "大正15年12月25日",  # 1day after Taisho end
    "昭和64年1月8日",  # 1day after Showa end
    "平成31年5月1日",  # 1day after Heisei end
    "平成31年13月3日",  # month is out of range
    "平成30年2月29日",  # day is out of range
    "平成31年3月3日10時",  # contain time
    "[平成]1年3月3日",  # symbol is surrounded
]
jp_code_invalid_cases = [
    "0250323",  # era code is out of range
    "6250323",  # era code is out of range
    "1450730",  # 1day after Meiji end
    "2151225",  # 1day after Taisho end
    "3640108",  # 1day after Showa end
    "4310501",  # 1day after Heisei end
    "3311329",  # month is out of range
    "3310230",  # day is out of range
]
dates_cannot_parse = jp_symbol_invalid_cases + jp_code_invalid_cases


@pytest.mark.parametrize("s", jp_symbol_invalid_cases)
def test_from_jp_symbol_raises(s):
    with pytest.raises(jptime.JPTimeError):
        jptime._from_japanese_era_with_symbol(s)


@pytest.mark.parametrize("s", jp_code_invalid_cases)
def test_from_jp_code_raises(s):
    with pytest.raises(jptime.JPTimeError):
        jptime._from_japanese_era_with_code(s)


@pytest.mark.parametrize("s", dates_cannot_parse)
def test_from_str_raises(s):
    with pytest.raises(jptime.ParseError):
        jptime.from_str(s)
