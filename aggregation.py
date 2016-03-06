import csv 
import datetime
from os import chdir, listdir
from scraper import format_lineup

path = 'C:\Users\Patrick Yifei Hu\Desktop\lineup-analysis\lineup analysis game-by-game'
chdir(path)

def convert_csv(file_name):
	stints = []
	count = 0
	with open(file_name, 'rb') as csv_file:
		reader = csv.reader(csv_file)
		for row in reader:
			stint = {}
			if count != 0:
				stint['lineup'] = set(row[0].split())
				minutes = row[1].strip().split(':')
				minutes = datetime.timedelta(0, int(minutes[1]), minutes=int(minutes[0]))
				stint['min'] = minutes
				stint['pts'] = int(row[2].strip())
				stint['opts'] = int(row[3].strip())
				stint['diff'] = int(row[4].strip())
				stint['fgm'] = int(row[5].strip())
				stint['fga'] = int(row[6].strip())
				stint['ast'] = int(row[7].strip())
				stint['dreb'] = int(row[8].strip())
				stint['oreb'] = int(row[9].strip())
				stint['treb'] = int(row[10].strip())
				stints.append(stint)
			else:
				count += 1
		return stints

def aggregate():
	file_names = listdir(path)
	all_stints = []
	aggregated_stints = []
	existing_lineups = []
	for file_name in file_names:
		stints = convert_csv(file_name)
		all_stints.extend(stints)
	for stint in all_stints:
		lineup = stint['lineup']
		if lineup not in existing_lineups:
			existing_lineups.append(lineup)
			aggregated_stints.append(stint)
		else:
			for astint in aggregated_stints:
				if astint['lineup'] == lineup:
					astint['min'] += stint['min']
					astint['pts'] += stint['pts']
					astint['opts'] += stint['opts']
					astint['diff'] += stint['diff']
					astint['fgm'] += stint['fgm']
					astint['fga'] += stint['fga']
					astint['ast'] += stint['ast']
					astint['dreb'] += stint['dreb']
					astint['oreb'] += stint['oreb']
					astint['treb'] += stint['treb']
	for stint in aggregated_stints:
		stint['lineup'] = format_lineup(sorted(list(stint['lineup'])))
		stint['min'] = format_time(str(stint['min']))
	return aggregated_stints

def format_time(time):
	result = 0.0
	time = time.split(':')
	result = float(time[0]) * 60 + float(time[1]) + float(time[2]) / 60
	return round(result, 1)

def csvify(stints):
	csv_rows = [["Lineup", "Min", "Pts", "Oppo. Pts", "Diff.", "Fgm", "Fga", "Ast", "D-Reb", "O-Reb", "Reb"]]
	for stint in stints:
		csv_row = [stint["lineup"], stint["min"], stint["pts"], stint["opts"], stint["diff"],
					stint["fgm"], stint["fga"],
					stint["ast"], stint["dreb"], stint["oreb"],
					stint["treb"]]
		csv_rows.append(csv_row)
	for row in csv_rows:
		str_row = ""
		for element in row:
			str_row = str_row + str(element) + ", "
		print str_row

def normalize(stints, desired_minutes):
	to_remove = []
	for stint in stints:
		minutes = stint['min']
		if minutes != 0:
			ratio = float(desired_minutes) / minutes
			stint['pts'] = round(stint['pts'] * ratio, 1)
			stint['opts'] = round(stint['opts'] * ratio, 1)
			stint['diff'] = round(stint['diff'] * ratio, 1)
			stint['fgm'] = round(stint['fgm'] * ratio, 1)
			stint['fga'] = round(stint['fga'] * ratio, 1)
			stint['ast'] = round(stint['ast'] * ratio, 1)
			stint['dreb'] = round(stint['dreb'] * ratio, 1)
			stint['oreb'] = round(stint['oreb'] * ratio, 1)
			stint['treb'] = round(stint['treb'] * ratio, 1)
		else:
			to_remove.append(stint)
	for element in to_remove:
		stints.remove(element)
	return stints

def run():
	stints = aggregate()
	stints = normalize(stints, 20)
	csvify(stints)