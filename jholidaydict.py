"""Python で日本の祝日 dict

日本の祝日を収めたハッシュテーブル (dict) を作る。
「国民の祝日に関する法律」による休日も含む。

法の改正履歴がコードから読み取れるものを目指す。
そのため速度、メモリ効率は度外視。

情報元。ともに 2018-10-08 時点の内容をもとに実装。
e-Gov 法令検索 - 国民の祝日に関する法律
http://elaws.e-gov.go.jp/search/elawsSearch/elaws_search/lsg0500/detail?lawId=323AC1000000178

国立天文台 - 暦計算室 - 暦要項 備考２：国民の祝日の変遷と暦要項
http://eco.mtk.nao.ac.jp/koyomi/yoko/appendix.html#holiday

国立天文台 - 暦計算室 - 国民の祝日と休日
http://eco.mtk.nao.ac.jp/koyomi/topics/html/topics2009_3.html
"""

import collections.abc
import datetime
import functools
import itertools
import operator

# 祝日の変遷

# 「国民の祝日に関する法律」施行日
# 「休日ニ関スル件」(昭和二年勅令第二十五号)と取り替え。
# 新旧で同じ日を指している事実上の改称がいくつか見受けられる。
DATE_00 = datetime.date(1948, 7, 23)

# 第一次改正
# 敬老の日、 体育の日が追加される。
# 建国記念の日も追加されたが日付が決められておらず
# 6 ヶ月以内に定めるとされた。
DATE_01 = datetime.date(1966, 6, 25)

# 「建国記念の日となる日を定める法令」施行日
# 建国記念の日が 02-11 に決まる。
DATE_KE = datetime.date(1966, 12, 9)

# 第二次改正
# 祝日が日曜であったときその翌日が休日となる。
# 俗に振替休日などと呼ばれるもの。
DATE_02 = datetime.date(1973, 4, 12)

# 第三次改正
# 前日および翌日が祝日である日が休日となる。
# 俗に国民の休日などと呼ばれるもの。
# 憲法記念日とこどもの日の間の 05-04 が休日となる。
DATE_03 = datetime.date(1985, 12, 27)

# 第四次改正
# 平成元年。天皇誕生日を 04-29 から 12-23 へ移動。
# とはいえ、 04-29 はみどりの日として祝日のまま残される。
DATE_04 = datetime.date(1989, 2, 17)

# 第五次改正
# 海の日が追加される。
DATE_05 = datetime.date(1996, 1, 1)

# 「国民の祝日に関する法律の一部を改正する法律」施行日
# 通称ハッピーマンデー法。このときから俗に言う移動祝日が現れる。
# まず対象となったのが成人の日(1月第2月曜)と体育の日(10月第2月曜)。
DATE_HM = datetime.date(2000, 1, 1)

# 第六次改正
# 月曜を祝日にする法律ふたつめ。
# 対象は海の日(7月第3月曜)と敬老の日(9月第3月曜)。
# このときまで 05-04 専用であった振替休日の規定が
# 秋分の日が水曜日であったとき敬老の日との間の火曜日で有効になる可能性が生まれた。
# 初回は 2009-09-22 。その後は 2015-09-22, 2026-09-22, 2032-09-23, 2037-09-22 と続く。
# 暦計算室によると、 28 年に 4 回程度の頻度で現れるとのこと。
DATE_06 = datetime.date(2003, 1, 1)

# 第七次改正
# みどりの日を 04-29 から 05-04 へ移動。
# 第四次改正のとき同様 04-29 は昭和の日として祝日のまま残される。
# また、振替休日の移動先が翌日だけでなくその日後の最も近い祝日ではない日になる。
# これにより 05-03 もしくは 05-04 が日曜であった場合も 05-06 に振替休日が現れるようになった。
# 初めて月曜以外に現れたのは 2008-05-06 。火曜日だった。
DATE_07 = datetime.date(2007, 1, 1)

# 第八次改正
# 山の日が追加される。
DATE_08 = datetime.date(2016, 1, 1)

# 「平成三十二年東京オリンピック競技大会・東京パラリンピック競技大会特別措置法」
# 2018-06-20 に施行された法律。
# これにより 2020 年だけ海の日、体育の日、山の日が
# それぞれ 07-23, 07-24, 08-10 に移動される。
DATE_TO = datetime.date(2018, 6, 20)

# ここから 2018-10-09 現在未施行。
# 「天皇の退位等に関する皇室典範特例法」と
# 「天皇の退位などに関する皇室典範特例法の施行期日を定める政令」
# 新元号における元年。天皇誕生日が 12-23 から 02-23 へ移動。
DATE_TT = datetime.date(2019, 5, 1)

# 第九次改正
# 体育の日がスポーツの日に変更される。
DATE_09 = datetime.date(2020, 1, 1)


class JHoliday(collections.abc.Mapping):
    def __init__(self, min_date=DATE_00, max_date=datetime.date(2150, 12, 31)):
        self.min_date = min_date
        self.max_date = max_date
        self._holidays_dict = None

    def __contains__(self, key):
        return key in self._holidays

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (self.min_date, self.max_date) == (other.min_date, other.max_date)

    def __getitem__(self, key):
        return self._holidays[key]

    def __iter__(self):
        return iter(self._holidays)

    def __len__(self):
        return len(self._holidays)

    @property
    def _holidays(self):
        if self._holidays_dict is None:
            holidays = dict(itertools.chain(self.ganjitsu(),
                                            self.seijinnohi(),
                                            self.kenkokukinennohi(),
                                            self.shunbunnohi(),
                                            self.showanohi(),
                                            self.kenpokinenbi(),
                                            self.midorinohi(),
                                            self.kodomonohi(),
                                            self.uminohi(),
                                            self.yamanohi(),
                                            self.keironohi(),
                                            self.shubunnohi(),
                                            self.supotsunohi(),
                                            self.taikunohi(),
                                            self.bunkanohi(),
                                            self.kinrokanshanohi(),
                                            self.tennotanjobi(),
                                            self.special(),
                                            ))
            holidays.update(self.kokuminnokyujitsu(dict(holidays)))
            self._holidays_dict = holidays
        return self._holidays_dict

    @classmethod
    def from_year(cls, min_year=DATE_00.year, max_year=2150):
        min_date = datetime.date(min_year, 1, 1)
        max_date = datetime.date(max_year, 12, 31)
        return cls(min_date, max_date)

    @staticmethod
    def _sorted_dates_filter(it, min_date, max_date):
        if min_date:
            it = itertools.dropwhile(
                functools.partial(operator.gt, min_date), it)
        if max_date:
            it = itertools.takewhile(
                functools.partial(operator.ge, max_date), it)
        return it

    @staticmethod
    def _dates_filter(it, min_date, max_date):
        return filter(lambda date: min_date <= date < max_date, it)

    @staticmethod
    def _holidays_filter(it, min_date, max_date):
        it1, it2 = itertools.tee(it)
        dates = map(operator.itemgetter(0), it1)
        selectors = map(lambda date: min_date <= date <= max_date, dates)
        return itertools.compress(it2, selectors)

    @staticmethod
    def _iter_dates(month, day):
        d = datetime.date(DATE_00.year, month, day)

        while True:
            yield d
            d = d.replace(year=d.year + 1)

    def iter_dates(self, month, day):
        """期間内の特定の月日の date を列挙する"""
        it = self._iter_dates(month, day)
        return self._sorted_dates_filter(it, self.min_date, self.max_date)

    @classmethod
    def _iter_nth_monday(cls, month, n):
        dates = cls._iter_dates(month, 1)

        d1 = datetime.timedelta(days=1)
        d7 = datetime.timedelta(days=7)
        for date in dates:
            weekday = date.weekday()
            date += d7 * (n - 1) + d1 * ((7 - weekday) % 7)
            yield date

    def iter_nth_monday(self, month, n):
        """期間内の特定の第 N 月曜の date を列挙する"""
        it = self._iter_nth_monday(month, n)
        return self._sorted_dates_filter(it, self.min_date, self.max_date)

    def iter_all_dates(self):
        """期間内の date をすべて列挙する"""
        one_day = datetime.timedelta(days=1)

        date = self.min_date
        max_date = self.max_date
        while date <= max_date:
            yield date
            date += one_day

    def ganjitsu(self):
        """元日

        01-01 と定められてから変更なし。
        """
        h = '元日'

        it = self.iter_dates(1, 1)
        it = self._sorted_dates_filter(it, DATE_00, None)
        yield from ((date, h) for date in it)

    def seijinnohi(self):
        """成人の日

        まず 01-15 と定められた。
        2000 年より俗に言うハッピーマンデー法により第2月曜に変更される。
        """
        h = '成人の日'

        it = self.iter_dates(1, 15)
        it = self._sorted_dates_filter(it, DATE_00, DATE_HM)
        yield from ((date, h) for date in it)

        it = self.iter_nth_monday(1, 2)
        it = self._sorted_dates_filter(it, DATE_HM, None)
        yield from ((date, h) for date in it)

    def kenkokukinennohi(self):
        """建国記念の日

        1966-12-09 より 02-11 として追加。 1967 年より現れ始めた。
        """
        h = '建国記念の日'

        it = self.iter_dates(2, 11)
        it = self._sorted_dates_filter(it, DATE_KE, None)
        return ((date, h) for date in it)

    def shunbunnohi(self):
        """春分の日

        春分日と定められてから変更なし。
        """
        h = '春分の日'

        dt2018 = datetime.datetime(2018, 3, 21, 1, 15)
        dt2018 -= datetime.timedelta(minutes=8)  # 1960 年対策
        delta = datetime.timedelta(days=365.242189)

        dt = dt2018
        min_date = max(DATE_00, self.min_date)
        while dt.date() >= min_date:
            if dt.date() < self.max_date:
                yield dt.date(), h
            dt -= delta

        dt2018 += datetime.timedelta(minutes=8 + 4)  # 2088, 2121 年対策
        dt = dt2018 + delta
        while dt.date() < self.max_date:
            if dt.date() >= min_date:
                yield dt.date(), h
            dt += delta

    def showanohi(self):
        """昭和の日

        04-29 はかつてみどりの日だった。
        2007 年にみどりの日は 05-04 へ移動された。
        その際 04-29 を祝日のまま残す形で現れた。
        昭和天皇の誕生日。
        """
        h = '昭和の日'

        it = self.iter_dates(4, 29)
        it = self._sorted_dates_filter(it, DATE_07, None)
        return ((date, h) for date in it)

    def kenpokinenbi(self):
        """憲法記念日

        05-03 と定められてから変更なし。
        """
        h = '憲法記念日'

        it = self.iter_dates(5, 3)
        it = self._sorted_dates_filter(it, DATE_00, None)
        yield from ((date, h) for date in it)

    def midorinohi(self):
        """みどりの日

        04-29 はかつて天皇誕生日だった。昭和天皇の誕生日。
        1989 年に天皇誕生日は 12-23 へ移動された。
        その際 04-29 を祝日のまま残す形で現れた。
        """
        h = 'みどりの日'

        it = self.iter_dates(4, 29)
        it = self._sorted_dates_filter(it, DATE_04, DATE_07)
        yield from ((date, h) for date in it)

        it = self.iter_dates(5, 4)
        it = self._sorted_dates_filter(it, DATE_07, None)
        yield from ((date, h) for date in it)

    def kodomonohi(self):
        """こどもの日

        05-05 と定められてから変更なし。
        """
        h = 'こどもの日'

        it = self.iter_dates(5, 5)
        it = self._sorted_dates_filter(it, DATE_00, None)
        yield from ((date, h) for date in it)

    def uminohi(self):
        """海の日

        1996 年より 07-20 として追加。
        2003 年より 7 月第 3 月曜に変更。
        """
        h = '海の日'

        it = self.iter_dates(7, 20)
        it = self._sorted_dates_filter(it, DATE_05, DATE_06)
        yield from ((date, h) for date in it)

        it = self.iter_nth_monday(7, 3)
        it = self._sorted_dates_filter(it, DATE_06, None)
        yield from ((date, h) for date in it if date.year != 2020)

        d2020 = datetime.date(2020, 7, 23)
        if self.min_date <= d2020 <= self.max_date:
            yield d2020, h

    def yamanohi(self):
        """山の日

        2016 年より 07-20 として追加。
        """
        h = '山の日'

        it = self.iter_dates(8, 11)
        it = self._sorted_dates_filter(it, DATE_08, None)
        yield from ((date, h) for date in it if date.year != 2020)

        d2020 = datetime.date(2020, 8, 10)
        if self.min_date <= d2020 <= self.max_date:
            yield d2020, h

    def keironohi(self):
        """敬老の日

        1966-06-25 より 09-15 として追加。 1966 年より現れ始めた。
        2003 年より 9 月第 3 月曜に変更。
        秋分の日が水曜日であったとき敬老の日との間の火曜日で
        休日が発生する可能性が生まれた。
        """
        h = '敬老の日'

        it = self.iter_dates(9, 15)
        it = self._sorted_dates_filter(it, DATE_01, DATE_06)
        yield from ((date, h) for date in it)

        it = self.iter_nth_monday(9, 3)
        it = self._sorted_dates_filter(it, DATE_06, None)
        yield from ((date, h) for date in it)

    def shubunnohi(self):
        """秋分の日

        秋分日と定められてから変更なし。
        """
        h = '秋分の日'

        dt2018 = datetime.datetime(2018, 9, 23, 10, 54)
        dt2018 -= datetime.timedelta(minutes=2)  # 2012 年対策
        delta = datetime.timedelta(days=365.242189)

        dt = dt2018
        min_date = max(DATE_00, self.min_date)
        if dt.date() < self.max_date:
            while dt.date() >= min_date:
                yield dt.date(), h
                dt -= delta

        dt = dt2018 + delta
        if dt.date() >= min_date:
            while dt.date() < self.max_date:
                yield dt.date(), h
                dt += delta

    def supotsunohi(self):
        """スポーツの日

        10 月 第 2 月曜はかつて体育の日だった。
        2020 年より体育の日と入れ変わる形で現れた。
        """
        h = 'スポーツの日'

        it = self.iter_nth_monday(10, 2)
        it = self._sorted_dates_filter(it, DATE_09, None)
        yield from ((date, h) for date in it if date.year != 2020)

        d2020 = datetime.date(2020, 7, 24)
        if self.min_date <= d2020 <= self.max_date:
            yield d2020, h

    def taikunohi(self):
        """体育の日

        1966-06-25 より 10-10 として追加。 1966 年より現れ始めた。
        2000 年より 10 月第 2 月曜に変更。
        """
        h = '体育の日'

        it = self.iter_dates(10, 10)
        it = self._sorted_dates_filter(it, DATE_01, DATE_HM)
        yield from ((date, h) for date in it)

        it = self.iter_nth_monday(10, 2)
        it = self._sorted_dates_filter(it, DATE_HM, DATE_09)
        yield from ((date, h) for date in it)

    def bunkanohi(self):
        """文化の日

        11-03 と定められてから変更なし。
        """
        h = '文化の日'

        it = self.iter_dates(11, 3)
        it = self._sorted_dates_filter(it, DATE_00, None)
        yield from ((date, h) for date in it)

    def kinrokanshanohi(self):
        """勤労感謝の日

        11-23 と定められてから変更なし。
        """
        h = '勤労感謝の日'

        it = self.iter_dates(11, 23)
        it = self._sorted_dates_filter(it, DATE_00, None)
        yield from ((date, h) for date in it)

    def tennotanjobi(self):
        """天皇誕生日

        昭和天皇誕生日 04-29
        天皇誕生日 12-23
        徳仁親王誕生日 02-23
        """
        h = '天皇誕生日'

        it = self.iter_dates(4, 29)
        it = self._sorted_dates_filter(it, DATE_00, DATE_04)
        yield from ((date, h) for date in it)

        it = self.iter_dates(12, 23)
        it = self._sorted_dates_filter(it, DATE_04, DATE_TT)
        yield from ((date, h) for date in it)

        it = self.iter_dates(2, 23)
        it = self._sorted_dates_filter(it, DATE_TT, None)
        yield from ((date, h) for date in it)

    def _special(self):
        yield datetime.date(1959, 4, 10), '皇太子明仁親王の結婚の儀'
        yield datetime.date(1989, 2, 24), '昭和天皇の大喪の礼'
        yield datetime.date(1990, 11, 12), '即位礼正殿の儀'
        yield datetime.date(1993, 6, 9), '皇太子徳仁親王の結婚の儀'
        yield datetime.date(2019, 5, 1), '即位の日'
        yield datetime.date(2019, 10, 22), '即位礼正殿の儀'

    def special(self):
        """その年限りの休日

        既存の 4 つはいずれも皇室関連の慶長行事に関するもの。
        """
        return self._holidays_filter(
            self._special(), self.min_date, self.max_date)

    def kokuminnokyujitsu(self, holidays):
        """休日

        振替休日、国民の休日は通称であり法律上ではただ「休日」とある。

        1973-04-12 より国民の祝日が日曜であったときその翌日が休日となる。振替休日。
        1985-12-27 より前日と翌日が祝日である国民の祝日でない日が休日となる。国民の休日。
        2007 年より国民の祝日が日曜であったときの移動先が変更、その後の最も近い国民の祝日でない日となった。
        """
        furikae = '振替休日'
        kokuminno = '国民の休日'

        d_1 = datetime.timedelta(days=1)
        d_2 = datetime.timedelta(days=2)

        for date_ in self.iter_all_dates():
            if date_ < DATE_02:
                pass
            elif date_ < DATE_03:
                if date_ in holidays:
                    if date_.weekday() == 6:
                        one = date_ + d_1
                        if one not in holidays and one <= self.max_date:
                            yield one, furikae
            elif date_ < DATE_07:
                if date_ in holidays:
                    if date_.weekday() == 6:
                        one = date_ + d_1
                        if one not in holidays and one <= self.max_date:
                            yield one, furikae
                            continue
                    two = date_ + d_2
                    if two in holidays:
                        one = date_ + d_1
                        if one not in holidays and one.weekday() != 6 and \
                           one <= self.max_date:
                            yield one, kokuminno
            else:
                if date_ in holidays:
                    if date_.weekday() == 6:
                        one = date_ + d_1
                        while one in holidays:
                            one += datetime.timedelta(days=1)
                        if one <= self.max_date:
                            yield one, furikae
                            continue
                    two = date_ + d_2
                    if two in holidays:
                        one = date_ + d_1
                        if one not in holidays and one.weekday() != 6 and \
                           one <= self.max_date:
                            yield one, kokuminno
