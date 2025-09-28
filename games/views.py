from django.shortcuts import render
import requests

def game_listing(request):
    start_date = request.GET.get("start_date")
    if not start_date:
        return render(request, "gameListing.html", {"game_list": None})
    
    end_date = request.GET.get("end_date")
    team = request.GET.get("team_name", "").strip().lower()
    
    headers = {"Authorization": "26af8e03-7266-4878-a6ce-6890a733f7d5"}

    params = {
        "cursor": 0, 
        "per_page": 100, 
        "start_date": start_date, 
        "end_date": end_date,
    }
    
    games = []
    wins = {}
    
    while True:
        response = requests.get("https://api.balldontlie.io/v1/games", headers=headers, params=params)
        
        if response.status_code != 200:
            break
            
        data = response.json()
        
        for game in data["data"]:
            if team:
                home_name = game["home_team"]["full_name"].lower()
                visitor_name = game["visitor_team"]["full_name"].lower()
                if team not in home_name and team not in visitor_name:
                    continue
            
            home_score = game["home_team_score"]
            visitor_score = game["visitor_team_score"]
            home_team = game["home_team"]["full_name"]
            visitor_team = game["visitor_team"]["full_name"]
            
            if visitor_score > home_score:
                winner = visitor_team
                wins[visitor_team] = wins.get(visitor_team, 0) + 1
            elif home_score > visitor_score:
                winner = home_team
                wins[home_team] = wins.get(home_team, 0) + 1
            else:
                winner = "Draw"
            
            games.append({
                "date": game["date"],
                "home_team_score": home_score,
                "visitor_team_score": visitor_score,
                "home_team_name": home_team,
                "visitor_team_name": visitor_team,
                "post_season": game["postseason"],
                "winning_team": winner,
            })
        
        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        params["cursor"] = next_cursor
    
    winning_stat = dict(sorted(wins.items(), key=lambda x: x[1], reverse=True))
    

    return render(request, "gameListing.html", {
        "game_list": games, 
        "winning_stat": winning_stat
    })