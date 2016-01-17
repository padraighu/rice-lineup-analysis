from bs4 import BeautifulSoup
from urllib2 import urlopen
import re 
import datetime

def scrape(splited_text, points_scored=0, points_allowed=0):
	#text = str(soup.find_all("span")[1].text)
	RICE_IS_HOME = True
	current_lineup = set(["Koulechov", "Drone", "Guercy", "Cashaw","Evans"])
	#print current_lineup
	current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
					"begin time": datetime.timedelta(0, 0, minutes=20), "end time": datetime.timedelta(0, 0, minutes=20),
					"lasting time": None, "initial points scored": points_scored, "initial points allowed": points_allowed}
	#print current_stint
	pattern = re.compile(":[^A-Za-z]+")
	score_pattern = re.compile("[0-9]-[0-9]")
	stints = []
	home_score = 0
	away_score = 0
	for line in splited_text:
		#print line, splited_text.index(line), "of", len(splited_text), splited_text.index(line) == len(splited_text) - 9
	 	is_log = re.search(pattern, line)
	 	if is_log:
	 		splited_line = line.split()
	 		#print splited_line
			for element in splited_line:
				is_score = re.search(score_pattern, element)
			 	is_time = re.search(pattern, element)
			 	if is_score:
			 		current_score = element
			 		dash_index = current_score.index("-")
			 		home_score = int(current_score[:dash_index])
			 		away_score = int(current_score[dash_index+1:])
			 		if RICE_IS_HOME:
			 			current_stint["points scored"] = home_score - current_stint["initial points scored"]
			 			current_stint["points allowed"] = away_score - current_stint["initial points allowed"]
			 		else:
			 			current_stint["points allowed"] = home_score - current_stint["initial points allowed"]
			 			current_stint["points scored"] = away_score - current_stint["initial points scored"]
			 	if is_time:
			 		#print current_stint["lineup"]
			 		game_time_index = splited_line.index(element)
			 		game_time = element.split(":")
			 		game_time = datetime.timedelta(0, int(game_time[1]), minutes=int(game_time[0]))
			 		#print game_time
			 		current_stint["end time"] = game_time
			 		current_stint["lasting time"] = current_stint["begin time"] - current_stint["end time"]
			 		#print current_stint["lasting time"]
			 		if RICE_IS_HOME:
			 			splited_line = splited_line[:game_time_index]
			 		else:
			 			splited_line = splited_line[game_time_index+1:]
			 		if len(splited_line) != 0 and "SUB" in splited_line:
			 			# or splited_text.index(line) == len(splited_text) - 9
			 			player_name = str(splited_line[-2][:-1])
			 			if splited_line[1] == "IN":
			 				#print player_name, "checking in"
			 				current_lineup.add(player_name)
			 			elif splited_line[1] == "OUT:":
			 				#print player_name, "checking out"
			 				current_lineup.remove(player_name)
			 			if len(current_lineup) == 5:
			 				stints.append(current_stint)
			 				current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
											"begin time": datetime.timedelta(0, game_time.total_seconds()),
											"end time": datetime.timedelta(0, game_time.total_seconds()),
											"lasting time": None}
							if RICE_IS_HOME:
								current_stint["initial points scored"] = home_score
								current_stint["initial points allowed"] = away_score
							else:
								current_stint["initial points scored"] = away_score
								current_stint["initial points allowed"] = home_score
							# if tuple(current_lineup) in stints:
			 				# 	stints[tuple(current_lineup)]["time"] += game_time
			 				# else:
			 				#  	stints[tuple(current_lineup)] = {"points scored": 0, "points allowed": 0,
								# 								"time": datetime.timedelta(0, 0, 0)}
	# The last lineup 
	# Because the end time isn't counted until 0:00 usually.
	current_stint["lasting time"] = current_stint["begin time"]
	stints.append(current_stint)
	# for stint in stints:
	# 	print stint["points scored"], stint["points allowed"]
	return stints
	# total_time = 0
	# for stint in stints:
	# 	total_time += stint["lasting time"].total_seconds()
	# print total_time  		 				

def format_stints(stints):
	new_stints = []
	existing_lineups = []
	for stint in stints:
		if set(stint["lineup"]) in existing_lineups:
			for new_stint in new_stints:
		 		if set(new_stint["lineup"]) == set(stint["lineup"]):
		 			new_stint["points scored"] += stint["points scored"]
		 			new_stint["points allowed"] += stint["points allowed"]
		 			new_stint["lasting time"] += stint["lasting time"]
		else:
			new_stints.append(dict(stint))
			existing_lineups.append(set(stint["lineup"]))
	total_time = 0
	for stint in new_stints:
		total_time += stint["lasting time"].total_seconds()
		stint["lasting time"] = str(stint["lasting time"])
		del stint["begin time"]
		del stint["end time"]
	#print datetime.timedelta(seconds=total_time)
	return new_stints

if __name__ == "__main__":
	url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice0114.html"
	soup = BeautifulSoup(urlopen(url), "html.parser")
	# Get first half and second half texts 
	text = soup.find_all("span")[1].text.splitlines()
	count = 0
	for line in text:
		is_divider = re.match("2nd PERIOD", line)
		if is_divider:
			divider_index = text.index(line)
	first_half_text = text[:divider_index]
	second_half_text = text[divider_index:]

	# Scrape them separately 
	stint1 = scrape(first_half_text)
	stint1.extend(scrape(second_half_text, 34, 35))
	stint2 = format_stints(stint1)

	for stint in stint2:
		print stint["lineup"], stint["lasting time"], stint["points scored"], "-", stint["points allowed"]