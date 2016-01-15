from bs4 import BeautifulSoup
from urllib2 import urlopen
import re
import datetime

def get_starting_lineup(player1, player2, player3, player4, player5):
	lineup = set([player1, player2, player3, player4, player5])
	return lineup

def scrape(splited_text):
	#text = str(soup.find_all("span")[1].text)
	RICE_IS_HOME = False
	current_lineup = get_starting_lineup("Koulechov", "Drone", "Guercy", "Mency","Evans")
	print current_lineup
	current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
					"begin time": datetime.timedelta(0, 0, minutes=20), "end time": datetime.timedelta(0, 0, minutes=20),
					"lasting time": None}
	#print current_stint
	pattern = re.compile(":[^A-Za-z]+")
	stints = []
	for line in splited_text:
	 	is_log = re.search(pattern, line)
	 	if is_log:
	 		splited_line = line.split()
	 		#print splited_line
			for element in splited_line:
			 	is_time = re.search(pattern, element)
			 	if is_time:
			 		game_time_index = splited_line.index(element)
			 		game_time = element.split(":")
			 		game_time = datetime.timedelta(0, int(game_time[1]), minutes=int(game_time[0]))
			 		#print game_time
			 		current_stint["end time"] = game_time
			 		current_stint["lasting time"] = current_stint["begin time"] - current_stint["end time"]
			 		if RICE_IS_HOME:
			 			splited_line = splited_line[:game_time_index]
			 		else:
			 			splited_line = splited_line[game_time_index+1:]
			 		if len(splited_line) != 0 and "SUB" in splited_line:
			 			player_name = str(splited_line[-2][:-1])
			 			if splited_line[1] == "IN":
			 				#print player_name, "checking in"
			 				current_lineup.add(player_name)
			 			elif splited_line[1] == "OUT:":
			 				#print player_name, "checking out"
			 				current_lineup.remove(player_name)
			 			if len(current_lineup) == 5:
			 				#print current_stint
			 				current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0,
											"begin time": datetime.timedelta(0, game_time.total_seconds()),
											"end time": datetime.timedelta(0, game_time.total_seconds()),
											"lasting time": None}
							stints.append(current_stint)
			 				# if tuple(current_lineup) in stints:
			 				# 	stints[tuple(current_lineup)]["time"] += game_time
			 				# else:
			 				#  	stints[tuple(current_lineup)] = {"points scored": 0, "points allowed": 0,
								# 								"time": datetime.timedelta(0, 0, 0)}
	return stints
	# total_time = 0
	# for stint in stints:
	# 	total_time += stint["lasting time"].total_seconds()
	# print total_time  		 				

def format_stints(stints):
	new_stints = []
	existing_lineups = []
	for stint in stints:
		if stint["lineup"] in existing_lineups:
			for new_stint in new_stints:
				if new_stint["lineup"] == stint["lineup"]:
					new_stint["points scored"] += stint["points scored"]
					new_stint["points allowed"] += stint["points allowed"]
					new_stint["lasting time"] += stint["lasting time"]
		else:
			new_stints.append(dict(stint))
			existing_lineups.append(tuple(stint["lineup"]))
	total_time = 0
	for stint in new_stints:
		total_time += stint["lasting time"].total_seconds()
		stint["lasting time"] = str(stint["lasting time"])
		del stint["begin time"]
		del stint["end time"]
	print total_time
	return new_stints

def main():
	url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice1113.html"
	soup = BeautifulSoup(urlopen(url), "html.parser")
	# Get first half and second half texts 
	text = soup.find_all("span")[1].text.splitlines()
	count = 0
	for line in text:
		is_divider = re.match("2nd PERIOD", line)
		if is_divider:
			divider_index = text.index(line)
	# need to fix starting lineup problem
	first_half_text = text[:divider_index]
	second_half_text = text[divider_index:]

	# Scrape them separately 
	stint1 = scrape(first_half_text)
	print "hello"
	stint1.extend(scrape(second_half_text))
	stint2 = format_stints(stint1)
	for stint in stint2:
		print stint
					

main()


# 1 Use timedelta instead of time to represent t in game.
# 2 Given a new stint, get its t0 and t1, whose difference will tell us how long did the stint last on the court.
# Instead of having multiple stints with the same lineup, we aggregate the minutes, points, etc. with one single stint, because ultimately that's what we want.