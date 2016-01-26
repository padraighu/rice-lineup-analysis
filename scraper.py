from bs4 import BeautifulSoup
from urllib2 import urlopen
import re 
import datetime

def scrape(splited_text, lineup, rice_is_home, points_scored=0, points_allowed=0):
	RICE_IS_HOME = rice_is_home
	current_lineup = lineup
	current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
					"begin time": datetime.timedelta(0, 0, minutes=20), "end time": datetime.timedelta(0, 0, minutes=20),
					"lasting time": None, "initial points scored": points_scored, "initial points allowed": points_allowed,
					"field goal attempt": 0, "field goal made": 0, "offensive rebound": 0, "defensive rebound": 0, "assist": 0}
	pattern = re.compile(":[^A-Za-z]+")
	score_pattern = re.compile("[0-9]-[0-9]")
	made_pattern = re.compile("GOOD!")
	missed_pattern = re.compile("MISSED")
	rebound_pattern = re.compile("REBOUND")
	assist_pattern = re.compile("ASSIST")
	stints = []
	home_score = 0
	away_score = 0
	for line in splited_text:
	 	is_log = re.search(pattern, line)
	 	if is_log:
	 		splited_line = line.split()
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
			 		game_time_index = splited_line.index(element)
			 		game_time = element.split(":")
			 		game_time = datetime.timedelta(0, int(game_time[1]), minutes=int(game_time[0]))
			 		current_stint["end time"] = game_time
			 		current_stint["lasting time"] = current_stint["begin time"] - current_stint["end time"]
			 		if RICE_IS_HOME:
			 			splited_line = splited_line[:game_time_index]
			 			if "chopped" not in splited_line:
			 				splited_line.append("chopped")
			 		else:
			 			splited_line = splited_line[game_time_index+1:]
			 			if "chopped" not in splited_line:
			 				splited_line.append("chopped")
			 		if len(splited_line) != 0 and "SUB" in splited_line:
			 			player_name = str(splited_line[-3][:-1])
			 			if splited_line[1] == "IN":
			 				current_lineup.add(player_name)
			 			elif splited_line[1] == "OUT:":
			 				current_lineup.remove(player_name)
			 			if len(current_lineup) == 5:
			 				stints.append(current_stint)
			 				current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
											"begin time": datetime.timedelta(0, game_time.total_seconds()),
											"end time": datetime.timedelta(0, game_time.total_seconds()),
											"lasting time": None, "field goal attempt": 0, "field goal made": 0,
											"offensive rebound": 0, "defensive rebound": 0, "assist": 0}
							if RICE_IS_HOME:
								current_stint["initial points scored"] = home_score
								current_stint["initial points allowed"] = away_score
							else:
								current_stint["initial points scored"] = away_score
								current_stint["initial points allowed"] = home_score

				# Because at this point splited_line is already chopped off. 
				# But element is in the orginal splited_line, so it might be a miss or made shot 
				# by the opponents, which we don't care.
				# So if element is no longer in splited_line, it means that we don't want to record 
				# the miss or made shot.
				if RICE_IS_HOME:
					try:
						missed_shot = re.match(missed_pattern, element) and splited_line[splited_line.index(element)+1] != "FT"
					except:
						missed_shot = False
					try:
						made_shot = re.match(made_pattern, element) and splited_line[splited_line.index(element)+1] != "FT"
					except:
						missed_shot = False 
					if missed_shot:
						# We don't want to count free throws.
						current_stint["field goal attempt"] += 1
					elif made_shot:
						current_stint["field goal attempt"] += 1
						current_stint["field goal made"] += 1
					# Same logic.
					# We don't count deadball rebounds because they are not included in the box score.
					if re.match(rebound_pattern, element):
						try:
							off_reb = splited_line[splited_line.index(element)+1] == "(OFF)" and splited_line[splited_line.index(element)+3] != "(DEADBALL)" 
						except:
							off_reb = False
						try:
							def_reb = splited_line[splited_line.index(element)+1] == "(DEF)" and splited_line[splited_line.index(element)+3] != "(DEADBALL)" 
						except:
							def_reb = False
						if off_reb:
							current_stint["offensive rebound"] += 1
						elif def_reb:
							current_stint["defensive rebound"] += 1
					try:
						is_assist = re.match(assist_pattern, element) and element in splited_line
					except:
						is_assist = False
					if is_assist:
						current_stint["assist"] += 1

				# Away scenario
				elif "chopped" in splited_line:
					missed_shot = re.match(missed_pattern, element)
					made_shot = re.match(made_pattern, element)
					if missed_shot and splited_line[splited_line.index(element)+1] != "FT":
						current_stint["field goal attempt"] += 1
					elif made_shot and splited_line[splited_line.index(element)+1] != "FT":
						current_stint["field goal attempt"] += 1
						current_stint["field goal made"] += 1
					if re.match(rebound_pattern, element):
						off_reb = splited_line[splited_line.index(element)+1] == "(OFF)" and splited_line[splited_line.index(element)+3] != "(DEADBALL)" 
						def_reb = splited_line[splited_line.index(element)+1] == "(DEF)" and splited_line[splited_line.index(element)+3] != "(DEADBALL)" 
						if off_reb:
							current_stint["offensive rebound"] += 1
						elif def_reb:
							current_stint["defensive rebound"] += 1
					is_assist = re.match(assist_pattern, element)
					if is_assist:
						current_stint["assist"] += 1

	# The last lineup 
	# Because the end time isn't counted until 0:00 usually.
	current_stint["lasting time"] = current_stint["begin time"]
	stints.append(current_stint)
	return stints

def format_lineup(set_lineup):
	string_lineup = ""
	for player in set_lineup:
		string_lineup = string_lineup + player + " "
	return string_lineup[:-1]

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
		 			new_stint["field goal attempt"] += stint["field goal attempt"]
		 			new_stint["field goal made"] += stint["field goal made"]
		 			new_stint["offensive rebound"] += stint["offensive rebound"]
		 			new_stint["defensive rebound"] += stint["defensive rebound"]
		 			new_stint["assist"] += stint["assist"]
		else:
			new_stints.append(dict(stint))
			existing_lineups.append(set(stint["lineup"]))
	total_time = 0
	for stint in new_stints:
		stint["lineup"] = format_lineup(stint["lineup"])
		total_time += stint["lasting time"].total_seconds()
		stint["lasting time"] = str(stint["lasting time"])[2:]
		stint["total rebound"] = stint["offensive rebound"] + stint["defensive rebound"]
		stint["point diff."] = stint["points scored"] - stint["points allowed"]
		del stint["begin time"]
		del stint["end time"]
		del stint["initial points scored"]
		del stint["initial points allowed"]
		#print datetime.timedelta(seconds=total_time)
	return new_stints

def csvify(stints):
	csv_rows = [["Lineup", "Min", "Pts", "Oppo. Pts", "Diff.", "Fgm", "Fga", "Ast", "D-Reb", "O-Reb", "Reb"]]
	for stint in stints:
		csv_row = [stint["lineup"], stint["lasting time"], stint["points scored"], stint["points allowed"], stint["point diff."],
					stint["field goal made"], stint["field goal attempt"],
					stint["assist"], stint["defensive rebound"], stint["offensive rebound"],
					stint["total rebound"]]
		csv_rows.append(csv_row)
	for row in csv_rows:
		str_row = ""
		for element in row:
			str_row = str_row + str(element) + ", "
		print str_row

def run(url, half_time_points_scored, half_time_points_allowed, rice_is_home, lineup):
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
	raw_stints = scrape(first_half_text, set(lineup), rice_is_home)
	raw_stints.extend(scrape(second_half_text, set(lineup), rice_is_home, half_time_points_scored, half_time_points_allowed))
	clean_stints = format_stints(raw_stints)
	csvify(clean_stints)
	
if __name__ == "__main__":
	url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice0123.html"
	hps = 25
	hpa = 45
	rice_is_home = False
	starting_lineup = set(["Koulechov", "Drone", "Guercy", "Cashaw", "Evans"])
	run(url, hps, hpa, rice_is_home, starting_lineup)
	