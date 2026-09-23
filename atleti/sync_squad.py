import re

from . import dossier


def _soccerdata():
    try:
        import soccerdata
    except Exception:
        return None
    return soccerdata


def _normalize_team_name(value):
    text = str(value or "").strip().lower()
    return (
        text.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ü", "u")
        .replace("ñ", "n")
        .replace("\n", " ")
        .replace("  ", " ")
    )


def _clean_field(value):
    text = str(value or "Unknown").strip()
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+Name:\s*\d+.*$", "", text)
    text = re.sub(r"\s+dtype:\s*str$", "", text)
    return text or "Unknown"


def _season_code(season):
    digits = re.sub(r"\D", "", str(season))
    if len(digits) == 4:
        return digits
    if len(digits) >= 6:
        if digits.startswith("19") or digits.startswith("20"):
            return digits[2:4] + digits[-2:]
        return digits[0:2] + digits[-2:]
    raise ValueError(f"Could not parse season: {season!r}")


def _load_atletico(player_stats, aliases):
    team_level = player_stats.index.get_level_values("team")
    for team_name in team_level.unique():
        if _normalize_team_name(team_name) in {
            "atletico madrid",
            "atletico de madrid",
            "atletico madri",
            "atletico",
        }:
            return player_stats.xs(team_name, level="team", drop_level=False)
    for alias in aliases:
        try:
            return player_stats.xs(alias, level="team", drop_level=False)
        except KeyError:
            continue
    return None


_POS_FITS = {
    "GK": ["goalkeeper depth"],
    "DF": ["3CB base", "back four"],
    "DF,MF": ["wing-back", "3CB hybrid"],
    "MF,DF": ["wing-back", "3CB hybrid"],
    "MF": ["double pivot", "half-space"],
    "MF,FW": ["wide forward", "box overload"],
    "FW,MF": ["wide forward", "box overload"],
    "FW": ["central striker", "pressing front"],
}


def _enrich(row, idx_label):
    player_name = _clean_field(idx_label)
    position = _clean_field(row.get(("pos", ""), "Unknown"))
    minutes = float(row.get(("Playing Time", "Min"), 0) or 0)
    matches = int(row.get(("Playing Time", "MP"), 0) or 0)
    return {
        "name": player_name,
        "position": position,
        "minutes": minutes,
        "matches_played": matches,
    }


def _tier(players):
    total = sum(p["minutes"] for p in players) or 1
    for rank, player in enumerate(players):
        share = player["minutes"] / total
        minutes = player["minutes"]
        role = "Core Starter" if rank < 11 else ("Starter / Rotation" if minutes >= 200 else "Rotation / Squad Member")
        if share >= 0.10:
            quality = "high"
        elif share >= 0.05:
            quality = "medium"
        else:
            quality = "low"
        if role == "Core Starter":
            pedigree = "senior option"
        elif role == "Starter / Rotation" and minutes >= 200:
            pedigree = "senior option"
        else:
            pedigree = "limited minutes"
        player["role"] = role
        player["quality"] = quality
        player["pedigree"] = pedigree
        player["load_profile"] = "high" if minutes >= 300 else "medium"
        player["injury_risk"] = "low-medium"
        player["low_minutes"] = role == "Rotation / Squad Member" and minutes < 120
        player["fits"] = _POS_FITS.get(player["position"], [])
    return players


def sync_dossier(season="2627"):
    sd = _soccerdata()
    if sd is None:
        print("soccerdata not installed - install with: pip install soccerdata")
        return None
    code = _season_code(season)
    dossier_data = dossier.load_dossier()
    print(f"Fetching FBref La Liga {code} squad...")
    fbref = sd.FBref(leagues="ESP-La Liga", seasons=code)
    player_stats = fbref.read_player_season_stats(stat_type="standard")
    subset = _load_atletico(player_stats, [])
    if subset is None or subset.empty:
        print("No Atlético Madrid data found for the requested season.")
        return None

    players = []
    for idx, row in subset.iterrows():
        label = idx[-1] if isinstance(idx, tuple) else idx
        players.append(_enrich(row, label))

    players.sort(key=lambda p: (p["minutes"], p["matches_played"]), reverse=True)
    players = _tier(players)
    dossier_data["season"] = f"20{code[0:2]}/{code[2:4]}"
    dossier_data["data_season"] = f"FBref {code[0:2]}-{code[2:4]}"
    dossier_data["players"] = players
    dossier.regenerate_constraints(dossier_data)
    dossier.save_dossier(dossier_data)
    print(f"Synced {len(players)} players into dossiers/atletico_madrid.json")
    return players