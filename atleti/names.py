import difflib
import re
import unicodedata


def fold(name):
    if name is None:
        return ""
    text = unicodedata.normalize("NFKD", str(name))
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", text.lower())


_CLEAN_FIXES = (
    ("atltico", "atletico"),
    ("attico", "atletico"),
    ("atetico", "atletico"),
    ("atletic", "atletico"),
)


def variants(name):
    base = fold(name)
    out = {base}
    for enc in ("latin-1", "cp1252"):
        try:
            repaired = name.encode(enc, "ignore").decode("utf-8", "ignore")
            out.add(fold(repaired))
        except Exception:
            continue
    fixed = set(out)
    for value in out:
        for bad, good in _CLEAN_FIXES:
            if bad in value:
                fixed.add(value.replace(bad, good))
    out.update(fixed)
    return out


def is_named(name, query_variants):
    if name is None:
        return False
    return bool(variants(name) & query_variants)


def _candidates(names_, name_by_last, counts, query_variants):
    out = []
    for name in names_:
        f = fold(name)
        if not f or len(f) < 3:
            continue
        if variants(name) & query_variants:
            rank = 0
        elif any(v in f for v in query_variants):
            rank = 1
        else:
            continue
        count = (counts or {}).get(name, 0)
        last = str(name_by_last.get(name, "") or "")
        out.append((count, -rank, last, name))
    return out


def resolve_team(names_, name_by_last, query, counts=None, k=3):
    out = _candidates(names_, name_by_last, counts, variants(query))
    out.sort(reverse=True)
    return [row[3] for row in out][:k]


def club_aliases(names_, name_by_last, counts, query):
    primary_list = resolve_team(names_, name_by_last, query, counts=counts, k=1)
    if not primary_list:
        return []
    primary = primary_list[0]
    pvariants = variants(primary)
    extra = [n for n in names_ if variants(n) & pvariants and n != primary]
    extra.sort(key=lambda n: -((counts or {}).get(n, 0)))
    return [primary] + extra