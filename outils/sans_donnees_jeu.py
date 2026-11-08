"""Refuse tout fichier qui ressemble à une donnée du jeu.

    python outils/sans_donnees_jeu.py

Lancé par la CI sur chaque Pull Request. Le dépôt ne doit contenir que du
texte, des outils et quelques images à nous.
"""

import subprocess
import sys
from pathlib import Path

INTERDITS = {".bin", ".cue", ".iso", ".img", ".chd", ".pbp", ".ecm", ".str", ".xa", ".vab", ".seq",
             ".tim", ".xdelta", ".sav", ".mcr", ".mcd", ".sstate", ".exe"}
NOMS = ("SLPM_869", "SLPM-869", "SYSTEM.CNF")
TAILLE_MAX = 2 * 1024 * 1024          # 2 Mo : largement assez pour une capture
EXCEPTIONS_TAILLE = set()


def main() -> int:
    racine = Path(__file__).resolve().parent.parent
    suivis = subprocess.run(["git", "ls-files"], cwd=racine, capture_output=True, text=True,
                            check=True).stdout.splitlines()
    fautes = []
    for f in suivis:
        p = racine / f
        if not p.is_file():
            continue            # sous-module
        if p.suffix.lower() in INTERDITS:
            fautes.append(f"{f} : type de fichier interdit ({p.suffix})")
        elif any(n.lower() in p.name.lower() for n in NOMS) and p.suffix.lower() not in (".jpg", ".png"):
            fautes.append(f"{f} : nom de fichier du jeu")
        elif p.stat().st_size > TAILLE_MAX and f not in EXCEPTIONS_TAILLE:
            fautes.append(f"{f} : {p.stat().st_size} octets (plus de {TAILLE_MAX // 1024 // 1024} Mo)")
    for x in fautes:
        print(f"::error file={x.split(' :')[0]}::{x}")
    print(f"{len(suivis)} fichiers suivis, {len(fautes)} problème(s).")
    return 1 if fautes else 0


if __name__ == "__main__":
    sys.exit(main())
