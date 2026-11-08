"""Tests de la chaîne extraire -> trad/ -> injecter.

    python -m pytest tests
"""

import ast
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import commun
import injecter

if not (commun.AMONT / "build.py").exists():
    pytest.skip("amont/ absent : git submodule update --init", allow_module_level=True)

CHAINES = commun.extraire()


def _module(remps, nom):
    src = (commun.AMONT / "tools" / f"{nom}.py").read_bytes()
    return injecter.appliquer(src, remps).decode("utf-8")


def _valeur(source, variable):
    for n in ast.parse(source).body:
        if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == variable for t in n.targets):
            return ast.literal_eval(n.value)
    raise KeyError(variable)


def test_extraction_couvre_toutes_les_tables():
    vues = {c.table.variable for c in CHAINES}
    assert vues == {t.variable for t in commun.TABLES}


def test_ids_uniques_par_fichier():
    cles = [(commun.chemin_json(c), c.id) for c in CHAINES]
    assert len(cles) == len(set(cles))


def test_rendu_dialogue_aller_retour():
    for c in CHAINES:
        if c.elements is None:
            continue
        neuf = ast.literal_eval(injecter.source_dialogue(c, c.en, lambda s: s))
        # Deux textes consécutifs sont fusionnés : le jeu les concatène de toute façon.
        attendu = []
        for e in c.elements:
            v = ast.literal_eval(e.source)
            if e.texte is not None and attendu and attendu[-1][0]:
                attendu[-1] = (True, attendu[-1][1] + v)
            else:
                attendu.append((e.texte is not None, v))
        assert neuf == [v for _, v in attendu], c.id


def test_sans_traduction_rien_ne_change():
    for nom in {t.module for t in commun.TABLES}:
        src = (commun.AMONT / "tools" / f"{nom}.py").read_bytes()
        assert injecter.appliquer(src, []) == src


def test_injection_remplace_au_bon_endroit():
    trads = {}
    choix = {}
    for c in CHAINES:
        rel = commun.chemin_json(c).relative_to(commun.TRAD).as_posix()
        if c.table.variable in choix:
            continue
        fr = c.en if c.elements is not None else "Été"
        if c.elements is not None:
            fr = c.en.replace("O", "Ô", 1) if "O" in c.en else c.en + ""
        trads[(rel, c.id)] = {"fr": fr}
        choix[c.table.variable] = (c, fr)
    par_module = injecter.remplacements(CHAINES, trads, "garder")
    for var, (c, fr) in choix.items():
        src = _module(par_module[c.table.module], c.table.module)
        val = _valeur(src, var)
        t = c.table
        if t.genre == "trans":
            texte = "".join(x for x in val[int(c.id, 16)] if isinstance(x, str) and x not in commun.CONTROLES)
            assert texte == "".join(v for k, v in commun.decouper(fr) if k == "t")
        elif t.genre == "liste":
            assert val[int(c.id)] == "Été"
        elif t.genre == "liste0":
            assert val[int(c.id)][0] == "Été"
        elif t.genre == "dict1":
            assert [v[1] for v in val.values()].count("Été") == 1
        else:
            # L'afficheur ASCII n'a pas d'accents : translittération forcée.
            attendu = "Ete" if t.ascii_seul else "Été"
            assert list(val.values()).count(attendu) == 1


def test_balises_differentes_refusees():
    c = next(c for c in CHAINES if c.elements is not None and "{CR}" in c.en)
    with pytest.raises(injecter.ErreurInjection):
        injecter.source_dialogue(c, c.en.replace("{CR}", " ", 1), lambda s: s)


def test_translitteration():
    assert injecter.sans_accents("Élève à l'église, ça va ? ћ200") == "Eleve a l'eglise, ca va ? ћ200"
