import csv
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from itertools import groupby

START_DATE = datetime.fromisoformat('2022-01-06')
NEW_CHAMP_DATE = datetime.fromisoformat('2024-01-01')
NEW_BONUS_DATE = datetime.fromisoformat('2025-05-19')

labels = ['L', 'T', 'F', 'S', 'R', 'B', 'A']

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

def totals(matches, date):
    res = defaultdict(lambda: 0)
    players = set()
    for (x, y) in matches:
        players.add(x['name'])
        players.add(y['name'])
        if x['scores'] == 0 and y['scores'] == 0:
            continue
        if x['scores'] == y['scores']:
            res[x['name']] += 1
            res[y['name']] += 1
        elif x['scores'] > y['scores']:
            res[x['name']] += 3
            if date >= NEW_CHAMP_DATE:
                res[x['name']] += x['scores'] - y['scores'] - 1
        else:
            res[y['name']] += 3
            if date >= NEW_CHAMP_DATE:
                res[y['name']] += y['scores'] - x['scores'] - 1
    res = dict(res)
    if date >= NEW_BONUS_DATE and res:
        maximum = max(res.values())
        winners = [k for k, v in res.items() if v == maximum]
        if len(winners) == 1:
            bonus = max(0, len(players) - 3)
            res[winners[0]] += bonus
    return res

def pretty_print(dic):
    sorted_dict = sorted(dic.items(), key=lambda item: item[1], reverse=True)
    return ", ".join([f"{k} {v}" for k, v in sorted_dict])

def winners():
    res = defaultdict(lambda: 0)
    for row in rows:
        vals = {}
        for x in labels:
            if (xi := to_int(row[x])) is not None:
                vals[x] = xi
        minimum = min(vals.values())
        winners = [k for k, v in vals.items() if v == minimum]
        if len(winners) == 1:
            res[winners[0]] += 1
    print(pretty_print(res))

winners()

def date(row):
    return START_DATE + timedelta(days=to_int(row['id']))

def make_day(row):
    row_date = date(row)
    res = totals(to_matches(row), row_date)
    res['date'] = row_date
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

def abschamps(lines, finished):
    def champs(line):
        maxval = max(line[2:])
        champs = [i for i, x in enumerate(line[2:]) if x == maxval]
        # print(f'{line}: {champs}')
        return champs
    abschamps = []
    for line in lines[2:]:
        abschamps += champs(line)
    if finished:
        abschamps += champs(lines[1])
    abschamps = {labels[x]: abschamps.count(x) for x in set(abschamps)}
    return abschamps

def main():
    vals = list(map(make_day, rows))
    weeks = make_periods(vals)
    current_id = to_int(rows[0]['id'])
    finished = False
    lines = []
    lines.append(['date', 'nums'] + labels)
    for week in weeks:
        line = [week[name] if name in week else 0 for name in labels]
        num = (week['date'] - START_DATE).days
        line.insert(0, week['date'].strftime('%Y-%m-%d'))
        line.insert(1, f"{num}-{num + 6}")
        lines.append(line)
        if current_id == num + 6:
            finished = True

    print(pretty_print(abschamps(lines, finished)))

    with open('stats.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(lines)

if __name__ == "__main__":
    main()
