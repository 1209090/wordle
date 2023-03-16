import csv
from datetime import datetime, timedelta

START_DATE = datetime.fromisoformat('2022-01-06')
print(START_DATE + timedelta(days=432))

labels = ['L', 'T', 'F', 'S']

def to_int(s):
    return int(s) if s.isdigit() else None

with open('wordle.csv') as csvfile:
    rows = list(csv.DictReader(csvfile))

with open('elo.csv') as elofile:
    elo = list(csv.DictReader(elofile))

def values(row):
    return [to_int(row[name]) for name in labels]
