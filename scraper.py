from bs4 import BeautifulSoup
from urllib2 import urlopen
import re 
import datetime

def scrape(splited_text, lineup, rice_is_home, points_scored=0, points_allowed=0):
	#text = str(soup.find_all("span")[1].text)
	RICE_IS_HOME = rice_is_home
	current_lineup = lineup
	#print current_lineup
	current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
					"begin time": datetime.timedelta(0, 0, minutes=20), "end time": datetime.timedelta(0, 0, minutes=20),
					"lasting time": None, "initial points scored": points_scored, "initial points allowed": points_allowed,
					"field goal attempt": 0, "field goal made": 0, "offensive rebound": 0, "defensive rebound": 0, "assist": 0}
	#print current_stint
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
			 		if RICE_IS_HOME == True:
			 			splited_line = splited_line[:game_time_index]
			 		else:
			 			splited_line = splited_line[game_time_index+1:]
			 		if len(splited_line) != 0 and "SUB" in splited_line:
			 			# or splited_text.index(line) == len(splited_text) - 9
			 			player_name = str(splited_line[-2][:-1])
			 			if splited_line[1] == "IN":
			 				#print player_name, "checking in"
			 				#print current_lineup
			 				current_lineup.add(player_name)
			 			elif splited_line[1] == "OUT:":
			 				#print player_name, "checking out"
			 				#print current_lineup
			 				current_lineup.remove(player_name)
			 			if len(current_lineup) == 5:
			 				#print current_lineup
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
							# if tuple(current_lineup) in stints:
			 				# 	stints[tuple(current_lineup)]["time"] += game_time
			 				# else:
			 				#  	stints[tuple(current_lineup)] = {"points scored": 0, "points allowed": 0,
								# 								"time": datetime.timedelta(0, 0, 0)}
				# Because at this point splited_line is already chopped off. 
				# But element is in the orginal splited_line, so it might be a miss or made shot 
				# by the opponents, which we don't care.
				# So if element is no longer in splited_line, it means that we don't want to record 
				# the miss or made shot.
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
						#print off_reb
					except:
						off_reb = False
					try:
						def_reb = splited_line[splited_line.index(element)+1] == "(DEF)" and splited_line[splited_line.index(element)+3] != "(DEADBALL)" 
						#print def_reb
					except:
						def_reb = False
					if off_reb:
						#print "hello"
						current_stint["offensive rebound"] += 1
					elif def_reb:
						#print "hi"
						current_stint["defensive rebound"] += 1
				try:
					is_assist = re.match(assist_pattern, element) and element in splited_line
				except:
					is_assist = False
				if is_assist:
					current_stint["assist"] += 1

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
		#total_time += stint["lasting time"].total_seconds()
		stint["lineup"] = format_lineup(stint["lineup"])
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
	# for stint in stint2:
	# 	print stint["lineup"], stint["lasting time"], stint["points scored"], "-", stint["points allowed"], stint["point diff."], "FGM:", stint["field goal made"], "FGA:", stint["field goal attempt"], "REB:", stint["total rebound"], "AST:", stint["assist"]

if __name__ == "__main__":
	url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice1113.html"
	hps = 31
	hpa = 47
	rice_is_home = False
	starting_lineup = set(["Koulechov", "Drone", "Guercy", "Mency", "Evans"])
	run(url, hps, hpa, rice_is_home, starting_lineup)
	