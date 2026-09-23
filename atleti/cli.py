import argparse
import datetime as dt
import sys

from . import analytics
from . import data
from . import dossier
from . import metrics
from . import report
from . import sync_squad

__version__ = "1.0.0"


def _our_windows():
    gts = data.goals_time_df()
    our_prof = analytics.minute_profiles(gts, data.is_us_team) if not gts.empty else None
    subs = analytics.substitution_windows(data.goals_time2_matches())
    return our_prof, subs


def cmd_sync(args):
    players = sync_squad.sync_dossier(season=args.season)
    if players is None:
        sys.exit(1)
    print(f"Synced {len(players)} players.")


def cmd_metrics(args):
    updated = metrics.refresh_dossier()
    print("Updated dossiers/atletico_madrid.json dataset_validation_metrics:")
    for key, value in updated.items():
        print(f"  {key}: {value}")


def cmd_scout(args):
    candidates = data.resolve_team(args.team, k=1)
    if not candidates:
        print(f"No match found for '{args.team}' in the dataset.")
        sys.exit(1)
    opp_label = candidates[0]
    df = data.results_df()
    opp_profile, resolved = analytics.opponent_profile(df, args.team, recent=args.recent)
    if opp_profile is None:
        print(f"No records found for '{args.team}'.")
        sys.exit(1)
    for_check = [opp_label]
    if resolved and resolved != opp_label:
        opp_label = resolved
    our = data.our_aliases()
    h2h = analytics.head_to_head(df, our, [opp_label])
    gts = data.goals_time_df()
    since = None
    window_end = opp_profile.get("window_end")
    if window_end:
        try:
            end = dt.date.fromisoformat(window_end)
            since = (end - dt.timedelta(days=365 * 3)).isoformat()
        except ValueError:
            since = None
    opp_goals = analytics.minute_profiles(gts, lambda t: data.names.is_named(t, data.names.variants(opp_label)), since=since) if not gts.empty else None
    text = report.scout_report(opp_label, [opp_label], opp_profile, h2h, opp_goals)
    print(text)
    if args.out:
        path = report.save_report(text, f"scout_{data.names.fold(args.team)}.md")
        print(f"\nSaved to {path}")


def cmd_brief(args):
    candidates = data.resolve_team(args.opponent, k=1)
    if not candidates:
        print(f"No match found for opponent '{args.opponent}'.")
        sys.exit(1)
    df = data.results_df()
    opp_profile, resolved = analytics.opponent_profile(df, args.opponent, recent=args.recent)
    if opp_profile is None:
        print(f"No records found for '{args.opponent}'.")
        sys.exit(1)
    opp_label = resolved if resolved else candidates[0]
    our = data.our_aliases()
    our_hist = analytics.history(df, our)
    h2h = analytics.head_to_head(df, our, [opp_label])
    our_prof, subs = _our_windows()
    dossier_data = dossier.load_dossier()
    text = report.staff_brief(dossier_data, opp_label, opp_profile, [opp_label], h2h, our_hist, our_prof, subs)
    print(text)
    if args.out:
        path = report.save_report(text, f"brief_vs_{data.names.fold(args.opponent)}.md")
        print(f"\nSaved to {path}")


def cmd_report(args):
    dossier_data = dossier.load_dossier()
    summary = dossier.squad_summary(dossier_data)
    constraints = dossier_data.get("team_constraints", {})
    print(f"Club: {dossier_data.get('club')} | Season: {dossier_data.get('season')}")
    print(f"Players: {summary['player_count']} | Starters: {summary['by_role'].get('Core Starter', 0)}")
    print(f"By position: {report._fmt_positions(summary['by_position'])}")
    print(f"By quality: {summary['by_quality']}")
    print(f"Injury risk flags: {', '.join(summary['injury_risk_flags']) or 'none'}")
    print(f"Primary risk: {constraints.get('primary_risk', 'n/a')}")
    metrics_block = dossier_data.get("dataset_validation_metrics", {})
    if metrics_block:
        print("\nDataset metrics:")
        for key, value in metrics_block.items():
            print(f"  {key}: {value}")
    if args.refresh:
        metrics.refresh_dossier()
        print("\nRefreshed dataset metrics from local datasets.")


def cmd_squad(args):
    dossier_data = dossier.load_dossier()
    players = dossier_data.get("players", [])
    print(f"Club: {dossier_data.get('club')} | Season: {dossier_data.get('season')}")
    print(f"{'Name':<20} {'Pos':<6} {'Role':<16} {'Quality':<10} {'Minutes':<8} {'Matches':<8} {'LowMin':<6} {'Fits'}")
    for p in players:
        name = p.get("name", "")
        pos = p.get("position", "")
        role = p.get("role", "")
        quality = p.get("quality", "")
        minutes = p.get("minutes", 0)
        matches = p.get("matches_played", 0)
        low_min = "yes" if p.get("low_minutes") else "no"
        fits = ", ".join(p.get("fits", []))[:30]
        print(f"{name:<20} {pos:<6} {role:<16} {quality:<10} {minutes:<8} {matches:<8} {low_min:<6} {fits}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ateli",
        description="Atlético Madrid staff & scouting toolkit - dossier, dataset analytics, match briefs.",
    )
    parser.add_argument("--version", action="version", version=f"ateli {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="Pull the current FBref squad into the dossier.")
    p_sync.add_argument("--season", default="2627", help="Season notation (e.g. 2627 or 2026-27).")
    p_sync.set_defaults(func=cmd_sync)

    p_metrics = sub.add_parser("metrics", help="Recompute dataset validation metrics into the dossier.")
    p_metrics.set_defaults(func=cmd_metrics)

    p_scout = sub.add_parser("scout", help="Generate an opponent scouting report.")
    p_scout.add_argument("team", help="Opponent display name (e.g. 'Real Madrid').")
    p_scout.add_argument("--recent", type=int, default=25, help="Recent window size.")
    p_scout.add_argument("--out", action="store_true", help="Write report to reports/.")
    p_scout.set_defaults(func=cmd_scout)

    p_brief = sub.add_parser("brief", help="Generate a staff match brief for an opponent.")
    p_brief.add_argument("--opponent", required=True, help="Opponent display name (e.g. 'Real Madrid').")
    p_brief.add_argument("--recent", type=int, default=25, help="Recent window size.")
    p_brief.add_argument("--out", action="store_true", help="Write report to reports/.")
    p_brief.set_defaults(func=cmd_brief)

    p_rep = sub.add_parser("report", help="Print current squad state and dossier metrics.")
    p_rep.add_argument("--refresh", action="store_true", help="Refresh metrics from datasets first.")
    p_rep.set_defaults(func=cmd_report)

    p_squad = sub.add_parser("squad", help="Print current squad state from dossier with full player details.")
    p_squad.set_defaults(func=cmd_squad)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()