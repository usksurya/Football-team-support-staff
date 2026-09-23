from . import analytics
from . import data
from . import dossier


def compute_metrics():
    df = data.results_df()
    aliases = data.our_aliases()
    hist = analytics.history(df, aliases)
    gts = data.goals_time_df()
    prof = analytics.minute_profiles(gts, data.is_us_team) if not gts.empty else {}
    subs = analytics.substitution_windows(data.goals_time2_matches())

    peak_scored = analytics._peak_window(prof.get("scoring_bins", {}))
    peak_conceded = analytics._peak_window(prof.get("conceding_bins", {}))
    return {
        "dataset_matches_analyzed": hist["matches"],
        "historical_win_rate_pct": hist["win_rate_pct"],
        "data_span": f"{hist['first_date']} to {hist['last_date']}",
        "goals_for_against": f"{hist['goals_for']}-{hist['goals_against']}",
        "peak_scoring_window": f"peak {peak_scored}",
        "peak_conceded_window": f"peak {peak_conceded}",
        "conceded_share_75_90_pct": prof.get("share_conceded_75_90"),
        "recommended_sub_windows": subs["recommended"] if subs else [],
        "substitution_events": subs["total"] if subs else 0,
        "source": "results/games.parquet (1888-2025) + goals_time (La Liga/CL/EL) + goals_time2 (La Liga match incidents)",
    }


def refresh_dossier():
    dossier_data = dossier.load_dossier()
    metrics = compute_metrics()
    dossier_data["dataset_validation_metrics"] = metrics
    dossier.regenerate_constraints(dossier_data)
    dossier.save_dossier(dossier_data)
    return metrics