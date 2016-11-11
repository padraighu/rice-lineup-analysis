from bs4 import BeautifulSoup
from urllib2 import urlopen
import re
import datetime

def scrape(split_text, lineup, rice_is_home, points_scored=0, points_allowed=0):
    RICE_IS_HOME = rice_is_home
    current_lineup = lineup
    current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0, "o-rebounds allowed": 0,
                     "d-rebounds allowed":0, "fouls drawn":0, "shots against":0, "made shots against":0,
                     "threes against":0, "made threes against": 0,
                     "begin time": datetime.timedelta(0, 0, minutes=20),
                     "end time": datetime.timedelta(0, 0, minutes=20),
                     "lasting time": None, "initial points scored": points_scored, "initial points allowed": points_allowed,
                     "field goal attempt": 0, "field goal made": 0, "three point attempt":0, "three point made":0,
                     "offensive rebound": 0, "defensive rebound": 0, "assist": 0, "block":0,
                     "steal":0, "turnover":0, "foul":0}
    pattern = re.compile(":[^A-Za-z]+")
    score_pattern = re.compile("[0-9]-[0-9]")
    made_pattern = re.compile("GOOD!")
    missed_pattern = re.compile("MISSED")
    rebound_pattern = re.compile("REBOUND")
    assist_pattern = re.compile("ASSIST")
    block_pattern = re.compile("BLOCK")
    steal_pattern = re.compile("STEAL")
    foul_pattern = re.compile("FOUL")
    turnover_pattern = re.compile("TURNOVR")
    time_pattern = re.compile("[0-9]{2}:[0-9]{2}")

    stints = []
    home_score = 0
    away_score = 0
    for line in split_text:
        is_log = re.search(pattern, line)
        if is_log:
            split_line = line.split()
            chopped = False
            for element in split_line:
                is_score = re.search(score_pattern, element)
                is_time = re.search(pattern, element)
                if is_score:
                    current_score = element
                    dash_index = current_score.index("-")
                    home_score = int(current_score[:dash_index])
                    away_score = int(current_score[dash_index + 1:])
                    if RICE_IS_HOME:
                        current_stint["points scored"] = home_score - current_stint["initial points scored"]
                        current_stint["points allowed"] = away_score - current_stint["initial points allowed"]
                    else:
                        current_stint["points allowed"] = home_score - current_stint["initial points allowed"]
                        current_stint["points scored"] = away_score - current_stint["initial points scored"]
                if is_time:
                    game_time_index = split_line.index(element)
                    game_time = element.split(":")
                    game_time = datetime.timedelta(0, int(game_time[1]), minutes=int(game_time[0]))
                    current_stint["end time"] = game_time
                    current_stint["lasting time"] = current_stint["begin time"] - current_stint["end time"]
                    chopped = True   
                    if RICE_IS_HOME:
                        rice_split_line = split_line[:game_time_index] 
                        opp_split_line = split_line[game_time_index + 1:]
                    else:
                        rice_split_line = split_line[game_time_index + 1:]
                        opp_split_line = split_line[:game_time_index] 
                    if len(rice_split_line) != 0 and "SUB" in rice_split_line:
                        if rice_split_line[1] == "IN":
                            player_name = str(rice_split_line[3][:-1])
                            current_lineup.add(player_name)
                        elif rice_split_line[1] == "OUT:":
                            player_name = str(rice_split_line[2][:-1])
                            current_lineup.remove(player_name)
                        if len(current_lineup) == 5:
                            stints.append(current_stint)
                            current_stint = {"lineup": tuple(current_lineup), "points scored": 0, "points allowed": 0, "o-rebounds allowed": 0,
                                            "d-rebounds allowed":0, "fouls drawn":0, "shots against":0, "made shots against":0,
                                            "threes against":0, "made threes against": 0,
                                            "begin time": datetime.timedelta(0, game_time.total_seconds()),
                                            "end time": datetime.timedelta(0, game_time.total_seconds()),
                                            "lasting time": None, "initial points scored": points_scored, "initial points allowed": points_allowed,
                                            "field goal attempt": 0, "field goal made": 0, "three point attempt":0, "three point made":0,
                                            "offensive rebound": 0, "defensive rebound": 0, "assist": 0, "block":0,
                                            "steal":0, "turnover":0, "foul":0}
                            if RICE_IS_HOME:
                                current_stint["initial points scored"] = home_score
                                current_stint["initial points allowed"] = away_score
                            else:
                                current_stint["initial points scored"] = away_score
                                current_stint["initial points allowed"] = home_score
                if RICE_IS_HOME:
                    game_time_txt = filter(lambda x : re.match(time_pattern, x), split_line)
                    if game_time_txt == [] or len(game_time_txt) > 1:
                        break
                    else:
                        game_time_txt = game_time_txt[0]
                    game_time_index = split_line.index(game_time_txt) # find game time
                    rice_split_line = split_line[:game_time_index] 
                    opp_split_line = split_line[game_time_index + 1:]
                    try:
                        missed_shot = re.match(missed_pattern, element) and rice_split_line[rice_split_line.index(element) + 1] != "FT"
                    except:
                        missed_shot = False
                    try:
                        made_shot = re.match(made_pattern, element) and rice_split_line[rice_split_line.index(element) + 1] != "FT"
                    except:
                        missed_shot = False
                    if missed_shot:
                        # We don't want to count free throws.
                        current_stint["field goal attempt"] += 1
                        is_3 = rice_split_line[rice_split_line.index(element) + 1] == "3"
                        if is_3:
                            current_stint["three point attempt"] += 1
                    elif made_shot:
                        current_stint["field goal attempt"] += 1
                        current_stint["field goal made"] += 1
                        is_3 = rice_split_line[rice_split_line.index(element) + 1] == "3"
                        if is_3:
                            current_stint["three point attempt"] += 1
                            current_stint["three point made"] += 1

                    if re.match(rebound_pattern, element):
                        if element in rice_split_line:
                            off_reb = rice_split_line[rice_split_line.index(element) + 1] == "(OFF)" and rice_split_line[rice_split_line.index(element) + 3] != "(DEADBALL)"
                            def_reb = rice_split_line[rice_split_line.index(element) + 1] == "(DEF)" and rice_split_line[rice_split_line.index(element) + 3] != "(DEADBALL)"
                            if off_reb:
                                    current_stint["offensive rebound"] += 1
                            elif def_reb:
                                current_stint["defensive rebound"] += 1
                        elif element in opp_split_line:
                            o_off_reb = opp_split_line[opp_split_line.index(element) + 1] == "(OFF)" and opp_split_line[opp_split_line.index(element) + 3] != "(DEADBALL)"
                            o_def_reb = opp_split_line[opp_split_line.index(element) + 1] == "(DEF)" and opp_split_line[opp_split_line.index(element) + 3] != "(DEADBALL)"
                            if o_off_reb:
                                current_stint["o-rebounds allowed"] += 1
                            elif o_def_reb:
                                current_stint["d-rebounds allowed"] += 1

                    is_assist = re.match(assist_pattern, element)
                    if is_assist and element in rice_split_line:
                        current_stint["assist"] += 1
                    is_block = re.match(block_pattern, element)
                    if is_block:
                        if element in rice_split_line:
                            current_stint["block"] += 1
                        elif element in opp_split_line:
                            pass
                    is_steal = re.match(steal_pattern, element)
                    if is_steal and element in rice_split_line:
                        current_stint["steal"] += 1
                    is_turnover = re.match(turnover_pattern, element)
                    if is_turnover and element in rice_split_line:
                        current_stint["turnover"] += 1
                    is_foul = re.match(foul_pattern, element)
                    if is_foul:
                        if element in rice_split_line:
                            current_stint["foul"] += 1
                        elif element in opp_split_line:
                            current_stint["fouls drawn"] += 1

                elif chopped:
                    missed_shot = re.match(missed_pattern, element)
                    made_shot = re.match(made_pattern, element)

                    if missed_shot and rice_split_line[rice_split_line.index(element) + 1] != "FT":
                        current_stint["field goal attempt"] += 1
                        is_3 = rice_split_line[rice_split_line.index(element) + 1] == "3"
                        if is_3:
                            current_stint["three point attempt"] += 1
                    elif made_shot and rice_split_line[rice_split_line.index(element) + 1] != "FT":
                        current_stint["field goal attempt"] += 1
                        current_stint["field goal made"] += 1 
                        is_3 = rice_split_line[rice_split_line.index(element) + 1] == "3"
                        if is_3:
                            current_stint["three point attempt"] += 1
                            current_stint["three point made"] += 1

                    if re.match(rebound_pattern, element):
                        off_reb = rice_split_line[rice_split_line.index(element) + 1] == "(OFF)" and rice_split_line[rice_split_line.index(element) + 3] != "(DEADBALL)"
                        def_reb = rice_split_line[rice_split_line.index(element) + 1] == "(DEF)" and rice_split_line[rice_split_line.index(element) + 3] != "(DEADBALL)"
                        if off_reb:
                            current_stint["offensive rebound"] += 1
                        elif def_reb:
                            current_stint["defensive rebound"] += 1
                    is_assist = re.match(assist_pattern, element)
                    if is_assist and element in rice_split_line:
                        current_stint["assist"] += 1
                    is_block = re.match(block_pattern, element)
                    if is_block and element in rice_split_line:
                        current_stint["block"] += 1
                    is_steal = re.match(steal_pattern, element)
                    if is_steal and element in rice_split_line:
                        current_stint["steal"] += 1
                    is_turnover = re.match(turnover_pattern, element)
                    if is_turnover and element in rice_split_line:
                        current_stint["turnover"] += 1
                    is_foul = re.match(foul_pattern, element)
                    if is_foul and element in rice_split_line:
                        current_stint["foul"] += 1
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

                    # NF Attempts at new variables by Nick
                    new_stint["three point attempt"] += stint["three point attempt"]
                    new_stint["three point made"] += stint["three point made"]
                    new_stint["assist"] += stint["assist"]
                    new_stint["block"] += stint["block"]
                    new_stint["steal"] += stint["steal"]
                    new_stint["turnover"] += stint["turnover"]
                    new_stint["foul"] += stint["foul"]
                    new_stint["o-rebounds allowed"] += stint["o-rebounds allowed"]
                    new_stint["d-rebounds allowed"] += stint["d-rebounds allowed"]
                    new_stint["fouls drawn"] += stint["fouls drawn"]
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

        # NF Attempts at new variables by Nick
        if stint["field goal attempt"] == 0:
            stint["fgp"] = 0
        else:
            stint["fgp"] = float(stint["field goal made"]) / stint["field goal attempt"]

        if stint["three point attempt"] == 0:
            stint["3pointper"] = 0
        else:
            stint["3pointper"] = float(stint["three point made"]) / stint["three point attempt"]

        if stint["field goal attempt"] == 0:
            stint["efgp"] = 0
        else:
            stint["efgp"] = ((stint["field goal made"] + 0.5) * stint["three point made"]) / float(stint["field goal attempt"])

        if stint["shots against"] == 0:
            stint["fgpAgainst"] = 0
        else:
            stint["fgpAgainst"] = float(stint["made shots against"]) / stint["shots against"]

        if stint["threes against"] == 0:
            stint["3pointperAgainst"] = 0
        else:
            stint["3pointperAgainst"] = float(stint["made threes against"]) / stint["threes against"]

        if stint["shots against"] == 0:
            stint["efgpAgainst"] = 0
        else:
            stint["efgpAgainst"] = ((stint["made shots against"] + 0.5) * stint["made threes against"]) / float(stint["shots against"])


        stint["total rebound against"] = stint["o-rebounds allowed"] + stint["d-rebounds allowed"]
        stint["rebound diff."] = stint["total rebound"] - stint["total rebound against"]

        if (stint["o-rebounds allowed"] + stint["defensive rebound"]) == 0:
            stint["DREB%"] = 0
        else:
            stint["DREB%"] = float(stint["defensive rebound"]) / (stint["o-rebounds allowed"] + stint["defensive rebound"])

        if (stint["d-rebounds allowed"] + stint["offensive rebound"]) == 0:
            stint["OREB%"] = 0
        else:
            stint["OREB%"] = float(stint["offensive rebound"]) / (stint["d-rebounds allowed"] + stint["offensive rebound"])
        del stint["begin time"]
        del stint["end time"]
        del stint["initial points scored"]
        del stint["initial points allowed"]
    return new_stints


def csvify(stints):
    csv_rows = [["Lineup", "Min", "Pts", "Oppo. Pts", "Diff.", "REB Diff.", "FGM", "FGA", "3PM", "3PA", "AST", "D-Reb", "O-Reb","REB", "D-RebA", "O-RebA", "REBA", "FGP", "3P%", "eFG%", "BK", "STL", "TO", "Fouls Against", "Fouls Drawn", "DREB%", "OREB%", "Opp. FG%", "Opp. 3P%", "Opp. eFG%"]]
    for stint in stints:
        csv_row = [stint["lineup"], stint["lasting time"], stint["points scored"], stint["points allowed"],
                   stint["point diff."], stint["rebound diff."],
                   stint["field goal made"], stint["field goal attempt"], stint["three point made"], stint["three point attempt"],
                   stint["assist"], stint["defensive rebound"], stint["offensive rebound"],
                   stint["total rebound"], stint["d-rebounds allowed"], stint["o-rebounds allowed"], stint["total rebound against"], stint["fgp"], stint["3pointper"], stint["efgp"], stint["block"], stint["steal"],
                   stint["turnover"], stint["foul"], stint["fouls drawn"], stint["DREB%"], stint["OREB%"],
                   stint["fgpAgainst"], stint["3pointperAgainst"], stint["efgpAgainst"]]
        csv_rows.append(csv_row)
    for row in csv_rows:
        str_row = ""
        for element in row:
            str_row = str_row + str(element) + ", "
        print(str_row)


def run(url, half_time_points_scored, half_time_points_allowed, rice_is_home, lineup, overtime_points_scored=None):
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

    overtime = False
    ot_pattern = re.compile('OT')
    for text in second_half_text:
        if re.match(ot_pattern, text):
            overtime = True
            ot_index = second_half_text.index(text)
            ot_text = second_half_text[ot_index:]
            ot_text = ot_text[5:]
            second_half_text = second_half_text[:ot_index]

    # Scrape them separately
    raw_stints = scrape(first_half_text, set(lineup), rice_is_home)
    raw_stints.extend(scrape(second_half_text, set(lineup), rice_is_home, half_time_points_scored, half_time_points_allowed))
    if overtime:
        raw_stints.extend(
            scrape(ot_text, set(["Koulechov", "LETCHER-ELLIS", "Guercy", "Cashaw", "Evans"]), rice_is_home,
                   overtime_points_scored, overtime_points_scored))
    clean_stints = format_stints(raw_stints)
    csvify(clean_stints)


if __name__ == "__main__":
    url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice0220.html"
    hps = 52
    hpa = 34
    rice_is_home = True
    overtime = False
    ops = 0
    starting_lineup = set(["Koulechov", "Drone", "Guercy", "Cashaw", "Evans"])
    if not overtime:
        run(url, hps, hpa, rice_is_home, starting_lineup)
    else:
        run(url, hps, hpa, rice_is_home, starting_lineup, ops)

# away & overtime case
    # url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice0225.html"
    # hps = 28
    # hpa = 30
    # rice_is_home = False
    # overtime = True
    # ops = 66
    # starting_lineup = set(["Koulechov", "Drone", "Guercy", "Cashaw", "Evans"])