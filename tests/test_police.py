import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "police"))

import accents as A

E_8x10 = A.depuis_octets(bytes.fromhex("000000007088f8807800"), 8, 10)   # « e » de Roman215


def test_aller_retour_octets():
    assert A.vers_octets(E_8x10) == bytes.fromhex("000000007088f8807800")


def test_e_aigu_pose_au_dessus_avec_une_ligne_de_vide():
    g = A.composer(E_8x10, "aigu", "e")
    assert g[:4] != E_8x10[:4]
    assert not any(g[3])                  # ligne de séparation
    assert g[4:] == E_8x10[4:]            # la lettre n'a pas bougé


def test_majuscule_sans_place_refusee():
    haut = [[0] * 8] + [[1, 1, 1, 1, 1, 0, 0, 0]] * 8 + [[0] * 8]
    assert A.composer(haut, "aigu", "E") is None


def test_i_perd_son_point():
    i = A.depuis_octets(bytes.fromhex("00200000602020207000"), 8, 10)
    g = A.composer(i, "trema", "i")
    assert g[1] == [0] * 8                # l'ancien point est effacé


def test_cedille_sous_la_lettre():
    c = A.depuis_octets(bytes.fromhex("00000000788880887800"), 8, 10)
    g = A.composer(c, "cedille", "c")
    assert any(g[9])


def test_tous_les_accents_de_la_police_sont_definis():
    cars = json.loads((RACINE / "police" / "caracteres.json").read_text(encoding="utf-8"))["accents"]
    assert set(cars) <= set(A.ACCENTS)
