"""Briques partagées par les outils du dépôt.

Le texte anglais de Roman215 vit dans six modules Python du dépôt amont
(``amont/tools/*.py``), mêlé au code qui l'injecte dans le jeu. Plutôt que de
recopier ces fichiers et d'y glisser des lignes ``#`` à remplir, on les lit
avec ``ast`` : chaque chaîne traduisible est repérée par sa position exacte
dans le source, extraite vers ``trad/**.json``, puis remplacée au même endroit
au moment de générer la version française. Le code de Roman215 n'est jamais
modifié à la main, et une nouvelle version de l'amont se récupère d'un coup.

Ce module ne dépend que de la bibliothèque standard.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Les consoles Windows ne sont pas en UTF-8 par défaut : sans ça, « entrées »
# s'affiche « entr�es ».
for _flux in (sys.stdout, sys.stderr):
    if hasattr(_flux, "reconfigure"):
        _flux.reconfigure(encoding="utf-8")

RACINE = Path(__file__).resolve().parent.parent
AMONT = RACINE / "amont"
TRAD = RACINE / "trad"

# Codes de contrôle des dialogues (tools/translate_pipeline.py, CTRL_NAME et
# AB_CTRL_INDEX). Ce ne sont pas du texte : ils s'écrivent {CR}, {WT}...
CONTROLES = {
    "CR", "WT", "PG", "ED", "SY", "SN", "Fe", "TI", "IT", "FI", "FO", "NI", "AG",
    "SU", "S2", "MN", "KO", "OT", "ZK", "ZO", "MG", "MH", "PP", "AL", "SE", "TW",
} | {f"A{i:02X}" for i in (0x0E, 0x0F, 0x14, 0x61, 0x62, 0x63, 0x64, 0x65,
                            0x66, 0x67, 0x68, 0x69, 0x6B, 0x6E, 0x6F)}

BALISE = re.compile(r"\{([^{}]*)\}")


@dataclass(frozen=True)
class Table:
    """Une structure de données traduisible dans un module amont."""

    module: str          # nom du fichier dans amont/tools, sans .py
    variable: str        # nom de la variable au niveau du module
    genre: str           # "trans" | "liste" | "dict" | "liste0" | "dict1"
    fichier: str         # chemin du JSON sous trad/ ; "{page}" pour les dialogues
    titre: str           # libellé humain (SUIVI.md)
    categorie: str       # regroupement des badges
    max_car: int | None = None   # limite stricte en caractères, si connue
    ascii_seul: bool = False     # chemin d'affichage sans accents possibles


TABLES: list[Table] = [
    Table("translations", "TRANS", "trans", "dialogues/{page}.json", "Dialogues", "dialogues"),
    Table("sys_strings", "SYS", "dict1", "systeme/sys.json", "Système — sauvegarde & carte mémoire", "systeme"),
    Table("sys_strings", "RETRANSLATED", "dict", "systeme/retraduit.json", "Système — COMP & invocations", "systeme"),
    Table("sys_strings", "ASCII_FIT_ENGLISH", "dict", "systeme/ascii.json", "Système — messages courts (ASCII)", "systeme", ascii_seul=True),
    Table("sys_strings", "AUDITED_SYSTEM_TEXT", "dict", "systeme/audite.json", "Système — menus, aide, boutiques", "systeme"),
    Table("menu_table", "MENU", "dict", "menus/commandes.json", "Menus — commandes", "menus"),
    Table("menu_table", "AB_MENU", "liste", "menus/negociation.json", "Menus — négociation", "menus"),
    Table("name_tables", "DEMONS", "liste", "noms/demons.json", "Noms — démons", "noms"),
    Table("name_tables", "RACES", "liste", "noms/races.json", "Noms — races", "noms"),
    Table("name_tables", "SPELLS", "liste", "noms/sorts.json", "Noms — sorts", "noms"),
    Table("name_tables", "ITEMS", "liste", "noms/objets.json", "Noms — objets", "noms"),
    Table("name_tables", "LOCATIONS", "liste", "noms/lieux.json", "Noms — lieux", "noms"),
    Table("name_tables", "NPCS", "liste", "noms/pnj.json", "Noms — PNJ", "noms"),
    Table("name_tables", "DRINKS", "liste", "noms/boissons.json", "Noms — boissons", "noms"),
    Table("name_tables", "TRAITS_MAP", "dict", "noms/affinites.json", "Noms — affinités", "noms"),
    Table("map_names", "ENGLISH", "liste", "cartes/lieux.json", "Cartes — noms de zones", "cartes"),
    Table("party_names", "NAMES", "liste0", "equipe/noms.json", "Équipe — noms par défaut", "equipe", max_car=8),
]

CATEGORIES = {
    "dialogues": "Dialogues",
    "systeme": "Système",
    "menus": "Menus",
    "noms": "Noms",
    "cartes": "Cartes",
    "equipe": "Équipe",
}


@dataclass
class Chaine:
    """Une entrée traduisible, telle qu'elle sera écrite dans le JSON."""

    table: Table
    id: str
    en: str
    # Spans (début, fin) en octets UTF-8 dans le source amont, un par segment
    # de texte. Pour les dialogues, ``elements`` garde la liste complète afin
    # de reconstruire les codes de contrôle à l'identique.
    span: tuple[int, int] | None = None
    elements: list | None = None
    note: str = ""
    max_octets: int | None = None
    page: str = ""


@dataclass
class Element:
    """Un élément d'une liste de dialogue : texte ou contrôle."""

    texte: str | None          # None si contrôle
    balise: str | None         # "CR", "0xc095,True"... si contrôle
    source: str                # texte source exact de l'élément


@dataclass
class Module:
    nom: str
    octets: bytes
    arbre: ast.Module
    lignes: list[int] = field(default_factory=list)   # offset octet de chaque ligne

    @classmethod
    def charger(cls, nom: str, racine: Path = AMONT) -> Module:
        brut = (racine / "tools" / f"{nom}.py").read_bytes()
        arbre = ast.parse(brut.decode("utf-8"))
        lignes = [0]
        for i, b in enumerate(brut):
            if b == 0x0A:
                lignes.append(i + 1)
        return cls(nom, brut, arbre, lignes)

    def span(self, noeud: ast.AST) -> tuple[int, int]:
        debut = self.lignes[noeud.lineno - 1] + noeud.col_offset
        fin = self.lignes[noeud.end_lineno - 1] + noeud.end_col_offset
        return debut, fin

    def source(self, noeud: ast.AST) -> str:
        a, b = self.span(noeud)
        return self.octets[a:b].decode("utf-8")

    def affectation(self, variable: str) -> ast.AST:
        for n in self.arbre.body:
            if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == variable for t in n.targets):
                return n.value
        raise KeyError(f"{self.nom}.{variable} introuvable dans l'amont")

    def commentaire_au_dessus(self, noeud: ast.AST) -> str:
        """Commentaires de l'amont juste au-dessus d'une entrée (contexte utile)."""
        texte = self.octets.decode("utf-8").splitlines()
        i = noeud.lineno - 2
        bloc: list[str] = []
        while i >= 0 and texte[i].strip().startswith("#"):
            bloc.append(texte[i].strip().lstrip("#").strip())
            i -= 1
        return " ".join(reversed([b for b in bloc if b and not set(b) <= set("-= ")]))


def _est_str(n: ast.AST) -> bool:
    return isinstance(n, ast.Constant) and isinstance(n.value, str)


def _cle(mod: Module, k: ast.AST) -> str:
    if _est_str(k):
        return k.value
    if isinstance(k, ast.Constant) and isinstance(k.value, int):
        return mod.source(k)
    return mod.source(k)


def elements_dialogue(mod: Module, liste: ast.List) -> list[Element]:
    out = []
    for e in liste.elts:
        if _est_str(e) and e.value not in CONTROLES:
            out.append(Element(e.value, None, mod.source(e)))
        elif _est_str(e):
            out.append(Element(None, e.value, mod.source(e)))
        else:
            out.append(Element(None, re.sub(r"\s+", "", mod.source(e)).strip("()"), mod.source(e)))
    return out


def rendre(elements: list[Element]) -> str:
    """Liste de dialogue -> chaîne lisible : "Salut{CR}toi.{WT}{ED}"."""
    return "".join(e.texte if e.texte is not None else "{" + e.balise + "}" for e in elements)


def balises(s: str) -> list[str]:
    return BALISE.findall(s)


def decouper(s: str) -> list[tuple[str, str]]:
    """Chaîne lisible -> [("t", texte) | ("b", balise)]."""
    out, pos = [], 0
    for m in BALISE.finditer(s):
        if m.start() > pos:
            out.append(("t", s[pos:m.start()]))
        out.append(("b", m.group(1)))
        pos = m.end()
    if pos < len(s):
        out.append(("t", s[pos:]))
    return out


def page_dialogue(cle: int) -> str:
    return f"0x{cle >> 8:02x}xx"


def extraire(racine: Path = AMONT) -> list[Chaine]:
    """Toutes les chaînes traduisibles de l'amont, dans l'ordre du source."""
    chaines: list[Chaine] = []
    modules: dict[str, Module] = {}
    for t in TABLES:
        mod = modules.setdefault(t.module, Module.charger(t.module, racine))
        val = mod.affectation(t.variable)
        if t.genre == "trans":
            vus = set()
            for k, v in zip(val.keys, val.values):
                cle = ast.literal_eval(k)
                ident = f"0x{cle:04x}"
                if ident in vus:
                    raise ValueError(f"clé de dialogue en double dans l'amont : {ident}")
                vus.add(ident)
                els = elements_dialogue(mod, v)
                if not any(e.texte for e in els):
                    continue          # entrée purement technique : rien à traduire
                chaines.append(Chaine(t, ident, rendre(els), span=mod.span(v), elements=els,
                                      note=mod.commentaire_au_dessus(k), page=page_dialogue(cle)))
        elif t.genre in ("liste", "liste0"):
            for i, e in enumerate(val.elts):
                if t.genre == "liste0":
                    e = e.elts[0]
                if not _est_str(e) or not e.value.strip():
                    continue
                chaines.append(Chaine(t, str(i), e.value, span=mod.span(e)))
        elif t.genre in ("dict", "dict1"):
            for k, v in zip(val.keys, val.values):
                maxo = None
                if t.genre == "dict1":
                    maxo = ast.literal_eval(v.elts[0])
                    v = v.elts[1]
                if not _est_str(v) or not v.value.strip():
                    continue
                chaines.append(Chaine(t, _cle(mod, k), v.value, span=mod.span(v), max_octets=maxo))
        else:
            raise ValueError(t.genre)
    return chaines


def chemin_json(c: Chaine) -> Path:
    return TRAD / c.table.fichier.format(page=c.page)


def lire_json(p: Path) -> list[dict]:
    return json.loads(p.read_text(encoding="utf-8"))


def ecrire_json(p: Path, entrees: list[dict]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(entrees, ensure_ascii=False, indent=2) + "\n"
    p.write_text(texte, encoding="utf-8", newline="\n")


def charger_traductions() -> dict[tuple[str, str], dict]:
    """{(fichier relatif, id): entrée} pour tout trad/."""
    out = {}
    for p in sorted(TRAD.rglob("*.json")):
        rel = p.relative_to(TRAD).as_posix()
        for e in lire_json(p):
            out[(rel, e["id"])] = e
    return out
