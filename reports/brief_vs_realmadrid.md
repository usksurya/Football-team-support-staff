# Staff Match Brief — Atlético de Madrid vs Real Madrid

*Generated from local dataset (results 1888-2025, FBref roster FBref 26-27)*

## 1. Executive summary
- Real Madrid enter with form **WWWWWWWW** (76.0% win rate, 25 games in window).
- We sit at a 49.4% all-time win rate; primary defensive danger window is around the **78'** mark.
- Senior centre-back depth is the limiting factor - protect it in selection.

## 2. Opponent model (dataset)
- Aliases matched: Real Madrid
- Recent window: 25 matches, W/D/L **19/0/6** (76.0% wins)
- Goals: 44.0 for / 26.0 against (avg 1.76 - 1.04)
- Home: 15 games (29.0-14.0) | Away: 10 (15.0-12.0)
- Strength index (goal diff): **0.72** | PPG last 25: **2.28**
- Main competitions: spain (19), UEFA CL (6)
- Last results:
  - 2025-05-18 spain: Sevilla 2.0-0.0 Real Madrid (W)
  - 2025-05-24 spain: Real Madrid 2.0-0.0 Real Sociedad (W)
  - 2025-08-19 spain: Real Madrid 1.0-0.0 Osasuna (W)
  - 2025-08-24 spain: Real Oviedo 3.0-0.0 Real Madrid (W)
  - 2025-08-30 spain: Real Madrid 2.0-1.0 Mallorca (W)
  - 2025-09-13 spain: Real Sociedad 2.0-1.0 Real Madrid (W)
  - 2025-09-16 UEFA CL: Real Madrid 2.0-1.0 Olympique Marseille (W)
  - 2025-09-20 spain: Real Madrid 2.0-0.0 Espanyol (W)

## 3. Head-to-head
- 20 prior meetings, W/D/L **5/9/6** (25.0% for us), 2017-05-10 to 2025-03-12.
- Recent:
  - 2024-02-04 spain: Real Madrid 1.0-1.0 Atlético Madrid (D)
  - 2024-09-29 spain: Atlético Madrid 1.0-1.0 Real Madrid (D)
  - 2025-02-08 spain: Real Madrid 1.0-1.0 Atlético Madrid (D)
  - 2025-03-04 UEFA CL: Real Madrid 1.0-2.0 Atlético Madrid (L)
  - 2025-03-12 UEFA CL: Atlético Madrid 1.0-0.0 Real Madrid (W)

## 4. Our squad state (dossier)
- Squad size: **23** | Core Starters: 11
- By position: DF 7, DF,MF 2, FW 1, FW,MF 3, GK 1, MF 8, MF,FW 1
- Injury-risk flags: none flagged
- Structural risk: Only 3 centre-back options with meaningful minutes available (Dávid Hancko, Marc Pubill, Robin Le Normand) plus depth: Cristian Romero, Daniel Martinez, Jorge Domínguez, José María Giménez - central defensive depth is the key structural risk.
- Rotation priority: Protect central defensive and goalkeeper depth while rotating midfield and wide attackers.

## 5. Historical windows (dataset-derived)
- Goals scored minute profile: 0'–14' (245), 15'–29' (316), 30'–44' (315), 45'–59' (348), 60'–74' (362), 75'–89' (394), 90'–104' (78)
- Goals conceded minute profile: 0'–14' (164), 15'–29' (209), 30'–44' (232), 45'–59' (220), 60'–74' (235), 75'–89' (294), 90'–104' (49)
- We concede 24.4% of goals after the 75th minute (avg concede 50.4').
- Typical substitution windows (from 2581 past sub events): 60'–74', 75'–89', 45'–59'

## 6. Recommended approach
- Compress blocking early if we concede space late; prioritise maintaining compactness through the final quarter.
- Use the 78' band as an alert phase - bank possession or refresh wide units before that stretch if possible.
- Consider planning first rotation around 60'–74' using available bench profiles (see dossier).
- Honour the senior centre-back rotation rule in `team_constraints`; no core starter is benched without an emergency trigger (from dossier workflow).

## 7. Risks & mitigations
- Key risk: late-game leakage + opponent transition speed (if their scoring window is early).
- Mitigation: pre-emptive sub management in the identified windows; keep a senior CB on the bench per `team_constraints`.
