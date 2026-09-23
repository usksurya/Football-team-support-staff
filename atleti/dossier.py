import json
from pathlib import Path

DOSSIERS_DIR = Path(__file__).resolve().parent.parent / "dossiers"
DOSSIER_PATH = DOSSIERS_DIR / "atletico_madrid.json"


def load_dossier(path=None):
    target = Path(path) if path else DOSSIER_PATH
    with open(target, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_dossier(dossier, path=None):
    target = Path(path) if path else DOSSIER_PATH
    with open(target, "w", encoding="utf-8") as handle:
        json.dump(dossier, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def squad_summary(dossier):
    players = dossier.get("players", [])
    positions = {}
    roles = {}
    quality = {}
    risks = [p["name"] for p in players if p.get("injury_risk") in ("medium", "medium-high", "high")]
    for player in players:
        pos = player.get("position", "Unknown")
        positions[pos] = positions.get(pos, 0) + 1
        role = player.get("role", "?")
        roles[role] = roles.get(role, 0) + 1
        qual = player.get("quality", "?")
        quality[qual] = quality.get(qual, 0) + 1
    return {
        "player_count": len(players),
        "by_position": dict(sorted(positions.items())),
        "by_role": dict(sorted(roles.items())),
        "by_quality": dict(sorted(quality.items())),
        "injury_risk_flags": risks,
    }


def senior_center_backs(players):
    cbs = []
    fringe = []
    for player in players:
        pos = str(player.get("position", ""))
        if pos != "DF":
            continue
        minutes = float(player.get("minutes", 0) or 0)
        if player.get("role") in ("Core Starter", "Starter / Rotation") or minutes >= 200:
            cbs.append(player["name"])
        elif player.get("role") or player.get("minutes") is not None:
            fringe.append(player["name"])
    return cbs, fringe


def regenerate_constraints(dossier):
    players = dossier.get("players", [])
    cbs, fringe = senior_center_backs(players)
    starters = [p for p in players if p.get("role") == "Core Starter"]
    if len(cbs) < 4:
        depth = (
            f"Only {len(cbs)} centre-back options with meaningful minutes available "
            f"({', '.join(cbs) or 'none'})" + (f" plus depth: {', '.join(fringe)}" if fringe else "") +
            " - central defensive depth is the key structural risk."
        )
    else:
        depth = (
            f"{len(cbs)} centre-back options with meaningful minutes "
            f"({', '.join(cbs)}) - central depth is workable."
        )
    dossier["team_constraints"] = {
        "primary_risk": depth,
        "rotation_priority": "Protect central defensive and goalkeeper depth while rotating midfield and wide attackers.",
        "tactical_priority": "Maintain shape integrity without compromising wide balance and transition security.",
        "bench_note": f"Last sync produced {len(players)} players; {len(starters)} are flagged Core Starters.",
    }
    return dossier