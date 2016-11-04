from bs4 import BeautifulSoup
from urllib2 import urlopen
import re
import datetime


def scrape(splited_text, lineup, rice_is_home, points_scored=0, points_allowed=0):
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
    made_3_pattern = re.compile("GOOD! 3 PTR")
    missed_3_pattern = re.compile("MISSED 3 PTR")
    is_3_pattern = re.compile("3")
    rebound_pattern = re.compile("REBOUND")
    assist_pattern = re.compile("ASSIST")
    block_pattern = re.compile("BLOCK")
    steal_pattern = re.compile("STEAL")
    foul_pattern = re.compile("FOUL")
    turnover_pattern = re.compile("TURNOVR")

    stints = []
    home_score = 0
    away_score = 0
    for line in splited_text:
        is_log = re.search(pattern, line)
        if is_log:
            splited_line = line.split()
            for element in splited_line:
                # print idx, len(splited_line) - 1
                # element = splited_line[idx]
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
                        splited_line = splited_line[game_time_index + 1:]
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

                # Because at this point splited_line is already chopped off.
                # But element is in the orginal splited_line, so it might be a miss or made shot
                # by the opponents, which we don't care.
                # So if element is no longer in splited_line, it means that we don't want to record
                # the miss or made shot.
                if RICE_IS_HOME:
                    try:
                        missed_shot = re.match(missed_pattern, element) and splited_line[
                                                                                splited_line.index(element) + 1] != "FT"
                    except:
                        missed_shot = False
                    try:
                        made_shot = re.match(made_pattern, element) and splited_line[
                                                                            splited_line.index(element) + 1] != "FT"
                    except:
                        missed_shot = False
                    if missed_shot:
                        # We don't want to count free throws.
                        current_stint["field goal attempt"] += 1
                    elif made_shot:
                        current_stint["field goal attempt"] += 1
                        current_stint["field goal made"] += 1

                    # NF Attempt at new variables by Nick
                    try:
                        missed_3_shot = re.match(missed_3_pattern, element) and splited_line[
                                                                                splited_line.index(element) + 1] != "FT"
                    except:
                        missed_3_shot = False
                    try:
                        made_3_shot = re.match(made_3_pattern, element) and splited_line[
                                                                            splited_line.index(element) + 1] != "FT"
                    except:
                        made_3_shot = False
                    if missed_3_shot:
                        # We don't want to count free throws.
                        current_stint["three point attempt"] += 1
                        current_stint["field goal attempt"] += 1
                    elif made_3_shot:
                        current_stint["three point attempt"] += 1
                        current_stint["field goal attempt"] += 1
                        current_stint["three point made"] += 1
                        current_stint["field goal made"] += 1
                    # Same logic.
                    # We don't count deadball rebounds because they are not included in the box score.
                    if re.match(rebound_pattern, element):
                        try:
                            off_reb = splited_line[splited_line.index(element) + 1] == "(OFF)" and splited_line[
                                                                                                       splited_line.index(
                                                                                                           element) + 3] != "(DEADBALL)"
                        except:
                            off_reb = False
                        try:
                            def_reb = splited_line[splited_line.index(element) + 1] == "(DEF)" and splited_line[
                                                                                                       splited_line.index(
                                                                                                           element) + 3] != "(DEADBALL)"
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

                    # NF Attempts at new variables by Nick
                    try:
                        is_block = re.match(block_pattern, element) and element in splited_line
                    except:
                        is_block = False
                    if is_block:
                        current_stint["block"] += 1

                    try:
                        is_steal = re.match(steal_pattern, element) and element in splited_line
                    except:
                        is_steal = False
                    if is_steal:
                        current_stint["steal"] += 1

                    try:
                        is_turnover = re.match(turnover_pattern, element) and element in splited_line
                    except:
                        is_turnover = False
                    if is_turnover:
                        current_stint["turnover"] += 1

                    try:
                        is_foul = re.match(turnover_pattern, element) and element in splited_line
                    except:
                        is_foul = False
                    if is_foul:
                        current_stint["foul"] += 1


                # Away scenario
                elif "chopped" in splited_line:
                    missed_shot = re.match(missed_pattern, element)
                    made_shot = re.match(made_pattern, element)

                    if missed_shot and splited_line[splited_line.index(element) + 1] != "FT":
                        current_stint["field goal attempt"] += 1
                    elif made_shot and splited_line[splited_line.index(element) + 1] != "FT":
                        current_stint["field goal attempt"] += 1
                        current_stint["field goal made"] += 1

                    if re.match(rebound_pattern, element):
                        off_reb = splited_line[splited_line.index(element) + 1] == "(OFF)" and splited_line[
                                                                                                   splited_line.index(
                                                                                                       element) + 3] != "(DEADBALL)"
                        def_reb = splited_line[splited_line.index(element) + 1] == "(DEF)" and splited_line[
                                                                                                   splited_line.index(
                                                                                                       element) + 3] != "(DEADBALL)"
                        if off_reb:
                            current_stint["offensive rebound"] += 1
                        elif def_reb:
                            current_stint["defensive rebound"] += 1

                    # NF Attempts at new variables by Nick
                    #print element
                    missed_3_shot = re.match(missed_3_pattern, element)
                    made_3_shot = re.match(made_3_pattern, element)
                    # print missed_3_shot, made_3_shot
                    if missed_3_shot and splited_line[splited_line.index(element) + 1] != "FT":
                        current_stint["three point attempt"] += 1
                        current_stint["field goal attempt"] += 1
                    elif made_3_shot and splited_line[splited_line.index(element) + 1] != "FT":
                        current_stint["three point attempt"] += 1
                        current_stint["three point made"] += 1
                        current_stint["field goal attempt"] += 1
                        current_stint["field goal made"] += 1

                    # NF Attempts at new variables by Nick
                    is_assist = re.match(assist_pattern, element)
                    if is_assist:
                        current_stint["assist"] += 1
                    is_block = re.match(block_pattern, element)
                    if is_block:
                        current_stint["block"] += 1
                    is_steal = re.match(steal_pattern, element)
                    if is_steal:
                        current_stint["steal"] += 1
                    is_turnover = re.match(turnover_pattern, element)
                    if is_turnover:
                        current_stint["turnover"] += 1
                    is_foul = re.match(foul_pattern, element)
                    if is_foul:
                        current_stint["foul"] += 1


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

                    # NF Attempts at new variables by Nick
                    new_stint["three point attempt"] += stint["three point attempt"]
                    new_stint["three point made"] += stint["three point made"]
                    new_stint["assist"] += stint["assist"]
                    new_stint["block"] += stint["block"]
                    new_stint["steal"] += stint["steal"]
                    new_stint["turnover"] += stint["turnover"]
                    new_stint["foul"] += stint["foul"]
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
        del stint["total rebound against"]

    return new_stints


def csvify(stints):
    csv_rows = [["Lineup", "Min", "Pts", "Oppo. Pts", "Diff.", "REB Diff.", "FGM", "FGA", "AST", "D-Reb", "O-Reb", "REB", "FGP", "3P%", "eFG%", "BK", "STL", "TO", "Fouls Against", "DREB%", "OREB%", "Opp. FG%", "Opp. 3P%", "Opp. eFG%"]]
    for stint in stints:
        csv_row = [stint["lineup"], stint["lasting time"], stint["points scored"], stint["points allowed"],
                   stint["point diff."], stint["rebound diff."],
                   stint["field goal made"], stint["field goal attempt"],
                   stint["assist"], stint["defensive rebound"], stint["offensive rebound"],
                   stint["total rebound"], stint["fgp"], stint["3pointper"], stint["efgp"], stint["block"], stint["steal"],
                   stint["turnover"], stint["foul"], stint["DREB%"], stint["OREB%"],
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
    raw_stints.extend(
        scrape(second_half_text, set(lineup), rice_is_home, half_time_points_scored, half_time_points_allowed))
    if overtime:
        raw_stints.extend(
            scrape(ot_text, set(["Koulechov", "LETCHER-ELLIS", "Guercy", "Cashaw", "Evans"]), rice_is_home,
                   overtime_points_scored, overtime_points_scored))
    clean_stints = format_stints(raw_stints)
    csvify(clean_stints)


if __name__ == "__main__":
    url = "http://www.riceowls.com/sports/m-baskbl/stats/2015-2016/rice0225.html"
    hps = 28
    hpa = 30
    rice_is_home = False
    overtime = True
    ops = 66
    starting_lineup = set(["Koulechov", "Drone", "Guercy", "Cashaw", "Evans"])
    if not overtime:
        run(url, hps, hpa, rice_is_home, starting_lineup)
    else:
        run(url, hps, hpa, rice_is_home, starting_lineup, ops)
