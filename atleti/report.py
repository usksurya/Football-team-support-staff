from . import analytics
from . import data
from . import dossier


def _fmt_bin(bins):
    if not bins:
        return "no data"
    ordered = sorted(bins.items(), key=lambda kv: int(kv[0].split("'")[0]))
    return ", ".join(f"{label} ({n})" for label, n in ordered)


def staff_brief(dossier_data, opp_label, opp_profile, opp_aliases, h2h, our_hist, our_prof, subs, opp_prof_goals=None):
    lines = []
    lines.append(f"# Staff Match Brief — Atlético de Madrid vs {opp_label}")
    lines.append("")
    lines.append(f"*Generated from local dataset (results 1888-2025, FBref roster {dossier_data.get('data_season', dossier_data.get('season', 'n/a'))})*")
    lines.append("")

    lines.append("## 1. Executive summary")
    opp_win = opp_profile["win_rate_pct"]
    form_o = opp_profile["form_last"]
    our_win = our_hist["win_rate_pct"]
    peak_c = our_prof.get("peak_conceded_window", "n/a") if our_prof else "n/a"
    notes = _notes(dossier_data, opp_profile, our_prof)
    lines.append(f"- {opp_label} enter with form **{form_o}** ({opp_win}% win rate, {opp_profile['matches']} games in window).")
    lines.append(f"- We sit at a {our_win}% all-time win rate; primary defensive danger window is around the **{peak_c}** mark.")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## 2. Opponent model (dataset)")
    lines.append(f"- Aliases matched: {', '.join(opp_aliases)}")
    lines.append(f"- Recent window: {opp_profile['matches']} matches, W/D/L **{opp_profile['wins']}/{opp_profile['draws']}/{opp_profile['losses']}** ({opp_win}% wins)")
    lines.append(f"- Goals: {opp_profile['goals_for']} for / {opp_profile['goals_against']} against (avg {opp_profile['avg_gf']} - {opp_profile['avg_ga']})")
    lines.append(f"- Home: {opp_profile['home_matches']} games ({opp_profile['home_gf']}-{opp_profile['home_ga']}) | Away: {opp_profile['away_matches']} ({opp_profile['away_gf']}-{opp_profile['away_ga']})")
    lines.append(f"- Strength index (goal diff): **{analytics.strength_index(opp_profile)}** | PPG last {25}: **{opp_profile['ppg_recent']}**")
    top_comp = list(opp_profile["competitions"].items())[:3]
    lines.append(f"- Main competitions: {', '.join(f'{k} ({v})' for k, v in top_comp)}")
    lines.append("- Last results:")
    for m in opp_profile["last_matches"]:
        lines.append(f"  - {m['date']} {m['competition']}: {m['home']} {m['gf']}-{m['ga']} {m['away']} ({m['result']})")
    lines.append("")

    if h2h:
        lines.append("## 3. Head-to-head")
        lines.append(f"- {h2h['played']} prior meetings, W/D/L **{h2h['wins']}/{h2h['draws']}/{h2h['losses']}** ({h2h['win_rate_pct']}% for us), {h2h['first_date']} to {h2h['last_date']}.")
        lines.append("- Recent:")
        for m in h2h["matches"][-5:]:
            lines.append(f"  - {m['date']} {m['competition']}: {m['home']} {m['gf']}-{m['ga']} {m['away']} ({m['result']})")
        lines.append("")

    lines.append("## 4. Our squad state (dossier)")
    summary = dossier.squad_summary(dossier_data)
    lines.append(f"- Squad size: **{summary['player_count']}** | Core Starters: {summary['by_role'].get('Core Starter', 0)}")
    lines.append(f"- By position: {_fmt_positions(summary['by_position'])}")
    lines.append(f"- Injury-risk flags: {', '.join(summary['injury_risk_flags']) or 'none flagged'}")
    constraints = dossier_data.get("team_constraints", {})
    if constraints.get("primary_risk"):
        lines.append(f"- Structural risk: {constraints['primary_risk']}")
        lines.append(f"- Rotation priority: {constraints.get('rotation_priority', 'n/a')}")
    lines.append("")

    if our_prof:
        lines.append("## 5. Historical windows (dataset-derived)")
        lines.append(f"- Goals scored minute profile: {_fmt_bin(our_prof.get('scoring_bins', {}))}")
        lines.append(f"- Goals conceded minute profile: {_fmt_bin(our_prof.get('conceding_bins', {}))}")
        lines.append(f"- We concede {our_prof.get('share_conceded_75_90', 0)}% of goals after the 75th minute (avg concede {our_prof.get('avg_minute_conceded', 'n/a')}').")
    if subs:
        lines.append(f"- Typical substitution windows (from {subs['total']} past sub events): {', '.join(subs['recommended'])}")
    lines.append("")

    lines.append("## 6. Recommended approach")
    lines.append("- Compress blocking early if we concede space late; prioritise maintaining compactness through the final quarter.")
    lines.append(f"- Use the {peak_c} band as an alert phase - bank possession or refresh wide units before that stretch if possible.")
    if subs:
        lines.append(f"- Consider planning first rotation around {subs['recommended'][0]} using available bench profiles (see dossier).")
    lines.append("- Honour the senior centre-back rotation rule in `team_constraints`; no core starter is benched without an emergency trigger (from dossier workflow).")
    lines.append("")

    lines.append("## 7. Risks & mitigations")
    lines.append("- Key risk: late-game leakage + opponent transition speed (if their scoring window is early).")
    lines.append("- Mitigation: pre-emptive sub management in the identified windows; keep a senior CB on the bench per `team_constraints`.")
    lines.append("")
    return "\n".join(lines)


def _fmt_positions(pos_map):
    return ", ".join(f"{k} {v}" for k, v in sorted(pos_map.items()))


def _notes(dossier_data, opp_profile, our_prof):
    notes = []
    depth = dossier_data.get("team_constraints", {}).get("primary_risk", "")
    if opp_profile["avg_gf"] >= 1.9:
        notes.append(f"Opponent carry an attacking profile ({opp_profile['avg_gf']} GF/game) - central/depth discipline is critical.")
    if our_prof and our_prof.get("share_conceded_75_90", 0) >= 25:
        notes.append("Our late-game conceding share is high - schedule monitoring during the final quarter.")
    if "centre-back" in depth.lower():
        notes.append("Senior centre-back depth is the limiting factor - protect it in selection.")
    if not notes:
        notes.append("No single overriding risk flag in the current data; maintain standard compactness and rotation discipline.")
    return notes[:3]


def scout_report(opp_label, opp_aliases, opp_profile, h2h, opp_goals=None):
    lines = []
    lines.append(f"# Scouting Report — {opp_label}")
    lines.append("")
    lines.append(f"*Aliases matched in dataset: {', '.join(opp_aliases)}*")
    lines.append("")
    lines.append("## Profile")
    lines.append(f"- Recent form: **{opp_profile['form_last']}** (window = {opp_profile['matches']} matches)")
    lines.append(f"- Record: W/D/L **{opp_profile['wins']}/{opp_profile['draws']}/{opp_profile['losses']}** ({opp_profile['win_rate_pct']}% wins)")
    lines.append(f"- Goals: {opp_profile['goals_for']} for / {opp_profile['goals_against']} against; avg {opp_profile['avg_gf']} - {opp_profile['avg_ga']}")
    lines.append(f"- PPG (last {25}): {opp_profile['ppg_recent']} | Strength index: {analytics.strength_index(opp_profile)}")
    lines.append(f"- Home: {opp_profile['home_gf']}-{opp_profile['home_ga']} in {opp_profile['home_matches']} | Away: {opp_profile['away_gf']}-{opp_profile['away_ga']} in {opp_profile['away_matches']}")
    lines.append("")

    if opp_goals:
        lines.append("## Scoring / conceding timing")
        lines.append(f"- Scores in: {_fmt_bin(opp_goals.get('scoring_bins', {}))}")
        lines.append(f"- Concedes in: {_fmt_bin(opp_goals.get('conceding_bins', {}))}")
        lines.append("")

    if h2h:
        lines.append("## Head-to-head vs Atlético de Madrid")
        lines.append(f"- Meetings: {h2h['played']} | W/D/L us **{h2h['wins']}/{h2h['draws']}/{h2h['losses']}** (us win {h2h['win_rate_pct']}%)")
        lines.append("- Recent:")
        for m in h2h["matches"][-5:]:
            lines.append(f"  - {m['date']} {m['competition']}: {m['home']} {m['gf']}-{m['ga']} {m['away']} ({m['result']})")
        lines.append("")

    lines.append("## Last matches")
    for m in opp_profile["last_matches"][-8:]:
        lines.append(f"- {m['date']} {m['competition']}: {m['home']} {m['gf']}-{m['ga']} {m['away']} ({m['result']})")
    lines.append("")
    lines.append("## Trends for planning")
    lines.append(f"- Their wins come in {opp_profile['win_rate_pct']}% of recent games.")
    lines.append("- Maintain a compact block and protect the final quarter per our conceded distribution.")
    lines.append("")
    return "\n".join(lines)


def save_report(text, name):
    out_dir = dossier.DOSSIERS_DIR.parent / "reports"
    out_dir.mkdir(exist_ok=True)
    path = out_dir / name
    path.write_text(text, encoding="utf-8")
    return path