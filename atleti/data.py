import glob
import json
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

from . import names

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "football-data" / "data"
RESULTS_FILE = DATA_DIR / "results" / "games.parquet"
GOALS_TIME_DIR = DATA_DIR / "goals_time"
GOALS_TIME2_DIR = DATA_DIR / "goals_time2"

OUR_QUERY = "Atletico Madrid"

_RE_GAME = re.compile(r"^(.*?) vs\. (.*?) (\d+):(\d+)$")


def results_df():
    df = pd.read_parquet(RESULTS_FILE)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["home_s"] = df["home"].astype(str)
    df["away_s"] = df["away"].astype(str)
    df["gh"] = pd.to_numeric(df["gh"], errors="coerce")
    df["ga"] = pd.to_numeric(df["ga"], errors="coerce")
    return df


@lru_cache(maxsize=1)
def results_index():
    df = results_df()
    first = df.groupby("home_s")["date"].first().to_dict()
    first.update(df.groupby("away_s")["date"].first().to_dict())
    last = df.groupby("home_s")["date"].max().to_dict()
    last.update(df.groupby("away_s")["date"].max().to_dict())
    for key in set(first) & set(last):
        if key == "nan":
            first.pop(key, None)
            last.pop(key, None)
    return first, last


@lru_cache(maxsize=1)
def team_names():
    df = results_df()
    return set(df["home_s"].unique()) | set(df["away_s"].unique())


@lru_cache(maxsize=1)
def team_counts():
    df = results_df()
    counts = df["home_s"].value_counts().to_dict()
    for name, value in df["away_s"].value_counts().to_dict().items():
        counts[name] = counts.get(name, 0) + value
    return counts


def resolve_team(query, k=3):
    names_ = team_names()
    _, last = results_index()
    return names.resolve_team(names_, last, query, counts=team_counts(), k=k)


def club_aliases(query):
    names_ = team_names()
    _, last = results_index()
    return names.club_aliases(names_, last, team_counts(), query)


@lru_cache(maxsize=1)
def our_primary():
    hits = resolve_team("Atletico Madrid", k=1)
    if hits:
        return hits[0]
    cands = resolve_team("Atletico", k=10)
    if cands:
        return cands[0]
    return None


def our_aliases():
    return club_aliases(OUR_QUERY)


def is_us_team(name):
    return names.is_named(name, names.variants(OUR_QUERY))


def goals_time_df():
    frames = []
    for fname in (
        "esp-primera-division.csv",
        "champions-league.csv",
        "europa-league.csv",
    ):
        path = GOALS_TIME_DIR / fname
        if not path.exists():
            continue
        frame = pd.read_csv(path, encoding="utf-8")
        frame["competition"] = fname[:-4]
        frame["time"] = pd.to_numeric(frame["time"], errors="coerce")
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def goals_time2_matches():
    matches = []
    for path in sorted(glob.glob(str(GOALS_TIME2_DIR / "*.json"))):
        season = Path(path).stem
        try:
            data = json.load(open(path, encoding="utf-8", errors="replace"))
        except Exception:
            continue
        for match in data:
            match["_season"] = season
            matches.append(match)
    return matches


def parse_game(game):
    if game is None:
        return None
    match = _RE_GAME.match(str(game))
    if not match:
        return None
    home, away, hs, as_ = match.groups()
    return home.strip(), away.strip(), int(hs), int(as_)