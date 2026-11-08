# Notes techniques

## Principe

```text
amont/tools/*.py  ──extraire.py──▶  trad/**.json  ──(traducteurs)──▶  trad/**.json
       │                                                                  │
       └─────────────────────────── injecter.py ◀─────────────────────────┘
                                         │
                                         ▼
                               build/smt2-fr/  ──build.py (Roman215)──▶  image FR + patch xdelta
```

- **`amont/`** est un sous-module Git figé sur une version publiée de
  [Roman215/smt2-psx-translation](https://github.com/Roman215/smt2-psx-translation)
  (actuellement `v0.2.3`).
- **`outils/commun.py`** lit les six modules de texte de l'amont avec `ast`.
  Chaque chaîne traduisible est repérée par sa position exacte (en octets)
  dans le source. La liste des tables est dans `TABLES`.
- **`outils/extraire.py`** écrit `trad/**.json`. Les dialogues (`TRANS`) sont
  rendus en une seule chaîne lisible, avec les contrôles en balises :
  `["Hi",'CR',"there.",'ED']` → `"Hi{CR}there.{ED}"`.
- **`outils/injecter.py`** copie l'amont dans `build/smt2-fr/` et remplace,
  à leur position exacte, les chaînes qui ont un `"fr"`. Pour un dialogue,
  il reconstruit la liste en reprenant le source d'origine de chaque
  contrôle, puis vérifie que les modules générés se chargent.
- **`outils/valider.py`** fait les contrôles décrits dans CONTRIBUTING.md.
  Il importe `build_en_tree.fullwidth()` de l'amont : le jeu de caractères
  autorisé est exactement celui de l'encodeur.
- **`outils/stats.py`** produit `SUIVI.md`, les badges et le bloc
  d'avancement du README.

Le code de Roman215 n'est jamais modifié dans ce dépôt. Les rares
correctifs que le français impose (le suffixe `'s party` de `{AG}`, par
exemple) sont dans `CORRECTIFS` de `injecter.py`. Ce sont des
remplacements exacts : l'injection s'arrête si l'amont change ce passage.

## Monter de version l'amont

```bash
cd amont
git fetch --tags
git checkout v0.2.4            # la nouvelle version
cd ..
python outils/extraire.py      # met à jour les "en", signale les "a_revoir"
python -m pytest tests
python outils/valider.py
git add amont trad
git commit -m "Amont : passage à la v0.2.4 de Roman215"
```

`extraire.py` ne perd jamais une traduction :

- **l'anglais a changé** : le français est gardé et `"a_revoir"` contient
  l'ancien anglais ;
- **l'entrée a disparu** : elle part dans `trad/_orphelins.json` ;
- **nouvelle entrée** : elle arrive avec `"fr": ""`.

## Construire

```bash
git submodule update --init
python outils/injecter.py                 # --accents garder quand la police sera branchée
cd build/smt2-fr
python build.py --input "…/Shin Megami Tensei II (Japan) (Rev 1).bin"
```

Les options de `build.py` (vidéos, gameplay, xdelta, `release.py`) sont
documentées dans le README de l'amont.

## Tests

```bash
python -m pip install pytest
python -m pytest tests
```

Les tests vérifient notamment :

- l'aller-retour extraire → injecter (sans traduction, l'amont est
  reproduit à l'octet près) ;
- le remplacement au bon endroit pour chaque genre de table ;
- le refus de balises différentes ;
- la composition des accents.

## Bon à savoir sur le moteur

- **Dialogues** : arbre de Huffman 16-aire reconstruit par le build, avec un
  dictionnaire extrait du corpus. Un texte plus long ne casse rien tant que
  les banques tiennent : c'est le build qui vérifie.
- **Tables de noms** (`name_tables.py`) : réencodées **en place**. Un nom
  trop long fait échouer le build. `NPCS` est le cas le plus serré, car des
  données de combat le suivent.
- **Textes système** (`sys_strings.py`) : chaque texte reste dans son
  emplacement d'origine (`max_octets`). Ils passent par un afficheur ASCII,
  1 octet par caractère, avec le marqueur `0x1f`.
- **Polices** : 12×12 à `0x800d4188` (dialogues, menus), 10×10 (plaques de
  nom), 8×10 en demi-chasse (afficheur ASCII, minuscules ajoutées par
  Roman215).
