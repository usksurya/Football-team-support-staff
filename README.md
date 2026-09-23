# Atlético Madrid Staff & Scouting Toolkit

A Python CLI package (`ateli`) that turns dataset and FBref squad data into operational staff outputs: match briefs, scouting reports, dataset metrics, and a full squad roster table.

---

## Quick‑start (Windows CMD)

```cmd
cd "C:\Users\kiran\OneDrive\Desktop\atletico madrid"
call ".venv\Scripts\python.exe" -m ateli sync --season 2627
call ".venv\Scripts\python.exe" -m ateli metrics
call ".venv\Scripts\python.exe" -m ateli scout "Barcelona"
call ".venv\Scripts\python.exe" -m ateli brief --opponent "Real Madrid" --out
call ".venv\Scripts\python.exe" -m ateli report
call ".venv\Scripts\python.exe" -m ateli squad
```

> **Important**: The `call` prefix is required in CMD because `&` and `|` are command separators even inside quotes. Using `call` before the python invocations avoids silent failures.

---

## Commands reference

| Command | What it does | Output |
| --- | --- | --- |
| `ateli sync --season 2627` | Pull FBref La Liga 2026/27 squad into `dossiers/atletico_madrid.json`. Enriches players with tiered roles (Core Starter / Starter‑Rotation / Rotation), quality, pedigree, `low_minutes` flag, and `team_constraints`. | Console log: `Synced N players.` |
| `ateli metrics` | Re‑compute dataset validation metrics into the dossier. Prints: matches analysed, win‑rate, data span, goals for/against, peak scoring/conceded windows, conceded‑share 75‑90 %, recommended substitution windows, substitution‑event count, data source. | Console output (see example below). |
| `ateli scout "TeamName"` | Generate a scouting report for the opponent. Resolves team‑name disambiguation (e.g. “Barcelona” → FC Barcelona, not Dominican Barcelona). Prints profile, record, goals/conceding timing, head‑to‑head vs Atlético, last matches, trends. | Text printed to console; `--out` flag writes `reports/scout_*.md`. |
| `ateli brief --opponent "TeamName" --out` | Produce a full staff match‑brief `reports/brief_vs_*.md`. Sections: executive summary, opponent model, head‑to‑head, our squad state, historical windows, recommended approach, risks & mitigations. | Markdown file saved to `reports/`. |
| `ateli report` | One‑page club dossier summary: club/season, player count, Core Starter count, breakdown by position & quality, injury‑risk flags, primary risk from `team_constraints`, dataset metrics table. | Console output. |
| `ateli squad` **(new)** | Print the full enriched roster from the dossier in a table with columns for Name, Pos, Role, Quality, Minutes, Matches, LowMin, and Fits. Useful for staff to see every player’s attributes at a glance. | Console table. |

*All commands are run from the project root `C:\Users\kiran\OneDrive\Desktop\atletico madrid`.*

---

## Data sources (read‑only)

| Source | Contents | Notes |
| --- | --- | --- |
| `results/games.parquet` | ~1.31 M rows, seasons 1888‑2025‑09‑21. Team names contain mojibake (e.g. `Atl�tico Madrid`). Team names are **not** unique across the dataset (≈66 “Atletico*” clubs worldwide). | Used for historical metrics, H2H, minute profiles. |
| `goals_time/*.csv` (esp‑primera‑division, champions‑league, europa‑league) | Per‑goal rows: scoring player, team, time, GH, GA, game, date, season. Team names double‑encoded (e.g. `AtlÃ©tico`). Covers up to 2024‑25 season. | 52 131 goals across the 3 CSVs. |
| `goals_time2/*.json` (spanien_la‑liga‑*.json) | Per‑match incidents including substitutions; our slug is `atletico-madrid`. 2 581 our‑sub events. | Used for substitution‑window analysis. |
| `elo/elo.parquet` (mis‑named CSV) | Team dictionary – not actively used in the tool. | – |
| `dossiers/atletico_madrid.json` | **Single source of truth** for the current squad: 23 players for 2026/27, enriched roles/quality/pedigree/low_minutes, `team_constraints`, `dataset_validation_metrics`. | Written/updated by `ateli sync`. |
| `.venv` | Python 3.12.4; dependencies: pandas 3.0.5, pyarrow 25.0.1, soccerdata 1.9.1. | Activate/virtual‑env used by all CLI commands. |

---

## Known quirks ( Windows / console )

- **Mojibake display**: The console font may show `�` for é/em‑dash/en‑dash, but **files are correct UTF‑8**. Do not “fix” files based on console output.
- **`call` prefix**: In CMD, always use `call ".venv\Scripts\python.exe" -m ateli …`. Without `ampersands` & pipes may split commands unexpectedly.
- **Team‑name disambiguation**: “Barcelona” resolves to **FC Barcelona** via a count‑then‑rank strategy in `names.py`. The dataset contains multiple clubs named “Barcelona” (including a Dominican side).
- **Early‑season snapshot** (2026/27, mid‑September): only ~6‑7 matches played, so minutes‑based role thresholds (Core Starter = top 11 by minutes) are relative to the current squad, not a full‑season fixed cutoff.

---

## Project structure (top‑level)

```text
atletico madrid/
│
├─ ateli/                       # Python package
│   ├─ __init__.py
│   ├─ __main__.py
│   ├─ cli.py                   # argparse entry‑point (sync, metrics, scout, brief, report, squad)
│   ├─ data.py                  # team‑name resolution, results df, aliases
│   ├─ names.py                 # prominence‑based disambiguation (count, rank)
│   ├─ analytics.py             # minute profiles, H2H, opponent profiles, substitution windows
│   ├─ dossier.py               # load/save dossier, squad summary, constraint regeneration
│   ├─ metrics.py               # refresh dataset_validation_metrics from parquet/CSVs
│   ├─ report.py                # scout_report(), staff_brief(), _fmt_positions()
│   └─ sync_squad.py            # sync_dossier() – FBref sync via soccerdata, _enrich(), _tier()
│
├─ dossiers/
│   └─ atletico_madrid.json     # current squad + constraints + metrics (sync‑generated)
│
├─ football-data/
│   └─ data/                    # parquet, CSVs, JSON (read‑only inputs)
│
├─ reports/                     # generated markdown briefs & scout reports
│
├─ .opencode/
│   ├─ agent/                   # specialist agent markdown files (tactical analyst, scout, etc.)
│   └─ command/                 # /match‑prep orchestrator
│
├─ requirements.txt             # pandas, pyarrow, soccerdata
│
├─ README.md                    # ← this file
│
└─ .venv/                       # Python virtual environment
```

---

## How to add a new agent (optional)

1. Create `C:\Users\kiran\OneDrive\Desktop\atletico madrid\.opencode\agent\<name>.md` using the template below.
2. The agent is automatically available from the chat: `> Atletico <name> <your question>`.
3. (Optional) Add the agent to `/match‑prep`’s allocation list in `.opencode\command\match‑prep.md`.

### Minimal agent template

```markdown
---
description: "<one‑sentence purpose>"
name: "<Agent Display Name>"
mode: subagent
---

You are the <role> for Atlético Madrid.

**Data source:** the dossier at `dossiers/atletico_madrid.json` (and/or the `ateli` data functions).

**Task:** <step‑by‑step instructions, e.g. "Filter players where low_minutes is true and minutes < 300. Return a markdown table: Name | Pos | Role | Quality | Minutes | Fits">

**Output format:** <what to return, e.g. "Always start with a one‑sentence summary, then a markdown table, then a short mitigation note.">

**Guardrails:** <any "must‑not‑do" rules, e.g. "Never bench a Core Starter without an emergency clause">
```

---

## Need help?

- Run `python -m ateli --help` (inside the venv) for a full list of CLI options.
- Open `dossiers/atletico_madrid.json` in VS Code/Notepad to inspect the current squad JSON structure.
- All generated reports land in `reports/` and can be read/edited like any Markdown file.

---

*Built for team staff and scouts. Developed with ❤️ in the Windows‑CMD / VS Code environment.*
