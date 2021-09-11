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
        print("Error1: " + str(e))
        sleep(60)
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

#check if the player already exists
covered_players = set()

def micro(gameMode,writer,string_to_send):
    players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={string_to_send}"
    request_from_server(players_endpoint, gameMode, writer)


#read csv
def Macro(csv_file,writefile_csv):
    with open(csv_file,'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_file.seek(0)
        t0 = time.process_time()
        next(csv_reader)

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
                if (num_loop%100==0):
                    print(f"starting player number {num_loop} ")
                # if num_loop > 10:
                #     break
                t1 = time.process_time()
                playerid = (line['playerId'])
                # print(f"playerId: {playerid}")
                if playerid in covered_players:
                    continue
                count_to_send = count_to_send + 1
                string_to_send = string_to_send + playerid + ","
                covered_players.add(playerid)
                if (count_to_send == 10):
                    micro("duo", writer,string_to_send)
                    micro("duo-fpp", writer,string_to_send)
                    micro("squad", writer,string_to_send)
                    micro("squad-fpp", writer,string_to_send)
                   # players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={string_to_send}"
                    count_to_send = 0
                    string_to_send = ""

                    #request_from_server(players_endpoint,gameMode,writer)

                    #calculate and print time
                   # print(f"finished players number {num_loop} ")
            # calculate and print time

            if(count_to_send != 0):
                players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={string_to_send}"
                request_from_server(players_endpoint,gameMode,writer)
                
Macro("matches.csv","lifetime.csv")

