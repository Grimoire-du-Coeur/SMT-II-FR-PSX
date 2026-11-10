"""Calcule l'avancement : SUIVI.md, badges shields.io et bloc du README.

    python outils/stats.py            # réécrit SUIVI.md, .github/badge*.json, README
    python outils/stats.py --court    # affiche seulement le résumé

Lancé automatiquement par .github/workflows/suivi.yml à chaque fusion.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict

from commun import CATEGORIES, RACINE, TABLES, TRAD, lire_json

BARRE = 24


def compter():
    par_cat = defaultdict(lambda: [0, 0])
    par_fichier = defaultdict(lambda: [0, 0])
    revoir = []
    cat_de = {}
    for t in TABLES:
        cat_de[t.fichier.split("{")[0]] = t.categorie
    for p in sorted(TRAD.rglob("*.json")):
        if p.name.startswith("_"):
            continue
        rel = p.relative_to(TRAD).as_posix()
        cat = next(c for f, c in cat_de.items() if rel.startswith(f) or rel == f)
        for e in lire_json(p):
            fait = bool(e.get("fr"))
            par_cat[cat][0] += fait
            par_cat[cat][1] += 1
            par_fichier[rel][0] += fait
            par_fichier[rel][1] += 1
            if e.get("a_revoir"):
                revoir.append((rel, e["id"]))
    return par_cat, par_fichier, revoir


def pct(f, t):
    return int(100 * f / t) if t else 0


def barre(f, t):
    n = round(BARRE * f / t) if t else 0
    return "█" * n + "░" * (BARRE - n)


def nb(n):
    return f"{n:,}".replace(",", " ")


def couleur(p):
    return "CE1126" if p < 25 else "B8860B" if p < 75 else "2E8B57"


def badge(label, f, t):
    p = pct(f, t)
    return {"schemaVersion": 1, "label": label, "message": f"{p} %", "color": couleur(p),
            "labelColor": "0D0D0D", "style": "for-the-badge"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--court", action="store_true")
    args = ap.parse_args()

    par_cat, par_fichier, revoir = compter()
    tf = sum(v[0] for v in par_cat.values())
    tt = sum(v[1] for v in par_cat.values())
    lignes = []
    for cat, nom in CATEGORIES.items():
        f, t = par_cat[cat]
        lignes.append(f"{nom:<13}  {barre(f, t)}  {pct(f, t):3} %   {nb(f):>6} / {nb(t)} textes")
    lignes.append("")
    lignes.append(f"{'Total':<13}  {barre(tf, tt)}  {pct(tf, tt):3} %   {nb(tf):>6} / {nb(tt)} textes")
    bloc = "\n".join(lignes)
    print(bloc)
    if args.court:
        return 0

    md = ["# Avancement de la traduction", "",
          "> Fichier **généré** par `outils/stats.py`. Ne pas le modifier à la main : chaque fusion l'écrase.",
          "", "```text", bloc, "```", "",
          ("Une entrée compte comme traduite dès que son champ `fr` est rempli. Sans traduction, "
           "le jeu affiche l'anglais de Roman215 : le patch reste jouable à chaque étape."), "",
          "## Par fichier", "", "| Fichier | Traduits | % |", "|---|---:|---:|"]
    for rel, (f, t) in sorted(par_fichier.items()):
        md.append(f"| [`{rel}`](trad/{rel}) | {nb(f)} / {nb(t)} | {pct(f, t)} % |")
    if revoir:
        md += ["", "## À revoir", "",
               "L'anglais de l'amont a changé depuis que ces lignes ont été traduites.", ""]
        md += [f"- [`{rel}`](trad/{rel}) — `{i}`" for rel, i in revoir]
    (RACINE / "SUIVI.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")

    gh = RACINE / ".github"
    gh.mkdir(exist_ok=True)
    (gh / "badge.json").write_text(json.dumps(badge("traduction", tf, tt)) + "\n",
                                   encoding="utf-8", newline="\n")
    for cat, nom in CATEGORIES.items():
        f, t = par_cat[cat]
        (gh / f"badge_{cat}.json").write_text(json.dumps(badge(nom.lower(), f, t), ensure_ascii=False) + "\n",
                                               encoding="utf-8", newline="\n")

    readme = RACINE / "README.md"
    if readme.exists():
        txt = readme.read_text(encoding="utf-8")
        neuf = re.sub(r"(<!-- avancement:debut -->\n).*?(\n<!-- avancement:fin -->)",
                      lambda m: m.group(1) + "```text\n" + bloc + "\n```" + m.group(2), txt, flags=re.DOTALL)
        if neuf != txt:
            readme.write_text(neuf, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
