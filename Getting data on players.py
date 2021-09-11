import requests
from datetime import datetime, timedelta
import json
import csv
import time
from time import sleep
from collections import defaultdict
import pickle
from threading import Thread
#authorization
api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3YTQ2OTJkMC1mMjc2LTAxMzctYzk2ZC0wYjdlY2UzYmI5NjYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTc0NzcxNDM5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJvbmR1bGtpbi1nbWFpIn0.ZjoJPr_DmRgOy2eK2pA1GQy5vekA39N8XU8pfInbhAM"
matches_endpoint = "https://api.pubg.com/shards/steam/matches/"
header = {
    "Authorization": "Bearer " + api_key,
    "Accept": "application/vnd.api+json"
}
playerid="account.54637389f48944eba0e6256d538b9f5b"

#function that saves and loads objects
def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


#check if the match already exists
pickle_in = open('D:/Ron/WORKS/Thesis/16.12.20/covered_matches.pkl',"rb")
covered_matches = pickle.load(pickle_in)
#covered_matches = set()
#save_object(covered_matches, 'D:/Ron/WORKS/Thesis/11.11.20/covered_matches.pkl')


#the headers of the csv
headers = ['playerId','gameMode','assists', 'boosts','dBNOs','dailyKills',
           'dailyWins', 'damageDealt','days', 'headshotKills', 'heals',
           'killPoints', 'kills','longestKill','longestTimeSurvived',
           'losses', 'maxKillStreaks','mostSurvivalTime','rankPoints',
           'rankPointsTitle','revives','rideDistance', 'roadKills',
           'roundMostKills','roundsPlayed','suicides','swimDistance',
           'teamKills', 'timeSurvived','top10s','vehicleDestroys',
           'walkDistance', 'weaponsAcquired', 'weeklyKills','weeklyWins',
           'winPoints', 'wins']

headers_matches = ["matchId",'playerMatchId', 'DBNOs', 'assists', 'boosts', 'damageDealt', 'deathType', 'headshotKills', 'heals',
           'killPlace', 'killStreaks', 'kills',
           'longestKill', 'name', 'playerId', 'revives', 'rideDistance', 'roadKills', 'swimDistance', 'teamKills',
           'timeSurvived', 'vehicleDestroys',
           'walkDistance', 'weaponsAcquired', 'winPlace', 'createdAt', 'stats', 'isCustomMatch', 'seasonState',
           'duration', 'gameMode', 'titleId','matchType',
           'shardId', 'tags', 'mapName', "rosterId", "won", "rank", "teamId"]


def get_matches(matches, match_type,writer_matches):
    for index, match in enumerate(matches):

        # if the match is already in covered matches, skip this
        if match["id"] in covered_matches:
            continue

        # if not, add match ID to set "covered_matches"
        covered_matches.add(match["id"])
        try:

            # request server for matches with ID
            r_matches = requests.get(matches_endpoint + match["id"], headers=header)

            # response in r.text
            match_data = json.loads(r_matches.text)

            # navigation to attributes
            attributes_matches = match_data["data"]["attributes"]

            # navigation to included
            players_matches = match_data["included"]

            # write the csv with its headers
            players_data_matches = defaultdict(dict)
            for player_matches in players_matches:
                if player_matches["type"] == "participant":
                    players_data_matches[player_matches["id"]] = {
                        **{"matchId": match["id"], "playerMatchId": player_matches["id"]},
                        **player_matches["attributes"]["stats"],
                        **attributes_matches,
                        **{
                            "rosterId": None, "won": None, "rank": None, "teamId": None
                        }
                    }
                elif player_matches["type"] == "roster":
                    for participant_matches in player_matches["relationships"]["participants"]["data"]:
                        players_data_matches[participant_matches["id"]] = {
                            **players_data_matches[participant_matches["id"]],
                            **{"rosterId": player_matches["id"], "won": player_matches["attributes"]["won"],
                               **player_matches["attributes"]["stats"]}
                        }


        except Exception as e:
            print("error sleeping \n" + str(e))
            sleep(60)

        for playerId, player_matches in players_data_matches.items():
            writer_matches.writerow(player_matches)


def request_from_server(request,game_mode,writer,gameMode_matches,match_type,writer_matches):
    try:
    # request server for players
    #     print(request)
        #remove last comma
        request = request[:-1] + "/"
        # print(request)

        #requesting from the server
        r = requests.get(request, headers=header)

        # the response in r.text
        response = json.loads(r.text)
        # print(response)
        ## Refer to function
        player_num_in_response = len(response["data"])
        response_iter = iter(response["data"])
        for i in range(player_num_in_response):
            # get_stats(i,gameMode, response, writer)
            current_response = next(response_iter)
            get_current_stats(game_mode, current_response, writer)
            # current_stats_thread = Thread(target=get_current_stats, args=(game_mode, current_response, writer))
            # current_stats_thread.start()

            matches = [*current_response["relationships"][gameMode_matches]["data"]]
            # matches_thread = Thread(target=get_matches, args=(matches,match_type,writer_matches))
            # matches_thread.start()
            #
            # current_stats_thread.join()
            # matches_thread.join()

            get_matches(matches,match_type,writer_matches)

    except Exception as e:
        print("Error1: " + str(e))
        sleep(60)
        request_from_server(request,game_mode,writer,gameMode_matches,match_type,writer_matches)

def get_current_stats(gameMode,current_response,writer):
    attributes = current_response["attributes"]["gameModeStats"][gameMode]
    # print(attributes)
    playerid = current_response["relationships"]["player"]["data"]["id"]
    playerid = playerid.strip("/")
    # print(playerid)

    players_data = defaultdict(dict)
    players_data[playerid] = {
        **{"playerId": playerid, "gameMode": gameMode},
        **attributes}
    writer.writerow(players_data[playerid])

#check if the player already exists
covered_players = set()

#read csv
def Macro(gameMode,writefile_csv_lifetime,writefile_csv_matches,gameMode_matches,match_type):
    #with open(csv_file,'r') as csv_file:
    #    csv_reader = csv.DictReader(csv_file)
    #    count = sum(1 for _ in csv_reader)
    #    print(count)
    #    csv_file.seek(0)
        #t0 = time.process_time()
    #    next(csv_reader)
    #    count_five_hundreads = 0
    #write the csv
    with open(writefile_csv_matches, mode='w') as matches_data_file,  open(writefile_csv_lifetime, mode='w') as lifetime_data_file:
        writer_matches = csv.DictWriter(matches_data_file, fieldnames=headers_matches, extrasaction='ignore')
        writer_matches.writeheader()

        writer = csv.DictWriter(lifetime_data_file, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()

        #num_loop=0
        #    ount_to_send = 0
        #string_to_send = ""

            #start loop for players
            #for line in csv_reader:
            #    num_loop=num_loop+1
            #   count_five_hundreads=count_five_hundreads+1
                # if num_loop > 10:
                #     break
                #t1 = time.process_time()
                #playerid = playerid
                # print(f"playerId: {playerid}")
                #if playerid in covered_players:
                #   continue
                #count_to_send = count_to_send + 1
                #string_to_send = string_to_send + playerid + ","
                #covered_players.add(playerid)
                #if (count_to_send == 10):
        players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={playerid}"
        #count_to_send = 0
        #string_to_send = ""

        request_from_server(players_endpoint,gameMode,writer,gameMode_matches,match_type,writer_matches)
                    #calculate and print time
                    #t2 = time.process_time()
                    #t3 = t2 - t1
                    #t4 = t2 - t0
            #if (count_five_hundreads == 100):
             #           print(f"finished players number {num_loop} out of {count}")
                        #count_five_hundreads = 0

            #if(count_to_send != 0):
             #   players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={string_to_send}"
             #   request_from_server(players_endpoint,gameMode,writer,gameMode_matches,match_type,writer_matches)
        print(f"finished player")


#Macro("duo","duo_new.csv","lifetime_duo_new.csv","matches_duo_new.csv","matchesDuo","Duo")
#Macro("duo-fpp","duo_fpp_new.csv","lifetime_duo_fpp_new.csv","matches_duo_fpp_new.csv","matchesDuoFPP","DuoFPP")
Macro("squad","lifetime_squad_new.csv","matches_squad_new.csv","matchesSquad","Squad")
Macro("squad-fpp","lifetime_squad_fpp_new.csv","matches_squad_fpp_new.csv","matchesSquadFPP","SquadFPP")

save_object(covered_matches, 'D:/Ron/WORKS/Thesis/16.12.20/covered_matches.pkl')
