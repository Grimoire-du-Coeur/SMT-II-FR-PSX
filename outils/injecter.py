"""Génère l'arbre de build français : l'amont, avec le français réinjecté.

    python outils/injecter.py                    # -> build/smt2-fr/
    python outils/injecter.py --sortie autre/dossier
    python outils/injecter.py --accents garder   # quand la police FR sera intégrée

Puis, dans le dossier généré, le build de Roman215 s'utilise tel quel :

    cd build/smt2-fr
    python build.py --input "chemin/vers/Shin Megami Tensei II (Japan) (Rev 1).bin"

Une entrée sans français garde son anglais : le jeu reste jouable de bout en
bout pendant toute la traduction, et chaque ligne traduite se voit tout de
suite en jeu.

Accents : tant que la police française n'est pas branchée sur l'encodeur
(voir police/README.md), ``--accents translitterer`` (le défaut) écrit
« e » pour « é », « c » pour « ç », etc. Le texte du dépôt, lui, garde
toujours ses accents.
"""

from __future__ import annotations

import argparse
import json
import py_compile
import shutil
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

from commun import AMONT, RACINE, TRAD, Chaine, charger_traductions, chemin_json, decouper, extraire

ACCENTS = json.loads((RACINE / "police" / "caracteres.json").read_text(encoding="utf-8"))["accents"]


def sans_accents(s: str) -> str:
    out = []
    for ch in s:
        if ch in ACCENTS:
            ch = "".join(c for c in unicodedata.normalize("NFD", ch) if not unicodedata.combining(c))
        out.append(ch)
    return "".join(out)


class ErreurInjection(Exception):
    pass


# Correctifs du code amont qui ne sont pas du texte de trad/ mais que le
# français impose. Chaque correctif est un remplacement exact : si l'amont
# change ce passage, l'injection s'arrête au lieu de deviner.
CORRECTIFS = [
    # {AG} (et A6F en négociation) affiche le nom du chef suivi de "'s party" :
    # « Hawk's party used... ». En français, {AG} est le nom seul et la phrase
    # s'accorde au singulier : « Hawk utilise... ». Tous les usages du suffixe
    # sont gardés par « if suffix: », une chaîne vide est donc sans effet de bord.
    ("translate_pipeline", 'PARTY_LEADER_SUFFIX = "\'s party"', 'PARTY_LEADER_SUFFIX = ""'),
]


def appliquer_correctifs(sortie: Path) -> None:
    for module, avant, apres in CORRECTIFS:
        p = sortie / "tools" / f"{module}.py"
        src = p.read_text(encoding="utf-8")
        if src.count(avant) != 1:
            raise ErreurInjection(f"correctif introuvable dans {module}.py (l'amont a changé ?) : {avant}")
        p.write_text(src.replace(avant, apres), encoding="utf-8", newline="")


def source_dialogue(c: Chaine, fr: str, conv) -> str:
    """Reconstruit la liste Python d'un dialogue à partir de la chaîne FR."""
    controles = [e.source for e in c.elements if e.texte is None]
    attendu = [e.balise for e in c.elements if e.texte is None]
    morceaux = decouper(fr)
    obtenu = [v for k, v in morceaux if k == "b"]
    if obtenu != attendu:
        raise ErreurInjection(f"{c.id} : balises {obtenu} au lieu de {attendu}")
    it = iter(controles)
    items = [repr(conv(v)) if k == "t" else next(it) for k, v in morceaux]
    return "[" + ",".join(items) + "]"


def remplacements(chaines: list[Chaine], trads: dict, mode: str) -> dict[str, list]:
    par_module = defaultdict(list)
    for c in chaines:
        rel = chemin_json(c).relative_to(TRAD).as_posix()
        e = trads.get((rel, c.id))
        if not e or not e.get("fr"):
            continue
        conv = sans_accents if (mode == "translitterer" or c.table.ascii_seul) else (lambda s: s)
        if c.elements is not None:
            neuf = source_dialogue(c, e["fr"], conv)
        else:
            neuf = repr(conv(e["fr"]))
        par_module[c.table.module].append((c.span, neuf))
    return par_module


def appliquer(octets: bytes, remps: list) -> bytes:
    out = bytearray(octets)
    for (a, b), neuf in sorted(remps, key=lambda r: r[0][0], reverse=True):
        out[a:b] = neuf.encode("utf-8")
    return bytes(out)


def copier_amont(sortie: Path) -> None:
    if sortie.exists():
        # On ne conserve que build/ (images générées, psxavenc en cache).
        for p in sortie.iterdir():
            if p.name == "build" or p.suffix.lower() in (".bin", ".cue"):
                continue
            shutil.rmtree(p) if p.is_dir() else p.unlink()
    shutil.copytree(AMONT, sortie, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", "__pycache__"))


def verifier_import(sortie: Path, modules: list[str]) -> None:
    code = "import sys; sys.path.insert(0, 'tools'); " + "; ".join(f"import {m}" for m in modules)
    r = subprocess.run([sys.executable, "-c", code], cwd=sortie, capture_output=True, text=True, check=False)
    if r.returncode:
        raise ErreurInjection("les modules générés ne se chargent pas :\n" + r.stderr[-2000:])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sortie", type=Path, default=RACINE / "build" / "smt2-fr")
    ap.add_argument("--accents", choices=("translitterer", "garder"), default="translitterer")
    args = ap.parse_args()

    if not (AMONT / "build.py").exists():
        print("amont/ est vide : lance d'abord  git submodule update --init", file=sys.stderr)
        return 2

    chaines = extraire()
    try:
        par_module = remplacements(chaines, charger_traductions(), args.accents)
    except ErreurInjection as e:
        print("ERREUR :", e, "\n(lance  python outils/valider.py  pour le détail)", file=sys.stderr)
        return 1

    copier_amont(args.sortie)
    total = 0
    for module, remps in sorted(par_module.items()):
        cible = args.sortie / "tools" / f"{module}.py"
        cible.write_bytes(appliquer((AMONT / "tools" / f"{module}.py").read_bytes(), remps))
        py_compile.compile(str(cible), doraise=True)
        total += len(remps)
        print(f"  {module:14} {len(remps):5} entrée(s) en français")
    try:
        appliquer_correctifs(args.sortie)
        verifier_import(args.sortie, sorted({t.module for t in (c.table for c in chaines)} | {"translate_pipeline"}))
    except ErreurInjection as e:
        print("ERREUR :", e, file=sys.stderr)
        return 1
    print(f"{total} entrée(s) réinjectée(s) sur {len(chaines)} -> {args.sortie}")
    if args.accents == "translitterer":
        print("(accents translittérés : la police française n'est pas encore branchée)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
