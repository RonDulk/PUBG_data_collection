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

def get_stats(gameMode,response,writer):
    attributes = response["data"]["attributes"]["gameModeStats"][gameMode]

    players_data = defaultdict(dict)

    players_data[playerid] = {
        **{"playerId": playerid, "gameMode": gameMode},
        **attributes}
    writer.writerow(players_data[playerid])


#check if the player already exists
covered_players = set()

#read csv
with open('new_squad_players.csv','r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    count = sum(1 for _ in csv_reader)
    print(count)
    csv_file.seek(0)
    t0 = time.process_time()
    next(csv_reader)
        
    #write the csv
    with open('lifetime.csv', mode='w') as data_file:
        writer = csv.DictWriter(data_file, fieldnames=headers,extrasaction='ignore')
        writer.writeheader()
        num_loop=0

        #start loop for players
        for line in csv_reader:
            num_loop=num_loop+1
            # if num_loop > 10:
            #     break
            t1 = time.process_time()
            playerid = (line['playerId'])
            print(f"playerId: {playerid}")
            if playerid in covered_players:
                continue
            covered_players.add(playerid)
            try:
                #endpoint for players
                players_endpoint = f"https://api.pubg.com/shards/steam/players/{playerid}/seasons/lifetime"

                #request server for players
                r = requests.get(players_endpoint, headers=header)

                #the response in r.text
                response = json.loads(r.text)

                #Refer to function
                get_stats("duo",response,writer)
                get_stats("squad",response,writer)
                get_stats("duo-fpp",response,writer)
                get_stats("squad-fpp",response,writer)

                #calculate and print time
                t2 = time.process_time()
                t3 = t2 - t1
                t4 = t2 - t0
                print(f"finished player number {num_loop} out of {count} elapsed time {t3} total time {t4}")

            except Exception as e:
                    print("Error1: " + str(e))
                    sleep(60)