import csv

with open('stats.csv') as file:
	contents = iter(csv.reader(file, delimiter='|'))
	next(contents)

	right_count = 0
	wrong_count = 0

	for row in contents:
		blue_shrooms = row[2]
		blue_bets = row[3]
		red_shrooms = row[4]
		red_bets = row[5]
		winner = row[-1]

		if blue_shrooms >= red_shrooms:
			if winner == 'blue':
				right_count += 1
			else:
				wrong_count += 1
		else:
			if winner == 'red':
				right_count += 1
			else:
				wrong_count += 1

	total_count = right_count + wrong_count
	right_percent = float(right_count) / total_count * 100.0
	wrong_percent = float(wrong_count) / total_count * 100.0

	print("Chat was right %s times out of %s (%s%% of the time)" % (right_count, total_count, round(right_percent, 2)))
	print("Chat was wrong %s times out of %s (%s%% of the time)" % (wrong_count, total_count, round(wrong_percent, 2)))