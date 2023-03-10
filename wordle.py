import csv

with open('wordle.csv') as csvfile:
    rows = list(csv.DictReader(csvfile))
