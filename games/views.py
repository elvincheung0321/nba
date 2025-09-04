from django.shortcuts import render
import requests
import json

url = "https://api.balldontlie.io/v1/games"

def game_listing(request):
    return_game_list = []
    winning_stats = {}
    
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    team_name = request.GET.get("team_name", "").strip()
    
    headers = {"Authorization": "26af8e03-7266-4878-a6ce-6890a733f7d5"}
    params = {"cursor": 0, "per_page": 100, "start_date": start_date, "end_date": end_date}
    
    if not start_date:
        return render(request, "gameListing.html", {"game_list": None})

    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            game_list = json.loads(response.content)["data"]
            meta = json.loads(response.content).get("meta", {})
            next_cursor = meta.get("next_cursor")
            
            for game in game_list:
                if team_name and (team_name.lower() not in game["home_team"]["full_name"].lower() and
                                  team_name.lower() not in game["visitor_team"]["full_name"].lower()):
                    continue 
                
                game_dict = {
                    "date": game["date"],
                    "home_team_score": game["home_team_score"],
                    "visitor_team_score": game["visitor_team_score"],
                    "home_team_name": game["home_team"]["full_name"],
                    "visitor_team_name": game["visitor_team"]["full_name"],
                    "post_season":game["postseason"]
                }

                if game["visitor_team_score"] > game["home_team_score"]:
                    game_dict["winning_team"] = game["visitor_team"]["full_name"]
                    winning_stats[game["visitor_team"]["full_name"]] = winning_stats.get(game["visitor_team"]["full_name"], 0) + 1
                elif game["visitor_team_score"] < game["home_team_score"]:
                    game_dict["winning_team"] = game["home_team"]["full_name"]
                    winning_stats[game["home_team"]["full_name"]] = winning_stats.get(game["home_team"]["full_name"], 0) + 1
                else:
                    game_dict["winning_team"] = "Draw"

                return_game_list.append(game_dict)

            if next_cursor is not None:
                params["cursor"] = next_cursor
            else:
                break
        else:
            break

    sorted_winning_stat = dict(sorted(winning_stats.items(), key=lambda x: x[1], reverse=True))
    context = {"game_list": return_game_list, "winning_stat": sorted_winning_stat}
    return render(request, "gameListing.html", context)