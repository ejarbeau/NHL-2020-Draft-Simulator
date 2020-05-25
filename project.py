import urllib.request
import json
import random
import operator
import csv


def getnhldata():
    nhldata = urllib.request.urlopen("https://statsapi.web.nhl.com/api/v1/standings/byLeague")
    formatted_data = json.load(nhldata)
    records = formatted_data['records'][0]['teamRecords']
    return records


def nhl_draft_odds():
    lottery_odds = open('lottery_odds.txt')
    draft_odds = lottery_odds.readlines()
    lottery_odds.close()
    return draft_odds


def team_finder(records, current_rank):
    return str(records[current_rank]['team']['name'])


def all_teams(records):
    current_rank = 30
    all_team = []
    for i in range(31):
        all_team.append(team_finder(records, current_rank))
        current_rank -= 1
    all_team.sort()
    return all_team


def is_lottery_team(records, current_rank):
    team = team_finder(records,current_rank)
    #exceptions for points percentages need to be made here
    if team == 'Columbus Blue Jackets':
        return True
    if team == 'New York Islanders':
        return False
    if team == 'Vancouver Canucks':
        return False
    if team == 'Winnipeg Jets':
        return True
    wildcard_ranking = int(records[current_rank]['wildCardRank'])
    return wildcard_ranking > 2


def points_percentage_calculator(records, current_rank):
    points = int(records[current_rank]['points'])
    games_played = int(records[current_rank]['gamesPlayed'])
    return points / (games_played * 2)


def team_points_percentage(records):
    point_percentage_list = {}
    for i in range(31):
        name = team_finder(records, i)
        points_percentage = points_percentage_calculator(records, i)
        league_rank = int(records[i]['leagueRank'])
        point_percentage_list[name] = [points_percentage, league_rank]
    point_percentage_sorted = dict(sorted(point_percentage_list.items(), key=operator.itemgetter(1)))
    return point_percentage_sorted


def name_to_rank(name, records):
    for current_rank in range(31):
        if name == str(records[current_rank]['team']['name']):
            return current_rank


def new_create_lottery_standings(records, draft_odds, points_percentage_sorted):
    current_pick = 0
    lottery_standings = {}
    pre_team_odds = 0
    post_team_odds = 0
    for team in points_percentage_sorted:
        current_rank = int(points_percentage_sorted[team][1]) - 1
        if is_lottery_team(records, current_rank):
            name = team_finder(records, current_rank)
            odds = float(draft_odds[current_pick])
            post_team_odds += odds
            current_team = [name, pre_team_odds, post_team_odds]
            lottery_standings[30 - current_pick] = current_team
            pre_team_odds = post_team_odds
            current_pick += 1
    for team in points_percentage_sorted:
        current_rank = int(points_percentage_sorted[team][1]) - 1
        if not is_lottery_team(records, current_rank):
            name = team_finder(records, current_rank)
            odds = float(draft_odds[current_pick])
            post_team_odds += odds
            current_team = [name, pre_team_odds, post_team_odds]
            lottery_standings[30 - current_pick] = current_team
            pre_team_odds = post_team_odds
            current_pick += 1
    return lottery_standings


def lottery_machine():
    return round(random.uniform(0.0, 99.9), 1)


def did_we_win(lottery_standings, selection, current_rank):
    return lottery_standings[current_rank][1] < selection <= lottery_standings[current_rank][2]


def nhl_lottery(lottery_standings, records):
    lottery_winners = []
    while len(lottery_winners) < 3:
        selection = lottery_machine()
        current_rank = 30
        for j in range(31):
            while did_we_win(lottery_standings, selection, current_rank) and been_chosen(records, lottery_winners,
                                                                                         current_rank):
                selection = lottery_machine()
            if did_we_win(lottery_standings, selection, current_rank) and not been_chosen(records, lottery_winners,
                                                                                          current_rank):
                lottery_winners.append(team_finder(records, current_rank))
            current_rank -= 1
    return lottery_winners


def been_chosen(records, lottery_winners, i):
    for team in lottery_winners:
        if team_finder(records, i) in lottery_winners:
            return True
    return False


def draft_order_generator(lottery_winners, lottery_standings):
    draft_order = []
    current_rank = 30
    for i in range(3):
        on_the_clock = lottery_winners[i]
        draft_order.append(on_the_clock)
    for i in range(31):
        if lottery_standings[current_rank][0] in lottery_winners:
            pass
        else:
            on_the_clock = lottery_standings[current_rank][0]
            draft_order.append(on_the_clock)
        current_rank -= 1
    return draft_order


def draft_pick_trades(draft_order,total_rounds):
    for pick in range(len(draft_order)):
        if pick < 31: #first round
            if draft_order[pick] == 'Toronto Maple Leafs':
                leafs_pick = int(pick)
            if draft_order[pick] == 'Carolina Hurricanes':
                canes_pick = int(pick)
            if draft_order[pick] == 'San Jose Sharks':
                draft_order[pick] = 'Ottawa Senators (from San Jose Sharks)'
            if draft_order[pick] == 'New York Islanders' and not pick < 4:
                draft_order[pick] = 'Ottawa Senators (from New York Islanders)'
            if draft_order[pick] == 'Vancouver Canucks' and not pick < 16:
                draft_order[pick] = 'New Jersey Devils (from Vancouver Canucks via Tampa Bay Lightning)'
            if draft_order[pick] == 'Arizona Coyotes' and not pick < 4:
                draft_order[pick] = 'New Jersey Devils (from Arizona Coyotes)'
            if draft_order[pick] == 'Pittsburgh Penguins' and not pick < 16:
                draft_order[pick] = 'Minnesota Wild (from Pittsburgh Penguins)'
            if draft_order[pick] == 'Boston Bruins':
                draft_order[pick] = 'Anaheim Ducks (from Boston Bruins)'
            if draft_order[pick] == 'Tampa Bay Lightning':
                draft_order[pick] = 'San Jose Sharks (from Tampa Bay Lightning)'
        if 31 <= pick < 62: #second round
            if draft_order[pick] == 'New Jersey Devils':
                draft_order[pick] = 'Nashville Predators (from New Jersey Devils)'
            if draft_order[pick] == 'Chicago Blackhawks':
                draft_order[pick] = 'Montreal Canadiens (from Chicago Blackhawks)'
            if draft_order[pick] == 'New York Rangers':
                draft_order[pick] = 'Carolina Hurricanes (from New York Rangers)'
            if draft_order[pick] == 'Columbus Blue Jackets':
                draft_order[pick] = 'Ottawa Senators (from Columbus Blue Jackets)'
            if draft_order[pick] == 'Vancouver Canucks':
                draft_order[pick] = 'Los Angeles Kings (from Vancouver Canucks)'
            if draft_order[pick] == 'Edmonton Oilers':
                draft_order[pick] = 'Detroit Red Wings (from Edmonton Oilers)'
            if draft_order[pick] == 'Pittsburgh Penguins':
                draft_order[pick] = 'Chicago Blackhawks (from Pittsburgh Penguins via Vegas Golden Knights)'
            if draft_order[pick] == 'Dallas Stars':
                draft_order[pick] = 'Ottawa Senators (from Dallas Stars via Vegas Golden Knights)'
            if draft_order[pick] == 'Colorado Avalanche':
                draft_order[pick] = 'San Jose Sharks (from Colorado Avalanche via Washington Capitals)'
            if draft_order[pick] == 'Vegas Golden Knights':
                draft_order[pick] = 'Los Angeles Kings (from Vegas Golden Knights)'
            if draft_order[pick] == 'Washington Capitals':
                draft_order[pick] = 'Detroit Red Wings (from Washington Capitals)'
            if draft_order[pick] == 'St. Louis Blues':
                draft_order[pick] = 'Montreal Canadiens (from St. Louis Blues)'
        if 62 <= pick < 93: #third round
            if draft_order[pick] == 'San Jose Sharks':
                draft_order[pick] = 'Detroit Red Wings (from San Jose Sharks)'
            if draft_order[pick] == 'New Jersey Devils':
                draft_order[pick] = 'Vegas Golden Knights (from New Jersey Devils)'
            if draft_order[pick] == 'Buffalo Sabres':
                draft_order[pick] = 'Carolina Hurricanes (from Buffalo Sabres)'
            if draft_order[pick] == 'Arizona Coyotes':
                draft_order[pick] = 'Washington Capitals (from Arizona Coyotes via Colorado Avalanche)'
            if draft_order[pick] == 'Minnesota Wild':
                draft_order[pick] = 'Nashville Predators (from Minnesota Wild)'
            if draft_order[pick] == 'Winnipeg Jets':
                draft_order[pick] = 'Ottawa Senators (from Winnipeg Jets)'
            if draft_order[pick] == 'Calgary Flames':
                draft_order[pick] = 'Chicago Blackhawks (from Calgary Flames)'
            if draft_order[pick] == 'Columbus Blue Jackets':
                draft_order[pick] = 'Los Angeles Kings (from Columbus Blue Jackets via Ottawa Senators and Toronto Maple Leafs)'
            if draft_order[pick] == 'Toronto Maple Leafs':
                draft_order[pick] = 'Colorado Avalanche (from Toronto Maple Leafs)'
            if draft_order[pick] == 'Dallas Stars':
                draft_order[pick] = 'New York Rangers (from Dallas Stars)'
            if draft_order[pick] == 'Philadelphia Flyers':
                draft_order[pick] = 'Tampa Lightning (from Philadelphia Flyers via San Jose Sharks)'
            if draft_order[pick] == 'Colorado Avalanche':
                draft_order[pick] = 'Florida Panthers (from Colorado Avalanche)'
            if draft_order[pick] == 'Washington Capitals':
                draft_order[pick] = 'Montreal Canadiens (from Washington Capitals)'
        if 93 <= pick < 124: #fourth round
            if draft_order[pick] == 'Detroit Red Wings':
                draft_order[pick] = 'Tampa Bay Lightning (from Detroit Red Wings)'
            if draft_order[pick] == 'San Jose Sharks':
                draft_order[pick] = 'Montreal Canadiens (from San Jose Sharks)'
            if draft_order[pick] == 'Anaheim Ducks':
                draft_order[pick] = 'Montreal Canadiens (from Anaheim Ducks)'
            if draft_order[pick] == 'Buffalo Sabres':
                draft_order[pick] = 'Calgary Flames (from Buffalo Sabres)'
            if draft_order[pick] == 'Winnipeg Jets':
                draft_order[pick] = 'Montreal Canadiens (from Winnipeg Jets)'
            if draft_order[pick] == 'Calgary Flames':
                draft_order[pick] = 'Los Angeles (from Calgary Flames)'
            if draft_order[pick] == 'Nashville Predators':
                preds_fourth = int(pick)
            if draft_order[pick] == 'Edmonton Oilers':
                draft_order[pick] = 'Detroit Red Wings (from Edmonton Oilers)'
            if draft_order[pick] == 'Vegas Golden Knights':
                draft_order[pick] = 'Toronto Maple Leafs (from Vegas Golden Knights)'
            if draft_order[pick] == 'Philadelphia Flyers':
                flyers_fourth = int(pick)
            if draft_order[pick] == 'Boston Bruins':
                draft_order[pick] = 'New Jersey Devils (from Boston Bruins)'
        if 124 <= pick < 155: #fifth round
            if draft_order[pick] == 'Ottawa Senators':
                draft_order[pick] = 'San Jose Sharks (from Ottawa Senators)'
            if draft_order[pick] == 'Florida Panthers':
                draft_order[pick] = 'Montreal Canadiens (from Florida Panthers)'
            if draft_order[pick] == 'Toronto Maple Leafs':
                draft_order[pick] = 'Florida Panthers (from Toronto Maple Leafs)'
            if draft_order[pick] == 'Carolina Hurricanes':
                draft_order[pick] = 'St. Louis Blues (from Carolina Hurricanes)'
            if draft_order[pick] == 'Tampa Bay Lightning':
                draft_order[pick] = 'Ottawa Senators (from Tampa Bay Lightning)'
            if draft_order[pick] == 'Vegas Golden Knights':
                draft_order[pick] = 'Toronto Maple Leafs (from Vegas Golden Knights)'
        if 155 <= pick < 186: #sixth round
            if draft_order[pick] == 'Ottawa Senators':
                draft_order[pick] = 'Tampa Bay Lightning (from Ottawa Senators)'
            if draft_order[pick] == 'San Jose Sharks':
                draft_order[pick] = 'Ottawa Senators (from San Jose Sharks)'
            if draft_order[pick] == 'Buffalo Sabres':
                draft_order[pick] = 'Dallas Starts (from Buffalo Sabres via Carolina Hurricanes and Florida Panthers)'
            if draft_order[pick] == 'Carolina Hurricanes':
                draft_order[pick] = 'Toronto Maple Leafs (from Carolina Hurricanes)'
            if draft_order[pick] == 'Colorado Avalanche':
                draft_order[pick] = 'Toronto Maple Leafs (from Colorado Avalanche)'
            if draft_order[pick] == 'St. Louis Blues':
                draft_order[pick] = 'Ottawa Senators (from St. Louis Blues via Edmonton Oilers)'
        if 186 <= pick: #seventh round
            if draft_order[pick] == 'Ottawa Senators':
                draft_order[pick] = 'Montreal Canadiens (from Ottawa Senators)'
            if draft_order[pick] == 'San Jose Sharks':
                draft_order[pick] = 'Toronto Maple Leafs (from San Jose Sharks)'
            if draft_order[pick] == 'Anaheim Ducks':
                draft_order[pick] = 'Vancouver Canucks (from Anaheim Ducks)'
            if draft_order[pick] == 'Montreal Canadiens':
                draft_order[pick] = 'Philadelphia Flyers (from Montreal Canadiens)'
            if draft_order[pick] == 'Chicago Blackhawks':
                draft_order[pick] = 'Montreal Canadiens (from Chicago Blackhawks)'
            if draft_order[pick] == 'Winnipeg Jets':
                draft_order[pick] = 'Toronto Maple Leafs (from Winnipeg Jets via Minnesota Wild)'
            if draft_order[pick] == 'Vancouver Canucks':
                draft_order[pick] = 'New York Rangers (from Vancouver Canucks)'
            if draft_order[pick] == 'Nashville Predators':
                draft_order[pick] = 'New York Rangers (from Nashville Predators)'
            if draft_order[pick] == 'Toronto Maple Leafs':
                draft_order[pick] = 'Carolina Hurricanes (from Toronto Maple Leafs)'
            if draft_order[pick] == 'Dallas Stars':
                draft_order[pick] = 'Buffalo Sabres (from Dallas Stars)'
            if draft_order[pick] == 'Pittsburgh Penguins':
                draft_order[pick] = 'San Jose Sharks (from Pittsburgh Penguins)'
            if draft_order[pick] == 'Washington Capitals':
                draft_order[pick] = 'San Jose Sharks (from Washington Capitals)'
            if draft_order[pick] == 'St. Louis Blues':
                draft_order[pick] = 'Toronto Maple Leafs (from St. Louis Blues)'
    if total_rounds >= 4:
        if preds_fourth < flyers_fourth:
            draft_order[preds_fourth] = 'Anaheim Ducks (from Nashville Predators via Philadelphia Flyers)'
        else:
            draft_order[preds_fourth] = 'Philadelphia Flyers (from Nashville Predators)'
            draft_order[flyers_fourth] = 'Anaheim Ducks (from Philadelphia Flyers)'
    if leafs_pick < 11:
        draft_order[canes_pick] = 'New York Rangers (from Carolina Hurricanes)'
    elif leafs_pick < canes_pick:
        draft_order[leafs_pick] = 'Carolina Hurricanes (from Toronto Maple Leafs)'
        draft_order[canes_pick] = 'New York Rangers (from Carolina Hurricanes)'
    elif leafs_pick > canes_pick:
        draft_order[canes_pick] = 'New York Rangers (from Toronto Maple Leafs)'
    return draft_order


def rounds_calculator():
    total_rounds = 0
    while total_rounds < 1 or total_rounds > 7:
        try:
            total_rounds = int(input('How many total rounds? (1-7): '))
        except ValueError:
            print('Input an integer between 1 and 7')
    return total_rounds


def should_print_draft_results():
    yes_no = 'a'
    while yes_no != 'yes' and yes_no != 'no':
        yes_no = str(input('Print draft results? (yes or no): '))
    return yes_no == 'yes'


def should_print_draft_class():
    yes_no = 'a'
    while yes_no != 'yes' and yes_no != 'no':
        yes_no = str(input('Print each team\'s draft class? (yes or no): '))
    return yes_no == 'yes'


def should_print_first_round_order():
    yes_no = 'a'
    while yes_no != 'yes' and yes_no != 'no':
        yes_no = str(input('Print the draft order for the first round? (yes or no): '))
    return yes_no == 'yes'


def main():
    records = getnhldata()
    draft_odds = nhl_draft_odds()
    all_teams_list = all_teams(records)
    points_percentage_sorted = team_points_percentage(records)
    lottery_standings = new_create_lottery_standings(records, draft_odds, points_percentage_sorted)
    total_rounds = rounds_calculator()
    lottery_winners = nhl_lottery(lottery_standings, records)
    first_rnd_draft_order = draft_order_generator(lottery_winners, lottery_standings)
    day2_order = day2_draft_order(lottery_standings, total_rounds)
    total_order = total_draft_order(first_rnd_draft_order, day2_order)
    total_order = draft_pick_trades(total_order, total_rounds)
    if should_print_first_round_order():
        print('After the NHL Draft Lottery, the draft order for the first round is: ')
        for pick in range(31):
            print(str(pick + 1) + ': ' + total_order[pick])
    print('')
    prospects = import_prospects()
    print('')
    draft_type = simulated_or_user_draft()
    if draft_type == 's':
        draft_results = simulated_draft(prospects, total_order, total_rounds)
    if draft_type == 'u':
        draft_results = user_draft(prospects, total_order, total_rounds)
    print('')
    if should_print_draft_results():
        print('')
        print_draft_results(draft_results)
    draft_class = draft_class_accumulator(all_teams_list,draft_results)
    print('')
    if should_print_draft_class():
        print('')
        draft_class_printer(draft_class)


def draft_class_printer(draft_class):
    for team in draft_class:
        print(str(team) + ' Draft Class')
        teams_draft = draft_class[team]
        for pick in teams_draft:
            if int(pick) == 1:
                print(str(pick) + 'st pick: ' + str(teams_draft[pick][0]) + ', ' + str(teams_draft[pick][1]) + ' from ' + str(
                    teams_draft[pick][2]) + ' with the #' + str(int(teams_draft[pick][3]+1)) + ' overall pick.')
            elif int(pick) == 2:
                print(str(pick) + 'nd pick: ' + str(teams_draft[pick][0]) + ', ' + str(teams_draft[pick][1]) + ' from ' + str(
                    teams_draft[pick][2]) + ' with the #' + str(int(teams_draft[pick][3]+1)) + ' overall pick.')
            elif int(pick) == 3:
                print(str(pick) + 'rd pick: ' + str(teams_draft[pick][0]) + ', ' + str(teams_draft[pick][1]) + ' from ' + str(
                    teams_draft[pick][2]) + ' with the #' + str(int(teams_draft[pick][3]+1)) + ' overall pick.')
            else:
                print(str(pick) + 'th pick: ' + str(teams_draft[pick][0]) + ', ' + str(teams_draft[pick][1]) + ' from ' + str(
                    teams_draft[pick][2]) + ' with the #' + str(int(teams_draft[pick][3]+1)) + ' overall pick.')
        print('')


def draft_class_accumulator(all_teams_list,draft_results):
    draft_class = {}
    for team in all_teams_list:
        team_class = team_draft_class(team,draft_results)
        draft_class[team] = team_class
    return draft_class


def team_draft_class(team,draft_results):
    team_class = {}
    team_pick = 1
    for pick in range(len(draft_results)):
        team_with_pick = draft_results[pick][0]
        if team_with_pick.startswith(team):
            player_name = draft_results[pick][1]
            player_position = draft_results[pick][2]
            player_team = draft_results[pick][3]
            team_class[team_pick] = [player_name,player_position,player_team,pick]
            team_pick += 1
    return team_class


def find_player_ranking(selection, all_players):
    for i in range(len(all_players)):
        if all_players[i] == selection:
            return int(i) + 1


def available_player_list(prospects):
    available_players = []
    for i in range(len(prospects)):
        available_players.append(prospects[i + 1][0])
    return available_players


def user_draft(prospects, total_order, total_rounds):
    draft_results = {}
    available_players = available_player_list(prospects)
    all_players = available_player_list(prospects)
    draft_results = user_round(total_order,prospects,draft_results,available_players,all_players,total_rounds)
    return draft_results


def user_round(total_order,prospects,draft_results,available_players,all_players, total_rounds):
    overall_pick = 0
    total_picks = len(prospects)
    for draft_round in range(total_rounds):
        for pick in range(31):
            if overall_pick < total_picks:
                best_available_player = available_players[0]
                print('The suggested pick is ' + str(best_available_player))
                selection = str(input('Input selection (First Name Last Name) or hit enter for simulated pick: '))
                if selection == '':
                    selection = best_available_player
                else:
                    while selection not in available_players:
                        selection = str(input('Invalid selection. Input selection (First Name Last Name) or hit enter for simulated pick: '))
                player_ranking = find_player_ranking(selection, all_players)
                team = total_order[overall_pick]
                player_name = prospects[player_ranking][0]
                player_position = position_converter(prospects[player_ranking][1])
                player_team = prospects[player_ranking][2]
                draft_results[overall_pick] = [team, player_name, player_position, player_team]
                available_players.remove(selection)
                overall_pick += 1
    return draft_results


def day2_draft_order(lottery_standings,total_rounds):
    day2_order = []
    for i in range(total_rounds-1):
        current_rank = 30
        for pick in range(31):
            on_the_clock = lottery_standings[current_rank][0]
            day2_order.append(on_the_clock)
            current_rank -= 1
    return day2_order


def total_draft_order(draft_order,day2_order):
    for i in range(len(day2_order)):
        draft_order.append(day2_order[i])
    return draft_order


def print_draft_results(draft_results):
    for pick in draft_results:
        print('The ' + str(draft_results[pick][0]) + ' select ' + str(draft_results[pick][1]) + ', ' + str(draft_results[pick][2]) + ' from ' + str(draft_results[pick][3]) + ' with the #' + str(int(pick)+1) + ' overall pick.')


def simulated_draft(prospects, total_order, total_rounds):
    draft_results = {}
    draft_results = simulated_round(draft_results,total_order,prospects,total_rounds)
    return draft_results


def simulated_round(draft_results,total_order,prospects,total_rounds):
    overall_pick = 0
    total_picks = len(prospects)
    for draft_round in range(total_rounds):
        for pick in range(31):
            if overall_pick < total_picks:
                team = total_order[overall_pick]
                player_name = prospects[overall_pick+1][0]
                player_position = position_converter(prospects[overall_pick+1][1])
                player_team = prospects[overall_pick+1][2]
                draft_results[overall_pick] = [team, player_name, player_position, player_team]
                overall_pick += 1
    return draft_results


def position_converter(player_position):
    if player_position == 'C':
        player_position = 'Centre'
    if player_position == 'LW':
        player_position = 'Left Wing'
    if player_position == 'RW':
        player_position = 'Right Wing'
    if player_position == 'D':
        player_position = 'Defenceman'
    if player_position == 'LHD':
        player_position = 'Left handed Defenceman'
    if player_position == 'RHD':
        player_position = 'Right handed Defenceman'
    if player_position == 'G':
        player_position = 'Goalie'
    return player_position


def import_prospects():
    prospect_list = '0'
    print('Prospects rankings file should be a csv file with 4 columns (Ranking, Name, Position, Team)')
    while not prospect_list.endswith('.csv'):
        prospect_list = str(input('Input name of prospect rankings file (press enter for default): '))
        if prospect_list == '':
            prospect_list = 'prospects.csv'
    reader = csv.reader(open(prospect_list))
    prospects = {}
    for row in reader:
        key = int(row[0])
        if key in prospects:
            pass
        prospects[key] = row[1:]
    return prospects


def simulated_or_user_draft():
    answer = 0
    while answer != 's' and answer != 'u':
        answer = str(input('Simulated or User Draft? (s for simulated, u for user): '))
        if answer != 's' and answer != 'u':
            print('Invalid input')
        if answer == '':
            break
    return answer


if __name__ == '__main__':
    main()
