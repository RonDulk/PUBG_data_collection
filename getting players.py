import requests
from datetime import datetime, timedelta
import json
import csv
import time
from time import sleep
from collections import defaultdict


def get_matches(matches,match_type):
    for index, match in enumerate(matches):
                    
        #if the match is already in covered matches, skip this
        # t1 = time.clock()


        if match["id"] in covered_matches:
            continue

        #if not, add match ID to set "covered_matches"
        covered_matches.add(match["id"])
        # t2 = time.clock()
        # print("elapsed check covered", t2 - t1)
        try:
            # t1 = time.clock()


            #request server for matches with ID
            r = requests.get(matches_endpoint + match["id"], headers=header)

            #response in r.text
            match_data = json.loads(r.text)
            # t2 = time.clock()
            # print("elapsed json load in matches", t2 - t1)
            #navigation to attributes
            attributes = match_data["data"]["attributes"]

            #navigation to included
            players = match_data["included"]
            
            #write the csv with its headers
            players_data = defaultdict(dict)
            # t1 = time.clock()

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
            # t2 = time.clock()
            # print("elapsed for get players in matches", t2 - t1)
            # if (index + 1) % 9 == 0:
            #     end_time = time.time()
            #     elapsed = int(end_time - start_time)
            #     print(f"Going to sleep for {61 - elapsed} seconds")
            #     sleep(61 - elapsed)

        except Exception as e:
            print("error sleeping \n"+str(e))
            sleep(1)
        # t1 = time.clock()


        for playerId, player in players_data.items():
            writer.writerow(player)
        # t2 = time.clock()
        # print("elapsed final for", t2 - t1)
        # print(f"Finished {match_type} match number {index} out of {len(matches)} matches of player number {playerid}")





#authorization
api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3YTQ2OTJkMC1mMjc2LTAxMzctYzk2ZC0wYjdlY2UzYmI5NjYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTc0NzcxNDM5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJvbmR1bGtpbi1nbWFpIn0.ZjoJPr_DmRgOy2eK2pA1GQy5vekA39N8XU8pfInbhAM"
matches_endpoint = "https://api.pubg.com/shards/steam/matches/"
header = {
    "Authorization": "Bearer " + api_key,
    "Accept": "application/vnd.api+json"
}

#number of samples
#samples_num = 14

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

#read csv
with open('Clean.csv','r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    count = sum(1 for _ in csv_reader)
    print(count)
    csv_file.seek(0)
    csv_reader = csv.DictReader(csv_file)
    t0 = time.clock()
    next(csv_reader)
        
    #write the csv
    with open('matches.csv', mode='w') as data_file:
        writer = csv.DictWriter(data_file, fieldnames=headers)
        writer.writeheader()

        num_loop=0
        # t0 = time.clock()
        #start loop for players
        for line in csv_reader:
            num_loop=num_loop+1
            # if num_loop > 10:
            #     break
            t1 = time.clock()

            playerid = (line['playerId'])
            # print(f"starting player number {num_loop} out of {count} elapsed time{t2}")
            try:
                # t1=time.clock()

                #endpoint for players
                players_endpoint = f"https://api.pubg.com/shards/steam/players/{playerid}/seasons/lifetime"
                # t2=time.clock()
                # print("elapsed players endpoint",t2-t1)
                # print(players_endpoint)

                #request server for players
                # t1=time.clock()
                r = requests.get(players_endpoint, headers=header)
                # t2 = time.clock()
                # print("elapsed request get players", t2 - t1)
                #the response in r.text
                # t1=time.clock()
                response = json.loads(r.text)
                # t2 = time.clock()
                # print("elapsed json loads", t2 - t1)
                #print(r.text)

                #navigate through data for duo
                #print(response["data"]["relationships"])
                # t1=time.clock()

                matches = response["data"]["relationships"]["matchesSquad"]["data"]
                get_matches(matches,"Squad")
                matches = response["data"]["relationships"]["matchesDuo"]["data"]
                get_matches(matches,"Duo")
                matches = response["data"]["relationships"]["matchesDuoFPP"]["data"]
                get_matches(matches,"DuoFPP")
                matches = response["data"]["relationships"]["matchesSquadFPP"]["data"]
                get_matches(matches,"SquadFPP")

                t2 = time.clock()
                t3 = t2 - t1
                t4 = t2 - t0
                print(f"finished player number {num_loop} out of {count} elapsed time {t3} total time {t4}")
                # print("elapsed matches block", t2 - t1)
                # #for each object in data look at matches ID
                # for index, match in enumerate(matches):

                #     #if the match is already in covered matches, skip this
                #     if match["id"] in covered_matches:
                #         continue

                #     #if not, add match ID to set "covered_matches"
                #     covered_matches.add(match["id"])
                #     try:

                #         #request server for matches with ID
                #         r = requests.get(matches_endpoint + match["id"], headers=header)

                #         #response in r.text
                #         match_data = json.loads(r.text)

                #         #navigation to attributes
                #         attributes = match_data["data"]["attributes"]

                #         #navigation to included
                #         players = match_data["included"]

                #         #write the csv with its headers
                #         players_data = defaultdict(dict)
                #         for player in players:
                #             if player["type"] == "participant":
                #                 players_data[player["id"]] = {
                #                     **{"matchId": match["id"], "playerMatchId": player["id"]},
                #                     **player["attributes"]["stats"],
                #                     **attributes,
                #                     **{
                #                         "rosterId": None, "won": None, "rank": None, "teamId":None
                #                     }
                #                 }
                #             elif player["type"] == "roster":
                #                 for participant in player["relationships"]["participants"]["data"]:
                #                     players_data[participant["id"]] = {
                #                         **players_data[participant["id"]],
                #                         **{"rosterId": player["id"], "won": player["attributes"]["won"], **player["attributes"]["stats"]}
                #                     }

                #         # if (index + 1) % 9 == 0:
                #         #     end_time = time.time()
                #         #     elapsed = int(end_time - start_time)
                #         #     print(f"Going to sleep for {61 - elapsed} seconds")
                #         #     sleep(61 - elapsed)

                #     except Exception as e:
                #         print("error sleeping \n"+str(e))
                #         sleep(60)

                #     for playerId, player in players_data.items():
                #         writer.writerow(player)

                #     print(f"Finished match number {index} out of {len(matches)} matches of player number {line}")

                # #if (sample_num + 1) % 10 == 0:
                # #    print("About to exceed sample quota going to sleep")
                # #    sleep(60)

                # #print(response["data"]["relationships"])
                # #matches = response["data"]["relationships"]["matchesDuo"]["data"]

                #   #for each object in data look at matches ID
                # for index, match in enumerate(matches):

                #     #if the match is already in covered matches, skip this
                #     if match["id"] in covered_matches:
                #         continue

                #     #if not, add match ID to set "covered_matches"
                #     covered_matches.add(match["id"])
                #     try:

                #         #request server for matches with ID
                #         r = requests.get(matches_endpoint + match["id"], headers=header)

                #         #response in r.text
                #         match_data = json.loads(r.text)

                #         #navigation to attributes
                #         attributes = match_data["data"]["attributes"]

                #         #navigation to included
                #         players = match_data["included"]

                #         #write the csv with its headers
                #         players_data = defaultdict(dict)
                #         for player in players:
                #             if player["type"] == "participant":
                #                 players_data[player["id"]] = {
                #                     **{"matchId": match["id"], "playerMatchId": player["id"]},
                #                     **player["attributes"]["stats"],
                #                     **attributes,
                #                     **{
                #                         "rosterId": None, "won": None, "rank": None, "teamId":None
                #                     }
                #                 }
                #             elif player["type"] == "roster":
                #                 for participant in player["relationships"]["participants"]["data"]:
                #                     players_data[participant["id"]] = {
                #                         **players_data[participant["id"]],
                #                         **{"rosterId": player["id"], "won": player["attributes"]["won"], **player["attributes"]["stats"]}
                #                     }

                #         # if (index + 1) % 9 == 0:
                #         #     end_time = time.time()
                #         #     elapsed = int(end_time - start_time)
                #         #     print(f"Going to sleep for {61 - elapsed} seconds")
                #         #     sleep(61 - elapsed)

                #     except Exception as e:
                #         print("error sleeping \n"+str(e))
                #         sleep(60)

                #     for playerId, player in players_data.items():
                #         writer.writerow(player)

                #     print(f"Finished match number {index} out of {len(matches)} matches of player number {line}")

                # #if (sample_num + 1) % 10 == 0:
                # #    print("About to exceed sample quota going to sleep")
                # #    sleep(60)

            except Exception as e:
                    print("error: " + str(e))
                    sleep(60)


