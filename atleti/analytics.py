from . import data

BIN_SIZE = 15


def _result(row, us):
    if row.gh > row.ga:
        return "W" if us == "home" else "L"
    if row.gh < row.ga:
        return "W" if us == "away" else "L"
    return "D"


def _score(row, us):
    if us == "home":
        return row.gh, row.ga
    return row.ga, row.gh


def _select(df, aliases):
    mask = df["home_s"].isin(aliases) | df["away_s"].isin(aliases)
    out = df[mask].copy()
    out["us_pos"] = out["home_s"].isin(aliases).map({True: "home", False: "away"})
    return out


def history(results, aliases, window=25, form_games=10):
    df = _select(results, aliases).sort_values("date")
    if df.empty:
        return None
    rows = []
    for _, row in df.iterrows():
        f, a = _score(row, row.us_pos)
        rows.append((row["date"], row["competition"], row["home_s"], row["away_s"], f, a, _result(row, row.us_pos)))
    wins = sum(1 for r in rows if r[6] == "W")
    draws = sum(1 for r in rows if r[6] == "D")
    losses = sum(1 for r in rows if r[6] == "L")
    gf = sum(r[4] for r in rows)
    ga = sum(r[5] for r in rows)
    home = [(r[4], r[5]) for r in rows if r[2] in aliases]
    away = [(r[4], r[5]) for r in rows if r[3] in aliases]
    rec = rows[-form_games:]
    recent = [r[6] for r in rec]

    def pts(res):
        return 3 if res == "W" else (1 if res == "D" else 0)

    ppg_window = rows[-window:]
    ppg = round(sum(pts(r[6]) for r in ppg_window) / len(ppg_window), 3) if ppg_window else 0
    window_start = str(ppg_window[0][0].date()) if ppg_window else ""
    window_end = str(ppg_window[-1][0].date()) if ppg_window else ""
    comps = {}
    for r in rows:
        comps[r[1]] = comps.get(r[1], 0) + 1
    last = rows[-8:]
    return {
        "matches": len(rows),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate_pct": round(wins / len(rows) * 100, 1),
        "goals_for": gf,
        "goals_against": ga,
        "avg_gf": round(gf / len(rows), 2),
        "avg_ga": round(ga / len(rows), 2),
        "home_matches": len(home),
        "home_gf": sum(x[0] for x in home),
        "home_ga": sum(x[1] for x in home),
        "away_matches": len(away),
        "away_gf": sum(x[0] for x in away),
        "away_ga": sum(x[1] for x in away),
        "form_last": "".join(recent),
        "ppg_recent": ppg,
        "no_goal_games": sum(1 for r in rows if r[4] == 0),
        "clean_sheets": sum(1 for r in rows if r[5] == 0),
        "first_date": str(rows[0][0].date()),
        "last_date": str(rows[-1][0].date()),
        "window_start": window_start,
        "window_end": window_end,
        "competitions": dict(sorted(comps.items(), key=lambda x: -x[1])),
        "last_matches": [
            {
                "date": str(r[0].date()),
                "competition": r[1],
                "home": r[2],
                "away": r[3],
                "gf": r[4],
                "ga": r[5],
                "result": r[6],
            }
            for r in last
        ],
    }


def opponent_profile(results, opp_query, recent=25, form_games=8):
    resolved = data.resolve_team(opp_query, k=1)
    if not resolved:
        return None, None
    primary = resolved[0]
    df = _select(results, [primary]).sort_values("date")
    if df.empty:
        return None, primary
    recent_df = df.tail(recent)
    prof = history(recent_df, [primary], window=recent, form_games=form_games)
    return prof, primary


def head_to_head(results, us_aliases, opp_aliases, recent=20):
    mask = (
        (results["home_s"].isin(us_aliases) & results["away_s"].isin(opp_aliases))
        | (results["home_s"].isin(opp_aliases) & results["away_s"].isin(us_aliases))
    )
    df = results[mask].sort_values("date")
    if df.empty:
        return None
    rows = []
    for _, row in df.iterrows():
        if row.home_s in us_aliases and row.away_s in opp_aliases:
            us, opp = "home", "away"
        else:
            us, opp = "away", "home"
        f, a = _score(row, us)
        rows.append((row.date, row.competition, row.home_s, row.away_s, f, a, _result(row, us)))
    rows = rows[-recent:]
    wins = sum(1 for r in rows if r[6] == "W")
    draws = sum(1 for r in rows if r[6] == "D")
    losses = sum(1 for r in rows if r[6] == "L")
    return {
        "played": len(rows),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate_pct": round(wins / len(rows) * 100, 1) if rows else 0,
        "first_date": str(rows[0][0].date()) if rows else "",
        "last_date": str(rows[-1][0].date()) if rows else "",
        "matches": [
            {
                "date": str(r[0].date()),
                "competition": r[1],
                "home": r[2],
                "away": r[3],
                "gf": r[4],
                "ga": r[5],
                "result": r[6],
            }
            for r in rows
        ],
    }


def _minute_series(goals_df, is_us_side, since=None):
    import pandas as _pd

    scored, conceded = [], []
    if since is not None and "date" in goals_df.columns:
        goals_df = goals_df[_pd.to_datetime(goals_df["date"], errors="coerce") >= since]
    for _, row in goals_df.iterrows():
        parsed = data.parse_game(row.get("game"))
        if not parsed:
            continue
        home, away, _, _ = parsed
        if is_us_side(home) or is_us_side(away):
            minute = row["time"]
            if not _pd.notna(minute):
                continue
            minute = min(int(minute), 90)
            if is_us_side(row.get("scoring_team")):
                scored.append(minute)
            else:
                conceded.append(minute)
    return scored, conceded


def _bins(minutes):
    if not minutes:
        return {}
    out = {}
    for m in minutes:
        edge = (m // BIN_SIZE) * BIN_SIZE
        label = f"{edge}'–{edge + BIN_SIZE - 1}'"
        out[label] = out.get(label, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0].split("'")[0])))


def _peak_window(bins, margin=3):
    if not bins:
        return "n/a"
    ordered = sorted(bins.items(), key=lambda kv: -kv[1])
    start = int(ordered[0][0].split("'")[0])
    return f"{start + margin}'"


def minute_profiles(goals_df, is_us_side, since=None):
    scored, conceded = _minute_series(goals_df, is_us_side, since)
    sb, cb = _bins(scored), _bins(conceded)
    profile = {
        "scoring_bins": sb,
        "conceding_bins": cb,
        "goals_scored": len(scored),
        "goals_conceded": len(conceded),
        "avg_minute_scored": round(sum(scored) / len(scored), 1) if scored else None,
        "avg_minute_conceded": round(sum(conceded) / len(conceded), 1) if conceded else None,
        "share_conceded_75_90": round(sum(v for k, v in cb.items() if int(k.split("'")[0]) >= 75) / len(conceded) * 100, 1) if conceded else None,
        "peak_scoring_window": _peak_window(sb),
        "peak_conceded_window": _peak_window(cb),
    }
    return profile


def substitution_windows(gt2_matches, limit=None):
    minutes = []
    for match in gt2_matches:
        if match.get("home") != "atletico-madrid" and match.get("away") != "atletico-madrid":
            continue
        side = "home" if match.get("home") == "atletico-madrid" else "away"
        for inc in match.get("incident", {}).get("incidents", []):
            if inc.get("incident_type") == "Substitution" and inc.get("team") == side:
                raw = str(inc.get("minute", ""))
                num = "".join(ch for ch in raw if ch.isdigit())
                if num:
                    minutes.append(min(int(num), 90))
    if not minutes:
        return None
    if limit:
        minutes = minutes[-limit:]
    bins = {}
    for m in minutes:
        edge = (m // BIN_SIZE) * BIN_SIZE
        label = f"{edge}–{edge + BIN_SIZE - 1}"
        bins[label] = bins.get(label, 0) + 1
    ordered = sorted(bins.items(), key=lambda kv: -kv[1])
    windows = [f"{int(k.split('–')[0])}'–{int(k.split('–')[1])}'" for k, _ in ordered[:3]]
    return {
        "total": len(minutes),
        "bins": dict(sorted(bins.items(), key=lambda kv: int(kv[0].split('–')[0]))),
        "recommended": windows,
        "median_minute": _median(minutes),
    }


def _median(values):
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return round((ordered[mid - 1] + ordered[mid]) / 2, 1)


def strength_index(profile):
    return round(profile["avg_gf"] - profile["avg_ga"], 2)