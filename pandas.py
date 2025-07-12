import datetime
import math
from io import BytesIO
from types import SimpleNamespace

import csv

NaN = float('nan')


def isna(value):
    return value is None or (isinstance(value, float) and math.isnan(value))


def to_numeric(series, errors='coerce'):
    out = []
    for v in series:
        try:
            if v == '' and errors == 'coerce':
                raise ValueError
            out.append(float(v))
        except Exception:
            if errors == 'coerce':
                out.append(NaN)
            else:
                raise
    return Series(out)


def to_datetime(val, errors='raise'):
    if isinstance(val, datetime.datetime):
        return val
    if isinstance(val, datetime.date):
        return datetime.datetime.combine(val, datetime.time())
    try:
        return datetime.datetime.fromisoformat(str(val))
    except Exception:
        if errors == 'raise':
            raise
        return NaN


class BoolSeries(list):
    def __invert__(self):
        return BoolSeries([not x for x in self])


class Series(list):
    def fillna(self, value):
        return Series([value if isna(x) else x for x in self])

    def apply(self, func):
        return Series([func(x) for x in self])

    @property
    def dt(self):
        series = self

        class _DT:
            def tz_localize(self, tz):
                if tz is None:
                    return Series([
                        x.replace(tzinfo=None) if isinstance(x, datetime.datetime) else x
                        for x in series
                    ])
                raise NotImplementedError

        return _DT()


class Row(dict):
    def __init__(self, mapping, columns):
        super().__init__(mapping)
        self._columns = columns
        self.iloc = [self.get(c) for c in columns]


class BoolDataFrame:
    def __init__(self, data, columns):
        self._data = data
        self._columns = columns

    def all(self, axis=None):
        if axis == 1:
            return BoolSeries([all(row) for row in self._data])
        raise NotImplementedError

    def __invert__(self):
        return BoolDataFrame([[not x for x in row] for row in self._data], self._columns)


class DataFrame:
    def __init__(self, records=None, columns=None):
        records = records or []
        if records and isinstance(records[0], dict):
            if columns is None:
                columns = []
                for r in records:
                    for k in r.keys():
                        if k not in columns:
                            columns.append(k)
            self._columns = list(columns)
            self._records = [
                {c: r.get(c) for c in self._columns}
                for r in records
            ]
        else:
            self._columns = list(columns or [])
            self._records = []

    @staticmethod
    def from_records(records, columns=None):
        return DataFrame(records, columns)

    @property
    def columns(self):
        return self._columns

    def __len__(self):
        return len(self._records)

    def __getitem__(self, key):
        if isinstance(key, list):
            if key and all(isinstance(b, bool) for b in key):
                filtered = [r for r, f in zip(self._records, key) if f]
                return DataFrame(filtered, self._columns)
            new_records = [{c: r.get(c) for c in key} for r in self._records]
            return DataFrame(new_records, key)
        elif isinstance(key, str):
            return Series([r.get(key) for r in self._records])
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if key not in self._columns:
            self._columns.append(key)
            for r in self._records:
                r[key] = None
        if isinstance(value, list):
            for r, v in zip(self._records, value):
                r[key] = v
        else:
            for r in self._records:
                r[key] = value

    def dropna(self, how=None):
        if how == 'all':
            filtered = [r for r in self._records if not all(isna(v) for v in r.values())]
        else:
            filtered = [r for r in self._records if not any(isna(v) for v in r.values())]
        return DataFrame(filtered, self._columns)

    def rename(self, columns=None, inplace=False):
        mapping = columns or {}
        new_columns = [mapping.get(c, c) for c in self._columns]
        new_records = []
        for r in self._records:
            nr = {mapping.get(c, c): r.get(c) for c in self._columns}
            new_records.append(nr)
        if inplace:
            self._columns = new_columns
            self._records = new_records
            return self
        return DataFrame(new_records, new_columns)

    def fillna(self, value):
        new_records = []
        for r in self._records:
            new_records.append({c: (value if isna(r.get(c)) else r.get(c)) for c in self._columns})
        return DataFrame(new_records, self._columns)

    def to_dict(self, orient='records'):
        if orient == 'records':
            return [dict(r) for r in self._records]
        raise NotImplementedError

    def iterrows(self):
        for idx, r in enumerate(self._records):
            yield idx, Row(r, self._columns)

    @property
    def loc(self):
        df = self

        class _Loc:
            def __init__(self, df):
                self.df = df

            def __setitem__(self, key, value):
                rows, col = key
                if isinstance(rows, BoolSeries):
                    for r, flag in zip(self.df._records, rows):
                        if flag:
                            r[col] = value
                else:
                    raise NotImplementedError

            def __getitem__(self, key):
                rows, col = key
                if isinstance(rows, BoolSeries):
                    data = [r[col] for r, flag in zip(self.df._records, rows) if flag]
                    return Series(data)
                raise NotImplementedError

        return _Loc(df)

    def __eq__(self, other):
        data = [[r.get(c) == other for c in self._columns] for r in self._records]
        return BoolDataFrame(data, self._columns)

    def to_excel(self, file, index=False):
        if hasattr(file, 'write'):
            writer = csv.writer(file)
            writer.writerow(self._columns)
            for r in self._records:
                writer.writerow([r.get(c) for c in self._columns])
        else:
            with open(file, 'w', newline='') as fh:
                writer = csv.writer(fh)
                writer.writerow(self._columns)
                for r in self._records:
                    writer.writerow([r.get(c) for c in self._columns])


def read_excel(fp):
    if hasattr(fp, 'read'):
        data = fp.read().decode('utf-8').splitlines()
        reader = csv.reader(data)
    else:
        reader = csv.reader(open(fp, newline=''))
    rows = list(reader)
    if not rows:
        return DataFrame([])
    headers = rows[0]
    records = [dict(zip(headers, row)) for row in rows[1:]]
    return DataFrame(records, headers)


def DataFrame_from_records(records, columns=None):
    return DataFrame(records, columns)

api = SimpleNamespace(types=SimpleNamespace(is_datetime64tz_dtype=lambda s: any(isinstance(v, datetime.datetime) and v.tzinfo for v in s)))

DataFrame.from_records = staticmethod(DataFrame_from_records)

__all__ = ['DataFrame', 'Series', 'read_excel', 'to_numeric', 'to_datetime', 'isna', 'NaN', 'api']
