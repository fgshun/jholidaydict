# Python で日本の祝日 dict
日本の祝日を収めたハッシュテーブル (dict) を作る。
「国民の祝日に関する法律」による休日も含む。

法の改正履歴がコードから読み取れるものを目指す。
そのため速度、メモリ効率は度外視。
コード内にどのようにこの法律が変わってきたのか、
それによって各祝日にどのような変化があったのかの説明を入れてある。

```
>>> import datetime

>>> import jholidaydict

>>> jholiday = jholidaydict.JHoliday.from_year(2018, 2020)

>>> holiday_dict = jholiday.make_dict()

>>> holiday_dict.get(datetime.date(2020, 7, 24))
'スポーツの日'

>>> min(holiday_dict.keys())
datetime.date(2018, 1, 1)

>>> max(holiday_dict.keys())
datetime.date(2020, 11, 23)
```

## API
`DATE_00` 「国民の祝日に関する法律」施行日。 `datetime.date(1948, 7, 23)`

`JHoliday.__init__(min_date=DATE_00, max_date=datetime.date(2150, 12, 31)`
min\_date から max\_date までの祝日を算出するための JHoliday インスタンスを作る。

`classmethod JHoliday.from_year(min_year=DATE_00.year, max_year=2150)`
min\_year 年始から max\_year 年末までの祝日を算出するための JHoliday インスタンスを作る。

`JHoliday.make_dict()`
期間内の祝日をまとめた dict をつくる。
