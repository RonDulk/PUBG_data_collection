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

#function that saves and loads objects
def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

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


def get_matches(matches, match_type,writer_matches,covered_matches,playerid):
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


def request_from_server(request,game_mode,writer,gameMode_matches,match_type,writer_matches,covered_matches,playerid):
    try:
    # request server for players
        request = request

        #requesting from the server
        r = requests.get(request, headers=header)

        # the response in r.text
        response = json.loads(r.text)

        ## Refer to function
        player_num_in_response = len(response["data"])
        response_iter = iter(response["data"])
        for i in range(player_num_in_response):
            current_response = next(response_iter)
            get_current_stats(game_mode, current_response, writer,playerid)
            matches = [*current_response["relationships"][gameMode_matches]["data"]]
            get_matches(matches,match_type,writer_matches,covered_matches,playerid)

    except Exception as e:
        print("Error1: " + str(e))
        sleep(60)
        request_from_server(request,game_mode,writer,gameMode_matches,match_type,writer_matches,covered_matches,playerid)

def get_current_stats(gameMode,current_response,writer,playerid):
    attributes = current_response["attributes"]["gameModeStats"][gameMode]
    playerid = current_response["relationships"]["player"]["data"]["id"]
    playerid = playerid.strip("/")
    players_data = defaultdict(dict)
    players_data[playerid] = {
        **{"playerId": playerid, "gameMode": gameMode},
        **attributes}
    writer.writerow(players_data[playerid])

#check if the player already exists
covered_players = set()

#read csv
def Macro(gameMode,writefile_csv_lifetime,writefile_csv_matches,gameMode_matches,match_type,covered_matches,playerid):

    #write the csv
    with open(writefile_csv_matches, mode='w') as matches_data_file,  open(writefile_csv_lifetime, mode='w') as lifetime_data_file:
        writer_matches = csv.DictWriter(matches_data_file, fieldnames=headers_matches, extrasaction='ignore')
        writer_matches.writeheader()
        writer = csv.DictWriter(lifetime_data_file, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        players_endpoint = f"https://api.pubg.com/shards/steam/seasons/lifetime/gameMode/{gameMode}/players?filter[playerIds]={playerid}"
        request_from_server(players_endpoint,gameMode,writer,gameMode_matches,match_type,writer_matches,covered_matches,playerid)
        if gameMode=="squad-fpp":
            print(f"finished player {playerid}")
        save_object(covered_matches, f'E:/Thesis/experimental phase/actual/covered_matches.pkl')

def get_stats_on_single_player (playerid,game_date):
    pickle_in = open(f'E:/Thesis/experimental phase/actual/covered_matches.pkl', "rb")
    covered_matches = pickle.load(pickle_in)
    Macro("squad",f"{game_date}/{playerid}lifetime_squad_new.csv",f"{game_date}/{playerid}matches_squad_new.csv","matchesSquad","Squad",covered_matches,playerid)
 #   Macro("squad-fpp",f"{game_date}/{playerid}lifetime_squad_fpp_new.csv",f"{game_date}/{playerid}matches_squad_fpp_new.csv","matchesSquadFPP","SquadFPP",covered_matches,playerid)

game_date="8.4.21"






get_stats_on_single_player("account.2cb84e75764e4503afa65d2e438058b5",game_date)
get_stats_on_single_player("account.354a06c799d64409a116b8c5fde8a8bb",game_date)
get_stats_on_single_player("account.2f737a33346247f59994dc0ba9839422",game_date)
get_stats_on_single_player("account.a0e0a833e0e14765b6892f37d76eab70",game_date)
get_stats_on_single_player("account.64c6f19517c1498693ca4c975b55acbd",game_date)
get_stats_on_single_player("account.6edcdc762894460c911a1b7008a201e5",game_date)
get_stats_on_single_player("account.3bcef14eb2a04c39b26b03d54ec9b641",game_date)
get_stats_on_single_player("account.92f501a43b98489bb1c3bb4de06b2068",game_date)
get_stats_on_single_player("account.0262a9b591b047bbb72241b3d451108f",game_date)
get_stats_on_single_player("account.b929ea623aaf4d0ebe0f308f47b71494",game_date)
get_stats_on_single_player("account.9593d8e0d5dc4cd788101a1a36144ab7",game_date)
get_stats_on_single_player("account.57edf3e6cd274713bc0eb2df9ed1050d",game_date)
get_stats_on_single_player("account.ea51db61ca8f43d99ba650382b09fdef",game_date)
get_stats_on_single_player("account.97e84d09bd394ae5b6ddef222d866262",game_date)
get_stats_on_single_player("account.a484abbdc8a64d10a014813e5dde5761",game_date)
get_stats_on_single_player("account.dd85c8b27bdf4138b6fe0267b8ceee92",game_date)
get_stats_on_single_player("account.61a46c6c22bf4eecbafbaaaa513f68b8",game_date)
get_stats_on_single_player("account.8c6bc563690e42b5bc0028fe438b153e",game_date)
get_stats_on_single_player("account.a05023c7dfee43958ccc28626b79c2b3",game_date)
get_stats_on_single_player("account.5ddada1165024af4aadfe72982c215c1",game_date)
get_stats_on_single_player("account.8715f7d9e42d4ae280f3ad2f018b69c9",game_date)
get_stats_on_single_player("account.f0237647bf0441bb88eb28ef8ec1d8f3",game_date)
get_stats_on_single_player("account.dd30917c8054441ca50fa8ba702e7743",game_date)
get_stats_on_single_player("account.53f42a54b471437aa1caae12abaa8eec",game_date)
get_stats_on_single_player("account.c73cc15e573d4cc8b10f809e7687949e",game_date)
get_stats_on_single_player("account.15a5d50a34ea4b1a87e0946697bbea51",game_date)
get_stats_on_single_player("account.acecb6ed0fcf40bc8f5ae0bbe11db941",game_date)
get_stats_on_single_player("account.c80925ca0d224fa4bad5d61b96affb28",game_date)
get_stats_on_single_player("account.f2afee80da314db98719b0a35c32bd5d",game_date)
get_stats_on_single_player("account.c41be816823e487c8c0c1d8872b61365",game_date)
get_stats_on_single_player("account.7d04baa79a1f46bc9a60fd96ebacaf8e",game_date)
get_stats_on_single_player("account.af8846e759064431956cc1f2c97fe213",game_date)
get_stats_on_single_player("account.a0c8003790b947e081655a65a1e45006",game_date)
get_stats_on_single_player("account.cf0a2340067e4459b8ed9a6cc2bddbc0",game_date)
get_stats_on_single_player("account.6c1812c3d26c491d8e2d51fd00236388",game_date)
get_stats_on_single_player("account.ea382ca125154b8398c8781345e6ff12",game_date)
get_stats_on_single_player("account.3674c92ab29a4d9eaa9863b17e27846b",game_date)
get_stats_on_single_player("account.6f25fc104c074b2a9e1036cf77602be2",game_date)
get_stats_on_single_player("account.a2c7957db7904171b49113fdeab84a09",game_date)
get_stats_on_single_player("account.9e69e784d5574ddb84aca3584252acaa",game_date)
get_stats_on_single_player("account.874996579653489dae32125822209d5b",game_date)
get_stats_on_single_player("account.a49860155d744e9aa52a552c3f47ef34",game_date)
get_stats_on_single_player("account.a11353b137824a65b1e78c2ded13dd4d",game_date)
get_stats_on_single_player("account.0a89add76c3c4266a8a1e4278286c35f",game_date)
get_stats_on_single_player("account.3a0b3a2648dd472d9254718eb8df226a",game_date)
get_stats_on_single_player("account.56bcac1076bb4ae9a6e71c7eaa985c34",game_date)
get_stats_on_single_player("account.ce4f6d087fcb47538681a32cb2d34f80",game_date)
get_stats_on_single_player("account.9ef8cda8738c40baa91240d839089714",game_date)
get_stats_on_single_player("account.6cc4b1b27755482d88016684ba1f6f07",game_date)
get_stats_on_single_player("account.8471acecf97b4e08bcfb0db3b37da912",game_date)
get_stats_on_single_player("account.771d59570cda40b48d471dd858993169",game_date)
get_stats_on_single_player("account.93fe61158e41485db8de925f60b40e05",game_date)
get_stats_on_single_player("account.87f2b2d182f7465eb93b57315bf6bcf3",game_date)
get_stats_on_single_player("account.ef422cab049d4692871716e0910846ec",game_date)
get_stats_on_single_player("account.9486e67aeb9141e599f6843fc6878209",game_date)
get_stats_on_single_player("account.2eb56e6db38649f998754b8ba29bde67",game_date)
get_stats_on_single_player("account.80ad170ae25e4691bbe1ca648ede5640",game_date)
get_stats_on_single_player("account.1ae178cb5cea4435956724e2bb97c329",game_date)
get_stats_on_single_player("account.5861cf1fd7ad478389e03bb7174c36b0",game_date)
get_stats_on_single_player("account.10b6a18a393148e69e4022b900629499",game_date)
get_stats_on_single_player("account.f9d8d7f350a74db09a0e40e9ac696690",game_date)
get_stats_on_single_player("account.a49fcb68f6454ae684b886431838bbeb",game_date)
get_stats_on_single_player("account.0c00ee3df8aa41e5bb018a0921ac66a7",game_date)
get_stats_on_single_player("account.49e0bc5019744af4b12f4dabe773a26b",game_date)
get_stats_on_single_player("account.25e6c5c11cb0487c850ab61e1f9dab29",game_date)
get_stats_on_single_player("account.aded7ee9a53149ae8c57ab7c1cef0bb8",game_date)
get_stats_on_single_player("account.9fea4f4461a84d3cb49fe0c717af26e3",game_date)
get_stats_on_single_player("account.b5c1b51f9eec4a0cb04cc2cc0086537f",game_date)
get_stats_on_single_player("account.1745677a85cc43f6a1c813257e1cafb6",game_date)
get_stats_on_single_player("account.d1f3acdb190e4b2e9902bd94afae2141",game_date)
get_stats_on_single_player("account.6ed0acc58ae946d1a2433548456dfef6",game_date)
get_stats_on_single_player("account.3035277101e54cb8a3aae7a1d1facd39",game_date)
get_stats_on_single_player("account.ad36ce57f8c4408cbc62237ed01244d8",game_date)
get_stats_on_single_player("account.bb49773c862244718985f3e548950a17",game_date)
get_stats_on_single_player("account.6cf68a3750864d22829a6e9b9a02d37a",game_date)
get_stats_on_single_player("account.52bdf148b35642aba1d675ce4b24c045",game_date)
get_stats_on_single_player("account.ae0e8bb274884e1eb6b4a794c362ea39",game_date)
get_stats_on_single_player("account.66b35c0bc6c54e1ba0e32b03e53fff63",game_date)
get_stats_on_single_player("account.937c6f6ed1c540c69af0b7c12057090a",game_date)
get_stats_on_single_player("account.093d315f25c94f28a74b23a5a352276e",game_date)
get_stats_on_single_player("account.6b8429fe564447a0a078224dfd5335e2",game_date)
get_stats_on_single_player("account.7f110949214a43fabd789e46f3a5ba44",game_date)
get_stats_on_single_player("account.64274250489d4b97b6a7b64a06ac21ac",game_date)
get_stats_on_single_player("account.9a4e414a8dec4432aadb2ed13d7391ba",game_date)
get_stats_on_single_player("account.61e462c7f4bf4806a1d41d5524d0c126",game_date)
get_stats_on_single_player("account.4368564556d04978b5aa1e5064a57a07",game_date)
get_stats_on_single_player("account.7944d20d4a704d0082b14eb326c853f4",game_date)
get_stats_on_single_player("account.97d6460cf39b4d2eb02fa8d39e9b4dd4",game_date)
get_stats_on_single_player("account.6e7ccd5162c549b0a7c5e34f6468ac4a",game_date)
get_stats_on_single_player("account.66db1b480a5c49ac9266163921cf04f2",game_date)
get_stats_on_single_player("account.68e6825c0c9b467a9ebe6dae3f605d11",game_date)
get_stats_on_single_player("account.58469797f14f4962a857ead7db1e12aa",game_date)
get_stats_on_single_player("account.fc3c946771194fa4982a4789d5a68dd6",game_date)
get_stats_on_single_player("account.d97ad349a07344599d14e8bfa541720d",game_date)
get_stats_on_single_player("account.62c857472bac45bda1114e2c5dcec611",game_date)
get_stats_on_single_player("account.31d58a9f1cb54147a7e6f912aed61a40",game_date)
get_stats_on_single_player("account.6c01d152f58044b387b17b891db7f905",game_date)
get_stats_on_single_player("account.8dd2752c98804bbbb793f34ebb5be644",game_date)
get_stats_on_single_player("account.0b8d514212f14df5b6980a5b22a33cd7",game_date)
get_stats_on_single_player("account.eb2f3eb7605a4324be9ac06c4d79dd8a",game_date)
get_stats_on_single_player("account.89c871ac06db4ef58890176c5158ccb8",game_date)
get_stats_on_single_player("account.d726a05c47d94178805dd26d024d135d",game_date)
get_stats_on_single_player("account.50d406ed02984c88b72c5ecda24b342e",game_date)
get_stats_on_single_player("account.8d01ca40edc940febebd726a80acf811",game_date)
get_stats_on_single_player("account.949e3a65a2414b4c8af391de17d80dc2",game_date)
get_stats_on_single_player("account.8eb5381fed0645e889183832b856d985",game_date)
get_stats_on_single_player("account.ab3aa65dd71a4a72a62ae6db6fc19671",game_date)
get_stats_on_single_player("account.908d49f3c75b484a978da89eb7f63a12",game_date)
get_stats_on_single_player("account.53f47be24855439d824ee1b5aba0f915",game_date)
get_stats_on_single_player("account.f63ba7130db148d8a65393417a8ad662",game_date)
get_stats_on_single_player("account.777af340a6c24554b42f2cd27cbdb274",game_date)
get_stats_on_single_player("account.ebea787a10e1438f9f1e6dc180bf4023",game_date)
get_stats_on_single_player("account.a6955831f6db4b83930c68620e354edf",game_date)
get_stats_on_single_player("account.0603c839393240b1b585793d5f9a8ed0",game_date)
get_stats_on_single_player("account.b1f8f3e069fc41b8ada8a9576cbc3738",game_date)
get_stats_on_single_player("account.1217f12322f243c382f2d7efd9a88991",game_date)
get_stats_on_single_player("account.baa8f6915562482ba59ced7606119849",game_date)
get_stats_on_single_player("account.59c2057c48f041df8e1d6378dd1e4433",game_date)
get_stats_on_single_player("account.6555142aed8c4b128be390034ab3db88",game_date)
get_stats_on_single_player("account.743f7e4f62894a3da9d4282565d77194",game_date)
get_stats_on_single_player("account.1a57b21c11bf4a279424d493b39cd5b9",game_date)


