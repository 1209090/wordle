import csv

def parse_winners(csv_filename):
    winners_list = []
    
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            date = row['date']
            scores = {key: int(value) for key, value in row.items() if key not in ['date', 'nums']}
            max_score = max(scores.values())
            winners = [player for player, score in scores.items() if score == max_score]
            
            winners_list.append({
                'date': date,
                'winners': ', '.join(winners),
                'scores': max_score
            })
    
    return winners_list

# Example usage:
csv_filename = 'stats.csv'
winners = parse_winners(csv_filename)
for entry in winners:
    print(f"{entry['date']}, {entry['winners']}, {entry['scores']}")
