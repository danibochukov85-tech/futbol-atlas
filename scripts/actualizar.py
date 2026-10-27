import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

token = os.environ.get("FOOTBALL_DATA_TOKEN")
if not token:
    raise SystemExit("Falta configurar FOOTBALL_DATA_TOKEN")

today = datetime.now(timezone.utc).date()
start = today - timedelta(days=2)
end = today + timedelta(days=7)

url = (
    "https://api.football-data.org/v4/matches"
    f"?dateFrom={start}&dateTo={end}"
)
request = Request(url, headers={"X-Auth-Token": token})

with urlopen(request, timeout=30) as response:
    data = json.load(response)

matches = []
for match in data.get("matches", []):
    score = match.get("score") or {}
    full = score.get("fullTime") or {}
    competition = match.get("competition") or {}
    matches.append({
        "id": match.get("id"),
        "competition": competition.get("code"),
        "league": competition.get("name"),
        "home": (match.get("homeTeam") or {}).get("name"),
        "away": (match.get("awayTeam") or {}).get("name"),
        "kickoff": match.get("utcDate"),
        "status": match.get("status"),
        "home_goals": full.get("home"),
        "away_goals": full.get("away"),
    })

output = Path("data/matches.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps({
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "matches": matches
    }, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"Actualizados {len(matches)} partidos")
