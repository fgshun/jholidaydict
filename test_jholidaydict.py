import datetime

import pytest

import jholidaydict


def test_holiday2018():
    D = datetime.date
    H = jholidaydict.JHoliday.from_year(2018, 2018).get

    assert H(D(2018, 1, 1)) == '元日'
    assert H(D(2018, 1, 8)) == '成人の日'
    assert H(D(2018, 2, 11)) == '建国記念の日'
    assert H(D(2018, 3, 21)) == '春分の日'
    assert H(D(2018, 4, 29)) == '昭和の日'
    assert H(D(2018, 5, 3)) == '憲法記念日'
    assert H(D(2018, 5, 4)) == 'みどりの日'
    assert H(D(2018, 5, 5)) == 'こどもの日'
    assert H(D(2018, 5, 5)) == 'こどもの日'
    assert H(D(2018, 7, 16)) == '海の日'
    assert H(D(2018, 8, 11)) == '山の日'
    assert H(D(2018, 9, 17)) == '敬老の日'
    assert H(D(2018, 9, 23)) == '秋分の日'
    assert H(D(2018, 10, 8)) == '体育の日'
    assert H(D(2018, 11, 3)) == '文化の日'
    assert H(D(2018, 11, 23)) == '勤労感謝の日'
    assert H(D(2018, 12, 23)) == '天皇誕生日'

    assert H(D(2018, 2, 12)) == '振替休日'
    assert H(D(2018, 4, 30)) == '振替休日'
    assert H(D(2018, 9, 24)) == '振替休日'
    assert H(D(2018, 12, 24)) == '振替休日'

    assert H(D(2017, 1, 1)) is None
    assert H(D(2019, 1, 1)) is None


def test_jholiday_init():
    D = datetime.date

    jholiday0 = jholidaydict.JHoliday(D(2018, 1, 1), D(2018, 1, 8))
    assert jholiday0.get(D(2018, 1, 1)) == '元日'
    assert jholiday0.get(D(2018, 1, 8)) == '成人の日'
    assert len(jholiday0) == 2

    jholiday1 = jholidaydict.JHoliday(D(2018, 1, 2), D(2018, 1, 8))
    assert jholiday1.get(D(2018, 1, 1)) is None
    assert jholiday1.get(D(2018, 1, 8)) == '成人の日'
    assert len(jholiday1) == 1

    jholiday2 = jholidaydict.JHoliday(D(2018, 1, 1), D(2018, 1, 7))
    assert jholiday2.get(D(2018, 1, 1)) == '元日'
    assert jholiday2.get(D(2018, 1, 8)) is None
    assert len(jholiday2) == 1

    jholiday3 = jholidaydict.JHoliday(D(2018, 1, 2), D(2018, 1, 7))
    assert jholiday3.get(D(2018, 1, 1)) is None
    assert jholiday3.get(D(2018, 1, 8)) is None
    assert len(jholiday3) == 0


def test_diff_cjholiday():
    cjholiday = pytest.importorskip('cjholiday')

    jholiday = jholidaydict.JHoliday()
    for date in jholiday.iter_all_dates():
        assert \
            jholiday.get(date) == \
            cjholiday.holiday_name(date=date)
