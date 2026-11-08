# Feuille de route

Ce qui reste à faire, dans l'ordre où ça débloque le plus de monde.

## 1. Brancher la police française — *bloquant pour les accents*

Le texte de `trad/` s'écrit avec ses accents, mais tant que la police
française n'est pas branchée, `outils/injecter.py` les translittère
(« é » → « e ») pour que le build de Roman215 fonctionne.

- [ ] Récupérer le travail de police de gc-ultimate117 et le comparer à
      [police/accents.py](../police/accents.py) (composition automatique).
- [ ] Choisir les emplacements SJIS libres des glyphes accentués dans les
      polices 12×12 (dialogues, menus) et 10×10 (plaques de nom).
- [ ] Étendre `fullwidth()` et la table de l'afficheur ASCII des textes système.
- [ ] Vérifier le rendu en jeu (dialogue, menu, écran de statut, sauvegarde),
      puis passer `--accents garder` par défaut.

Détails : [police/README.md](../police/README.md).

## 2. Premier build complet en jeu

- [ ] Lancer `outils/injecter.py` puis `build.py` sur une image Rev 1, et
      vérifier que les tables à taille fixe passent (menus, noms, PNJ) avec
      les traductions actuelles.
- [ ] Parcourir le début du jeu (Okamoto, Virtual Battle, Colisée) et
      corriger les lignes trop larges.
- [ ] Faire des captures pour le README (`assets/captures/`).

## 3. Traduction — par ordre d'utilité

| Priorité | Fichiers | Pourquoi |
|---|---|---|
| ✅ fait | `dialogues/0x00xx` | texte système partagé : COMP, fusion, portes, boutiques |
| 1 | `menus/`, `systeme/` | visibles en permanence, ils fixent le vocabulaire |
| 2 | `dialogues/0x01xx` → `0x03xx` | le début du jeu (Valhalla, Okamoto, Colisée) |
| 3 | `noms/objets`, `noms/sorts` (noms descriptifs) | boutiques et combats |
| 4 | `cartes/lieux`, `noms/races` | après décision sur le Dictionnaire |
| 5 | `dialogues/0x10xx` → `0x31xx` | le reste de l'histoire |
| 6 | `dialogues/0x40xx` → `0x50xx` | négociations avec les démons (codes `{A..}`) |
| 7 | `dialogues/0x60xx` → `0x70xx` | divers |

Les noms de démons et de sorts d'Atlus restent tels quels : `noms/demons`
et la plupart de `noms/sorts` n'ont qu'une poignée d'entrées à traduire.

## 4. Textes encore hors de `trad/`

Ces textes anglais vivent dans d'autres fichiers de Roman215. Ils ne sont
pas encore extraits : il faudra ajouter leurs tables à `outils/commun.py`
(ou des correctifs à `outils/injecter.py`).

| Fichier amont | Contenu |
|---|---|
| `tools/opening_movie.py` | sous-titres de la vidéo d'introduction (Charon…) |
| `tools/rdlogo.py` | avertissement « œuvre de fiction » au démarrage |
| `tools/overlay_text.py` | messages du COMP et aides ajoutés par Roman215 |
| `tools/compendium.py` | libellés du Compendium |
| `tools/build_prod_exe.py`, `build.py` | quelques chaînes isolées (« Your drink? », « Use it on whom? »…) |
| `sys_strings.py` → `_COMPOSED_SLOTS` | « Dismiss … ? », « Discard … ? » composés à la volée |
| `name_entry.py`, `status_screen.py` | écrans en image : textures à redessiner |

## 5. Questions ouvertes pour l'équipe

- Les termes 💬 du [Dictionnaire](Dictionnaire.md) : *Underworld*, HP/MP,
  les races, les états FLY/BAT.
- `{OT}` dans les messages du terminal (0x004c, 0x004e, 0x0050) : quel texte
  insère-t-il exactement ? Ces trois lignes attendent la réponse.
- Faut-il garder les surnoms anglais des combattants (Red Bear, Killer Tsune) ?
