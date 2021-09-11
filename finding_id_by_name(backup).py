import requests
from datetime import datetime, timedelta
import json
import csv
import time
from time import sleep
from collections import defaultdict


api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3YTQ2OTJkMC1mMjc2LTAxMzctYzk2ZC0wYjdlY2UzYmI5NjYiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTc0NzcxNDM5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJvbmR1bGtpbi1nbWFpIn0.ZjoJPr_DmRgOy2eK2pA1GQy5vekA39N8XU8pfInbhAM"
player_endpoint = "https://api.pubg.com/shards/steam/players?filter[playerNames]=Seenitcoming"
player_endpoint_Or = "https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/squad/players?filter[playerIds]=account.54637389f48944eba0e6256d538b9f5b"
player_endpoint_Ben = "https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/squad/players?filter[playerIds]=account.1f81db05d897460d885268a64f7fc2cf"
player_endpoint_Yoav = "https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/squad/players?filter[playerIds]=account.1be0a44c37614253995100228452b990"

header = {
    "Authorization": "Bearer " + api_key,
    "Accept": "application/vnd.api+json"
}
r = requests.get(player_endpoint_Or, headers=header)
response = json.loads(r.text)
print (response)
r = requests.get(player_endpoint_Ben, headers=header)
response = json.loads(r.text)
print (response)
r = requests.get(player_endpoint_Yoav, headers=header)
response = json.loads(r.text)
print (response)

player_endpoint = "https://api.pubg.com/shards/steam/players?filter[playerNames]=RudenSJ"
r = requests.get(player_endpoint, headers=header)
response = json.loads(r.text)
print (response)

