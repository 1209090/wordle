import csv

with open('wordle.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['word'])
