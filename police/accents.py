"""Compose les lettres accentuées à partir des glyphes de base du jeu.

Plutôt que de dessiner 26 glyphes à la main dans trois polices (12x12 pour
les dialogues et menus, 10x10 pour les plaques de nom, 8x10 pour l'afficheur
ASCII), on part de la lettre de base déjà présente (et déjà crénée par le
build de Roman215) et on y pose l'accent au-dessus de l'encre, centré sur
la lettre. Le résultat suit donc automatiquement le style de chaque police.

Une majuscule n'a en général pas de place au-dessus d'elle dans une cellule
de 10 ou 12 pixels : ``composer`` renvoie alors ``None`` et le caractère est
remplacé par sa forme sans accent (É -> E), ce qui est l'usage courant pour
les capitales en jeu vidéo.

STATUT : module testé sur des bitmaps, pas encore branché sur build.py ni
vérifié en jeu. Voir police/README.md pour la suite.
"""

from __future__ import annotations

# lettre accentuée -> (lettre de base, accent)
ACCENTS = {
    "é": ("e", "aigu"), "è": ("e", "grave"), "ê": ("e", "circ"), "ë": ("e", "trema"),
    "à": ("a", "grave"), "â": ("a", "circ"), "ä": ("a", "trema"),
    "ù": ("u", "grave"), "û": ("u", "circ"), "ü": ("u", "trema"),
    "ô": ("o", "circ"), "ö": ("o", "trema"),
    "î": ("i", "circ"), "ï": ("i", "trema"),
    "ç": ("c", "cedille"),
    "É": ("E", "aigu"), "È": ("E", "grave"), "Ê": ("E", "circ"), "Ë": ("E", "trema"),
    "À": ("A", "grave"), "Â": ("A", "circ"), "Ô": ("O", "circ"), "Î": ("I", "circ"),
    "Ï": ("I", "trema"), "Ù": ("U", "grave"), "Û": ("U", "circ"), "Ç": ("C", "cedille"),
}

# Motifs de 3 colonnes centrés sur la lettre ; "X" = pixel allumé.
MOTIFS = {
    "aigu": ["..X", ".X."],
    "grave": ["X..", ".X."],
    "circ": [".X.", "X.X"],
    "trema": ["X.X"],
    "cedille": [".X.", "X.."],
}

Bitmap = list[list[int]]


def _encre(rows: Bitmap) -> tuple[int, int, int, int] | None:
    pts = [(y, x) for y, r in enumerate(rows) for x, v in enumerate(r) if v]
    if not pts:
        return None
    ys = [p[0] for p in pts]
    xs = [p[1] for p in pts]
    return min(ys), max(ys), min(xs), max(xs)


def sans_point(rows: Bitmap) -> Bitmap:
    """i -> ı : efface tout ce qui est au-dessus du premier vide en partant du bas."""
    out = [list(r) for r in rows]
    vu_encre = False
    for y in range(len(out) - 1, -1, -1):
        if any(out[y]):
            vu_encre = True
        elif vu_encre:
            for yy in range(y + 1):
                out[yy] = [0] * len(out[yy])
            break
    return out


def composer(base: Bitmap, accent: str, lettre: str = "") -> Bitmap | None:
    """Renvoie le glyphe accentué, ou None s'il n'y a pas la place."""
    rows = sans_point(base) if lettre.lower() == "i" else [list(r) for r in base]
    boite = _encre(rows)
    if boite is None:
        return None
    haut, bas, gauche, droite = boite
    motif = MOTIFS[accent]
    h, w = len(rows), len(rows[0])
    centre = (gauche + droite + 1) // 2
    x0 = max(0, min(w - 3, centre - 1))
    if accent == "cedille":
        y0 = bas + 1
        if y0 + len(motif) > h:
            y0 = h - len(motif)
            if y0 <= bas - 1:
                return None
    else:
        y0 = haut - 1 - len(motif)       # une ligne de vide entre accent et lettre
        if y0 < 0:
            return None
    for dy, ligne in enumerate(motif):
        for dx, c in enumerate(ligne):
            if c == "X":
                rows[y0 + dy][x0 + dx] = 1
    return rows


def depuis_octets(data: bytes, largeur: int, hauteur: int) -> Bitmap:
    """Bitmap 1 bit/pixel, bit de poids fort à gauche, lignes contiguës."""
    return [[(data[(y * largeur + x) >> 3] >> (7 - ((y * largeur + x) & 7))) & 1
             for x in range(largeur)] for y in range(hauteur)]


def vers_octets(rows: Bitmap) -> bytes:
    h, w = len(rows), len(rows[0])
    out = bytearray((w * h + 7) // 8)
    for y in range(h):
        for x in range(w):
            if rows[y][x]:
                k = y * w + x
                out[k >> 3] |= 1 << (7 - (k & 7))
    return bytes(out)
