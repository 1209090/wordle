import csv
from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from itertools import groupby
import elo
import pandas as pd

START_DATE = datetime.fromisoformat('2022-01-06')
NEW_CHAMP_DATE = datetime.fromisoformat('2024-01-01')

labels = ['L', 'T', 'F', 'S', 'R', 'B']

words = pd.read_csv('wordle.csv')
for label in labels:
    words[label + 'scores'] = 7 - pd.to_numeric(words[label], errors='coerce')

elo_ratings = pd.read_csv('elo.csv')

match = elo.EloMatch([elo.Player(n, 1000) for n in labels])

with open('elo.csv') as csvfile:
    ELO = list(csv.DictReader(csvfile))

class Word:
    def __init__(self, id, word, date, guesses, elo):
        self.id = id
        self.word = word
        self.date = date
        self.guesses = guesses
        self.elo = elo

    def __repr__(self):
        return f"Word({self.id}, {self.word}, {self.date}, {self.guesses}, {self.elo})"

    def __str__(self):
        return f"{self.id} {self.word} {self.date} {self.guesses} {self.elo}"

    def to_row(self):
        elo = [f"{n}" for n in self.elo]
        return [str(self.id), self.date.strftime('%Y-%m-%d'), self.word] + self.guesses + elo

    def header(self):
        return ['id', 'date', 'word'] + labels + labels

    @staticmethod
    def create_word(row):
        guesses = [row[name] for name in labels]
        elo = next(filter(lambda erow: erow['слово'] == row['word'], ELO), None)
        if elo is not None:
            elo = list(map(to_int, [elo['L'], elo['T'], elo['F'], elo['S'], elo['R'], elo['B']]))
        return Word(row['id'], row['word'], START_DATE + timedelta(days=to_int(row['id'])), guesses, elo)

def scores(self):
    guesses = self.guesses
    scores = [7 - x if x is not None else None for x in guesses]

def to_int(s):
    return int(s) if s.isdigit() else None

with open('wordle.csv') as csvfile:
    rows = list(csv.DictReader(csvfile))

def mdrow(lst, file=None):
    res = '|'.join(lst)
    res = f'|{res}|'
    if file is not None:
        print(res, file=file)
    return res

with open('README.md', 'w', newline='\n') as f:
    words = [Word.create_word(row) for row in rows]
    mdrow(words[0].header(), f)
    mdrow(['---'] * len(words[0].header()), f)
    for word in words:
        mdrow(word.to_row(), f)

def to_matches(row):
    day = []
    for x in labels:
        for y in labels:
            if x > y and (xi := to_int(row[x])) is not None and (yi := to_int(row[y])) is not None:
                day.append(({'name': x, 'scores': 7 - xi}, {'name': y, 'scores': 7 - yi}))
    return day

def totals(matches, date):
    res = defaultdict(lambda: 0)
    for (x, y) in matches:
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
    return dict(res)

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

def abschamps(lines, finished):
    def champs(line):
        maxval = max(line[2:])
        champs = [i for i, x in enumerate(line[2:]) if x == maxval]
        return champs
    abschamps = []
    for line in lines[2:]:
        abschamps += champs(line)
    if finished:
        abschamps += champs(lines[1])
    abschamps = {labels[x]: abschamps.count(x) for x in set(abschamps)}
    return abschamps

print(f'Week: {abschamps(lines, finished)}')

with open('week-champs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(lines)
