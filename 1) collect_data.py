import requests
from datetime import datetime, timedelta
import json
import csv
from time import sleep
from collections import defaultdict
import time


#authorization
api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3YTQ2OTJkMC1mMjc2LTAxMzctYzk2ZC0wYjdlY2UzYmI5NjYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTc0NzcxNDM5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJvbmR1bGtpbi1nbWFpIn0.ZjoJPr_DmRgOy2eK2pA1GQy5vekA39N8XU8pfInbhAM"
matches_endpoint = "https://api.pubg.com/shards/steam/matches/"
header = {
    "Authorization": "Bearer " + api_key,
    "Accept": "application/vnd.api+json"
}

#number of samples
samples_num = 14

#the headers of the csv
headers = ["matchId",'playerMatchId', 'DBNOs', 'assists', 'boosts', 'damageDealt', 'deathType', 'headshotKills', 'heals',
           'killPlace', 'killStreaks', 'kills',
           'longestKill', 'name', 'playerId', 'revives', 'rideDistance', 'roadKills', 'swimDistance', 'teamKills',
           'timeSurvived', 'vehicleDestroys',
           'walkDistance', 'weaponsAcquired', 'winPlace', 'createdAt', 'stats', 'isCustomMatch', 'seasonState',
           'duration', 'gameMode', 'titleId','matchType',
           'shardId', 'tags', 'mapName', "rosterId", "won", "rank", "teamId"]

#check if the match already exists
covered_matches = set()

#write the csv
with open('Clean.csv', mode='w') as data_file:
    writer = csv.DictWriter(data_file, fieldnames=headers)
    writer.writeheader()

    #start loop for samples from 0 to 13
    for sample_num in range(samples_num):
        try:

            #set the date with help of the loop
            date = (datetime.utcnow() - timedelta(days=sample_num+1, seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

            #endpoint for samples
            samples_endpoint = f"https://api.pubg.com/shards/steam/samples?filter[createdAt-start]={date}"

            #request server for samples
            r = requests.get(samples_endpoint, headers=header)

            #the response in r.text
            response = json.loads(r.text)

            #navigate through data
            matches = response["data"]["relationships"]["matches"]["data"]

            #for each object in data look at matches ID
            for index, match in enumerate(matches):
                
                #if the match is already in covered matches, skip this
                if match["id"] in covered_matches:
                    continue

                #if not, add match ID to set "covered_matches"
                covered_matches.add(match["id"])
                try:

                    #request server for matches with ID
                    r = requests.get(matches_endpoint + match["id"], headers=header)

                    #response in r.text
                    match_data = json.loads(r.text)

                    #navigation to attributes
                    attributes = match_data["data"]["attributes"]

                    #navigation to included
                    players = match_data["included"]
                    
                    #write the csv with its headers
                    players_data = defaultdict(dict)
                    for player in players:
                        if player["type"] == "participant":
                            players_data[player["id"]] = {
                                **{"matchId": match["id"], "playerMatchId": player["id"]},
                                **player["attributes"]["stats"],
                                **attributes,
                                **{
                                    "rosterId": None, "won": None, "rank": None, "teamId":None
                                }
                            }
                        elif player["type"] == "roster":
                            for participant in player["relationships"]["participants"]["data"]:
                                players_data[participant["id"]] = {
                                    **players_data[participant["id"]],
                                    **{"rosterId": player["id"], "won": player["attributes"]["won"], **player["attributes"]["stats"]}
                                }

                    # if (index + 1) % 9 == 0:
                    #     end_time = time.time()
                    #     elapsed = int(end_time - start_time)
                    #     print(f"Going to sleep for {61 - elapsed} seconds")
                    #     sleep(61 - elapsed)

                except Exception as e:
                    print("error sleeping \n"+str(e))
                    sleep(60)

                for playerId, player in players_data.items():
                    writer.writerow(player)

            print(f"Finished match number {index} out of {len(matches)} matches of sample number {sample_num}")
            if (sample_num + 1) % 10 == 0:
                print("About to exceed sample quota going to sleep")
                sleep(60)


        except Exception as e:
            print("error: " + str(e))
            sleep(60)

