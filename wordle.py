import csv
from datetime import datetime, timedelta
from collections import defaultdict

START_DATE = datetime.fromisoformat('2022-01-06')
print(START_DATE + timedelta(days=432))

labels = ['L', 'T', 'F', 'S']

def to_int(s):
    return int(s) if s.isdigit() else None

with open('wordle.csv') as csvfile:
    rows = list(csv.DictReader(csvfile))

def to_matches(row):
    day = []
    for x in labels:
        for y in labels:
            if x > y and (xi := to_int(row[x])) is not None and (yi := to_int(row[y])) is not None:
                day.append(({'name': x, 'scores': 7 - xi}, {'name': y, 'scores': 7 - yi}))
    return day

def totals(matches):
    res = defaultdict(lambda: 0)
    for (x, y) in matches:
        if x['scores'] == y['scores']:
            res[x['name']] += 1
            res[y['name']] += 1
        elif x['scores'] > y['scores']:
            res[x['name']] += 3
        else:
            res[y['name']] += 3
    return dict(res)

def date(row):
    return START_DATE + timedelta(days=to_int(row['id']))

def make_day(row):
    res = totals(to_matches(row))
    res['date'] = date(row)
    return res

vals = list(map(make_day, rows))
print(vals)
