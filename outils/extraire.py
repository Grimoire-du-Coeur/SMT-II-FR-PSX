"""Crée ou met à jour trad/**.json à partir du texte anglais de l'amont.

    python outils/extraire.py            # met à jour trad/
    python outils/extraire.py --verifier # n'écrit rien, échoue si trad/ est en retard

À lancer après chaque montée de version de l'amont (voir docs/TECHNIQUE.md).
Aucune traduction n'est jamais perdue :

- une entrée dont l'anglais a changé garde son français et reçoit
  ``"a_revoir"`` avec l'ancien anglais, pour qu'un humain tranche ;
- une entrée disparue de l'amont qui avait un français part dans
  ``trad/_orphelins.json`` au lieu d'être effacée.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from commun import TRAD, charger_traductions, chemin_json, ecrire_json, extraire, lire_json


def construire() -> tuple[dict, list[dict], list[str]]:
    anciennes = charger_traductions()
    fichiers: dict = defaultdict(list)
    vus = set()
    revoir = []
    for c in extraire():
        p = chemin_json(c)
        rel = p.relative_to(TRAD).as_posix()
        vus.add((rel, c.id))
        old = anciennes.get((rel, c.id), {})
        e = {"id": c.id, "en": c.en, "fr": old.get("fr", "")}
        if c.max_octets is not None:
            e["max_octets"] = c.max_octets
        if c.note:
            e["note"] = c.note
        if old.get("en") not in (None, c.en) and e["fr"]:
            e["a_revoir"] = old["en"]
            revoir.append(f"{rel} {c.id}")
        elif old.get("a_revoir"):
            e["a_revoir"] = old["a_revoir"]
        if old.get("commentaire"):
            e["commentaire"] = old["commentaire"]
        fichiers[p].append(e)
    orphelins = [dict(e, fichier=rel) for (rel, i), e in anciennes.items()
                 if rel != "_orphelins.json" and (rel, i) not in vus and e.get("fr")]
    return fichiers, orphelins, revoir


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verifier", action="store_true", help="ne rien écrire, juste comparer")
    args = ap.parse_args()

    fichiers, orphelins, revoir = construire()
    retard = []
    for p, entrees in sorted(fichiers.items()):
        if not p.exists() or lire_json(p) != entrees:
            retard.append(p.relative_to(TRAD).as_posix())
            if not args.verifier:
                ecrire_json(p, entrees)
    po = TRAD / "_orphelins.json"
    if orphelins:
        anciens = lire_json(po) if po.exists() else []
        if not args.verifier:
            ecrire_json(po, anciens + orphelins)

    total = sum(len(v) for v in fichiers.values())
    print(f"{total} entrées dans {len(fichiers)} fichiers.")
    for r in revoir:
        print(f"  à revoir (l'anglais a changé) : {r}")
    if orphelins:
        print(f"  {len(orphelins)} traduction(s) orpheline(s) -> trad/_orphelins.json")
    if args.verifier and retard:
        print("trad/ n'est pas à jour avec l'amont :", *retard[:20], sep="\n  ")
        return 1
    if not args.verifier:
        print(f"{len(retard)} fichier(s) écrit(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
