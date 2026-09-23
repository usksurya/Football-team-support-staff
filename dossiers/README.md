# Team Dossier System

This folder stores the structured team data used by the custom tactical agents.

## Purpose

Each dossier acts as the source of truth for a club’s:
- squad profile
- player roles and traits
- tactical identity
- continuity constraints
- load-risk and injury considerations
- recommended system fit

## Loader model

The lead agent should read the active dossier, then map the squad into:
- starting lineup logic
- rotation units
- scenario-specific systems
- risk flags
- personnel optimization

## Example schema

```json
{
  "club": "Atletico Madrid",
  "season": "2026/27",
  "model": "asymmetric phase-change system",
  "core_identity": "high-structure, compact transitions, vertical control",
  "players": [
    {
      "name": "Cristian Romero",
      "position": "CB",
      "role": "stopper",
      "quality": "elite",
      "pedigree": "senior starter",
      "load_profile": "high",
      "injury_risk": "medium",
      "fit": ["3CB base", "deep progression"]
    }
  ]
}
```

## Recommended usage

- Keep one dossier per club.
- Add a dossier for each team you want analyzed.
- Swap the active dossier dynamically when the prompt changes club.
- Use the dossier to drive system selection, rotation planning, and risk mapping.
