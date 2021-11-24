# jptime

jptime handle japanese time format.

## Installation

```sh
pip install jptime
```

## Usage

```py
from datetime import datetime
import jptime

# from string
jpt = jptime.from_str("平成元年三月三日")
assert jpt.to_tuple() == (4, 1, 3, 3)
assert jpt.to_datetime() == datetime(1989, 3, 3)

# from datetime
jpt = jptime.from_datetime(datetime(2019, 5, 1))
assert jpt.to_tuple() == (5, 1, 5, 1) # 令和1年5月1日
```

## Supported formats

- japanese era
  - era_symbol/yy/mm/dd (allow kanji number)
    (e.g. 昭和5年3月3日)
  - era_code + yymmdd
    (e.g. 3031123, H040323)
- christian era (delegate to dateutil.parser)
  (e.g. 19920323, 2018-12-12, 2018年8月13日)
