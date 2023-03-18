import csv
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import groupby

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

def squash(days):
    res = dict()
    for d in days:
        for k, v in d.items():
            if k != 'date':
                if k in res:
                    res[k] += v
                else:
                    res[k] = v
    return res

def make_periods(days):
    weeks = []
    for k, g in groupby(days, key=lambda d: d['date'] - timedelta(days=d['date'].weekday())):
        scores = squash(g)
        scores['date'] = k
        weeks.append(scores)
    return weeks

vals = list(map(make_day, rows))
weeks = make_periods(vals)
lines = []
lines.append(['date', 'nums'] + labels)
for week in weeks:
    line = [week[name] if name in week else 0 for name in labels]
    num = (week['date'] - START_DATE).days
    line.insert(0, week['date'].strftime('%Y-%m-%d'))
    line.insert(1, f"{num}-{num + 6}")
    lines.append(line)

abschamps = []
for line in lines:
    maxval = max(line[2:])
    champs = [i for i, x in enumerate(line[2:]) if x == maxval]
    abschamps += champs
abschamps = {x: abschamps.count(x) for x in set(abschamps)}
print(abschamps)
with open('week-champs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(lines)
