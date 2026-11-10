"""Aperçu PNG des accents composés sur la police 8x10 de Roman215.

    python police/apercu.py      # -> police/apercu_8x10.png

Seule la police 8x10 (minuscules de l'afficheur ASCII) est publiée dans
l'amont, sous amont/tools/lowercase_font_patch.json ; les polices 12x12 et
10x10 sont dans l'exécutable du jeu et ne peuvent être prévisualisées
qu'au moment du build.
"""

import json
import struct
import sys
import zlib
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import accents as A

ECHELLE = 6
FOND = (0x14, 0x10, 0x0A)
ENCRE = (0xE8, 0xD9, 0xB0)
ACCENT = (0xCE, 0x11, 0x26)


def police_8x10():
    patch = json.loads((ICI.parent / "amont" / "tools" / "lowercase_font_patch.json").read_text())
    octets = [bytes.fromhex(v) for _, v in sorted(patch.items(), key=lambda kv: int(kv[0], 16))]
    return {chr(ord("a") + i): A.depuis_octets(b, 8, 10) for i, b in enumerate(octets)}


def png(chemin, pixels):
    h, w = len(pixels), len(pixels[0])
    brut = b"".join(b"\x00" + bytes(c for px in ligne for c in px) for ligne in pixels)

    def bloc(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    chemin.write_bytes(b"\x89PNG\r\n\x1a\n" + bloc(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                       + bloc(b"IDAT", zlib.compress(brut, 9)) + bloc(b"IEND", b""))


def main():
    pol = police_8x10()
    lettres = [c for c in A.ACCENTS if c.islower()]
    cellules = []
    for c in lettres:
        base, acc = A.ACCENTS[c]
        g = A.composer(pol[base], acc, base)
        lettre = A.sans_point(pol[base]) if base == "i" else pol[base]
        cellules.append((lettre, g))
    marge, pas = 2, 10
    w = (marge * 2 + len(cellules) * pas) * ECHELLE
    h = (marge * 2 + 10) * ECHELLE
    img = [[FOND] * w for _ in range(h)]
    for i, (base, g) in enumerate(cellules):
        for y in range(10):
            for x in range(8):
                if not g[y][x]:
                    continue
                col = ENCRE if base[y][x] else ACCENT
                for dy in range(ECHELLE):
                    for dx in range(ECHELLE):
                        img[(marge + y) * ECHELLE + dy][(marge + i * pas + x) * ECHELLE + dx] = col
    sortie = ICI / "apercu_8x10.png"
    png(sortie, img)
    print(f"{sortie}  ({' '.join(lettres)})")


if __name__ == "__main__":
    main()
