import requests
from datetime import datetime, timedelta
import json
import csv
import time
from time import sleep
from collections import defaultdict

#authorization
api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3YTQ2OTJkMC1mMjc2LTAxMzctYzk2ZC0wYjdlY2UzYmI5NjYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTc0NzcxNDM5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJvbmR1bGtpbi1nbWFpIn0.ZjoJPr_DmRgOy2eK2pA1GQy5vekA39N8XU8pfInbhAM"
# matches_endpoint = "https://api.pubg.com/shards/steam/matches/"
header = {
    "Authorization": "Bearer " + api_key,
    "Accept": "application/vnd.api+json"
}

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




def request_from_server(request,gameMode,writer):
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
            get_current_stats(gameMode, current_response, writer)

    except Exception as e:
        #############################print("Error1: " + str(e))
        sleep(20)
        request_from_server(request,gameMode,writer)

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

# def get_stats(i,gameMode,response,writer):
#     attributes = response["data"][i]["attributes"]["gameModeStats"][gameMode]
#     # print(attributes)
#     playerid = response["data"][i]["relationships"]["player"]["data"]["id"]
#     playerid = playerid.strip("/")
#     # print(playerid)
#     players_data = defaultdict(dict)
#     players_data[playerid] = {
#         **{"playerId": playerid, "gameMode": gameMode},
#         **attributes}
#     writer.writerow(players_data[playerid])


#check if the player already exists
covered_players = set()

#read csv
def Macro(gameMode,csv_file,writefile_csv):
    with open(csv_file,'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        count = sum(1 for _ in csv_reader)
        print(count)
        csv_file.seek(0)
        #t0 = time.process_time()
        next(csv_reader)
        count_five_hundreads = 0
        #write the csv
        with open(writefile_csv, mode='w') as data_file:
            writer = csv.DictWriter(data_file, fieldnames=headers,extrasaction='ignore')
            writer.writeheader()
            num_loop=0
            count_to_send = 0
            string_to_send = ""
            #start loop for players
            for line in csv_reader:
                num_loop=num_loop+1
                count_five_hundreads=count_five_hundreads+1
                # if num_loop > 10:
                #     break
                #t1 = time.process_time()
                playerid = (line['playerId'])
                # print(f"playerId: {playerid}")
                if playerid in covered_players:
                    continue
                count_to_send = count_to_send + 1
                string_to_send = string_to_send + playerid + ","
                covered_players.add(playerid)
                if (count_to_send == 10):
                    players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={string_to_send}"
                    count_to_send = 0
                    string_to_send = ""

                    request_from_server(players_endpoint,gameMode,writer)
                    #calculate and print time
                    ##t2 = time.process_time()
                    ##t3 = t2 - t1
                    ##t4 = t2 - t0
                    if (count_five_hundreads == 500):
                        print(f"finished players number {num_loop} out of {count} ")
                        count_five_hundreads=0

            if(count_to_send != 0):
                players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={string_to_send}"
                request_from_server(players_endpoint,gameMode,writer)
Macro("duo","duo_new.csv","lifetime_duo_new.csv")
Macro("duo-fpp","duo_fpp_new.csv","lifetime_duo_fpp_new.csv")
Macro("squad","squad_new.csv","lifetime_squad_new.csv")
Macro("squad-fpp","squad_fpp_new.csv","lifetime_squad_fpp_new.csv")
