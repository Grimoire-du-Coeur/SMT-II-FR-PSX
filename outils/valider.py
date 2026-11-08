"""Vérifie les traductions de trad/ avant qu'elles partent en jeu.

    python outils/valider.py                       # tout le dépôt
    python outils/valider.py trad/dialogues/0x01xx.json
    python outils/valider.py --github              # annotations pour les PR

ERREUR  = le build casserait, ou le texte serait faux à coup sûr. Bloquant.
ATTENTION = à regarder, mais pas bloquant (longueur, dictionnaire...).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from commun import AMONT, RACINE, TRAD, balises, chemin_json, extraire

sys.path.insert(0, str(AMONT / "tools"))
import build_en_tree as ET

POLICE = json.loads((RACINE / "police" / "caracteres.json").read_text(encoding="utf-8"))
ACCENTS = set(POLICE["accents"])
INTERDITS = POLICE["interdits"]
CHAMPS = {"id", "en", "fr", "max_octets", "note", "a_revoir", "commentaire"}
LARGEUR_LIGNE = 32          # caractères ; la boîte de dialogue en affiche ~30
COUPURES = {"CR", "PG", "WT"}   # balises après lesquelles le texte repart en début de ligne


@dataclass
class Message:
    niveau: str
    fichier: str
    id: str
    texte: str
    ligne: int = 1


def glyphe_ok(ch: str) -> bool:
    try:
        ET.fullwidth(ch)
        return True
    except KeyError:
        return False


def lignes(s: str) -> list[str]:
    coupe = r"\{(?:" + "|".join(COUPURES) + r")\}"
    sans_autres = re.sub(r"\{(?!(?:" + "|".join(COUPURES) + r")\})[^{}]*\}", "", s)
    return [x.strip() for x in re.split(coupe, sans_autres)]


def charger_dictionnaire() -> list[tuple[str, str]]:
    """Termes validés (✅) de docs/Dictionnaire.md : [(anglais, français)]."""
    p = RACINE / "docs" / "Dictionnaire.md"
    if not p.exists():
        return []
    out = []
    for l in p.read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cols) >= 3 and "✅" in cols[2] and not cols[0].startswith("-"):
            en = re.sub(r"\*\(.*?\)\*", "", cols[0]).split("/")[0].strip().strip("*`")
            fr = cols[1].split("/")[0].strip()
            if fr.startswith(("*", "—")) or "," in en:
                continue            # « inchangés », listes de noms : rien à contrôler
            fr = fr.strip("`")
            if en and fr and en != fr and len(en) > 2:
                out.append((en, fr))
    # Les termes longs d'abord : « Center Gal » masque « Center » dans la même ligne.
    return sorted(out, key=lambda t: -len(t[0]))


def termes_manquants(en: str, fr: str, dico: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out = []
    for en_t, fr_t in dico:
        motif = rf"\b{re.escape(en_t)}\b"
        if re.search(motif, en):
            if fr_t.lower() not in fr.lower():
                out.append((en_t, fr_t))
            en = re.sub(motif, " ", en)
    return out


def valider(fichiers: list[Path] | None) -> list[Message]:
    msgs: list[Message] = []
    amont = {}
    tables = {}
    car_table: dict[str, set] = {}
    for c in extraire():
        rel = chemin_json(c).relative_to(TRAD).as_posix()
        amont[(rel, c.id)] = c
        tables[rel] = c.table
        car_table.setdefault(rel, set()).update(c.en)
    dico = charger_dictionnaire()

    tous = sorted(p for p in TRAD.rglob("*.json") if not p.name.startswith("_"))
    cibles = [p.resolve() for p in fichiers] if fichiers else [p.resolve() for p in tous]
    presents = set()

    for p in tous:
        rel = p.relative_to(TRAD).as_posix()
        brut = p.read_text(encoding="utf-8")
        try:
            entrees = json.loads(brut)
        except json.JSONDecodeError as e:
            msgs.append(Message("ERREUR", rel, "-", f"JSON invalide : {e.msg} (ligne {e.lineno})", e.lineno))
            continue
        lignes_id = {}
        for i, l in enumerate(brut.splitlines(), 1):
            m = re.match(r'\s*"id": "(.*)",?$', l)
            if m:
                lignes_id[json.loads(f'"{m.group(1)}"')] = i
        for e in entrees:
            presents.add((rel, e.get("id")))
        if p.resolve() not in cibles:
            continue
        table = tables.get(rel)
        for e in entrees:
            ident = e.get("id", "?")
            ln = lignes_id.get(ident, 1)

            def m(niv, t, rel=rel, ident=ident, ln=ln):
                msgs.append(Message(niv, rel, ident, t, ln))

            inconnus = set(e) - CHAMPS
            if inconnus:
                m("ERREUR", f"champ(s) inconnu(s) : {', '.join(sorted(inconnus))}")
            c = amont.get((rel, ident))
            if c is None:
                m("ERREUR", "cette entrée n'existe pas dans l'amont (id modifié ?)")
                continue
            if e.get("en") != c.en:
                m("ERREUR", "le champ \"en\" a été modifié : il ne faut toucher qu'à \"fr\"")
            fr = e.get("fr", "")
            if not isinstance(fr, str):
                m("ERREUR", "\"fr\" doit être une chaîne")
                continue
            if e.get("a_revoir"):
                m("ATTENTION", "l'anglais a changé depuis la traduction : relire puis retirer \"a_revoir\"")
            if not fr:
                continue

            # 1. Balises de contrôle : mêmes codes, même ordre.
            if c.elements is not None:
                be, bf = balises(c.en), balises(fr)
                if be != bf:
                    m("ERREUR", f"balises différentes de l'anglais : {''.join('{'+b+'}' for b in bf)} "
                                f"au lieu de {''.join('{'+b+'}' for b in be)}")
                if re.search(r"[{}]", re.sub(r"\{[^{}]*\}", "", fr)):
                    m("ERREUR", "accolade isolée : une balise est mal fermée")
            # 2. Caractères.
            texte = re.sub(r"\{[^{}]*\}", "", fr) if c.elements is not None else fr
            for ch in sorted(set(texte)):
                if ch in INTERDITS:
                    m("ERREUR", f"caractère « {ch} » interdit : écrire {INTERDITS[ch]}")
                elif ch in ACCENTS:
                    if table.ascii_seul:
                        m("ATTENTION", f"« {ch} » : ce texte passe par l'afficheur ASCII, il sortira sans accent")
                elif not glyphe_ok(ch) and ch not in car_table[rel]:
                    m("ERREUR", f"caractère « {ch} » (U+{ord(ch):04X}) absent de la police du jeu")
            # 3. Longueurs.
            if table.max_car and len(fr) > table.max_car:
                m("ERREUR", f"{len(fr)} caractères pour {table.max_car} au maximum")
            if c.max_octets and len(fr) + 1 > c.max_octets:
                m("ERREUR", f"trop long pour son emplacement : {len(fr) + 1} octets pour {c.max_octets}")
            elif table.categorie in ("systeme", "noms", "menus", "cartes") and len(fr) > len(c.en):
                m("ATTENTION", f"plus long que l'anglais ({len(fr)} > {len(c.en)}) : place à vérifier en jeu")
            if c.elements is not None:
                limite = max(LARGEUR_LIGNE, *(len(x) for x in lignes(c.en)))
                for x in lignes(fr):
                    if len(x) > limite:
                        m("ATTENTION", f"ligne de {len(x)} caractères (limite ~{limite}) : « {x[:40]}… » — ajouter un {{CR}} ?")
            # 4. Typographie (convention du Grimoire, cf. CONTRIBUTING.md).
            # Une balise compte comme un mot : « Congédier {MG}? » est correct.
            if re.search(r"\w \?|\w !|\w :", re.sub(r"\{[^{}]*\}", "X", fr)):
                m("ATTENTION", "pas d'espace avant ! ? : (convention du projet, comme P1)")
            if re.search(r"\s$", texte) and not re.search(r"\s$", re.sub(r"\{[^{}]*\}", "", c.en)):
                m("ATTENTION", "espace en fin de texte")
            if c.elements is not None and texte == re.sub(r"\{[^{}]*\}", "", c.en) and len(texte) > 12:
                m("ATTENTION", "le français est identique à l'anglais : oubli ?")
            # 5. Dictionnaire.
            for en_t, fr_t in termes_manquants(c.en, fr, dico):
                m("ATTENTION", f"dictionnaire : « {en_t} » se traduit « {fr_t} »")

    if fichiers is None:
        for (rel, ident) in sorted(set(amont) - presents):
            msgs.append(Message("ERREUR", rel, ident, "entrée de l'amont absente : lancer  python outils/extraire.py"))
    return msgs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("fichiers", nargs="*", type=Path)
    ap.add_argument("--github", action="store_true", help="annotations ::error / ::warning")
    ap.add_argument("--erreurs-seules", action="store_true")
    args = ap.parse_args()

    msgs = valider(args.fichiers or None)
    nerr = sum(m.niveau == "ERREUR" for m in msgs)
    natt = len(msgs) - nerr
    for m in msgs:
        if args.erreurs_seules and m.niveau != "ERREUR":
            continue
        if args.github:
            niv = "error" if m.niveau == "ERREUR" else "warning"
            print(f"::{niv} file=trad/{m.fichier},line={m.ligne},title={m.id}::{m.texte}")
        else:
            print(f"{m.niveau:9} trad/{m.fichier} [{m.id}] {m.texte}")
    print(f"\n{nerr} erreur(s), {natt} avertissement(s).")
    return 1 if nerr else 0


if __name__ == "__main__":
    sys.exit(main())
