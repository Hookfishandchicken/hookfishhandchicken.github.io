
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

now = datetime.now(timezone.utc)
games = []

for year in [now.year, now.year + 1]:
    url = (
        "https://site.api.espn.com/apis/site/v2/"
        "sports/football/nfl/scoreboard"
        f"?dates={year}&seasontype=2&limit=500"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    for event in data.get("events", []):
        try:
            date = datetime.fromisoformat(
                event["date"].replace("Z", "+00:00")
            )

            if date <= now:
                continue

            competitors = event["competitions"][0]["competitors"]
            home = next(t for t in competitors if t["homeAway"] == "home")
            away = next(t for t in competitors if t["homeAway"] == "away")

            games.append({
                "date": event["date"],
                "home": {
                    "name": home["team"]["displayName"],
                    "logo": home["team"].get("logo", "")
                },
                "away": {
                    "name": away["team"]["displayName"],
                    "logo": away["team"].get("logo", "")
                }
            })
        except (KeyError, IndexError, StopIteration, ValueError):
            continue

games.sort(key=lambda game: game["date"])

output = Path("nfl/nfl.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps({"games": games, "updated": now.isoformat()}, indent=2),
    encoding="utf-8"
)

print(f"Saved {len(games)} upcoming NFL games")
