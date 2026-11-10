# Police française

<p align="center"><img src="apercu_8x10.png" alt="Lettres accentuées composées sur la police 8×10 de Roman215" width="100%"></p>

## Où on en est

| Étape | État |
|---|---|
| Jeu de caractères du projet ([caracteres.json](caracteres.json)) | ✅ défini, appliqué par le validateur |
| Composition des glyphes accentués ([accents.py](accents.py)) | ✅ écrite et testée sur des bitmaps |
| Branchement sur l'encodeur (`fullwidth()`) et les polices du jeu | ⏳ à faire, voir ci-dessous |
| Vérification en jeu | ⏳ à faire |

En attendant, `outils/injecter.py` translittère les accents (« é » → « e »).
**Le texte de `trad/` s'écrit quand même avec ses accents** : rien ne sera
à reprendre le jour où la police sera branchée.

## Le principe

Le jeu a trois polices bitmap :

| Police | Adresse | Sert à |
|---|---|---|
| 12×12 | `0x800d4188` dans l'exécutable | dialogues, menus |
| 10×10 | exécutable | plaques de nom (groupe, statut) |
| 8×10 demi-chasse | exécutable, minuscules de Roman215 | afficheur ASCII des textes système |

Plutôt que de dessiner chaque lettre accentuée trois fois, `accents.py`
part de la lettre de base déjà présente dans la police (et déjà crénée par
le build de Roman215). Il y pose l'accent au-dessus de l'encre, centré, en
laissant une ligne de vide. Le « i » perd son point avant de recevoir son
accent, et la cédille se place sous la lettre.

Une majuscule n'a en général pas la place d'un accent dans une cellule de
10 ou 12 pixels. `composer()` renvoie alors `None`, et le caractère sera
écrit sans accent (É → E), comme c'est l'usage dans beaucoup de jeux.

L'aperçu ci-dessus est généré par `python police/apercu.py` à partir de la
police 8×10 publiée par Roman215. Les polices 12×12 et 10×10 sont dans
l'exécutable du jeu : on ne peut les prévisualiser qu'au moment du build.

## Pour brancher la police

1. **Choisir les emplacements.** Il faut une plage de codes SJIS dont les
   glyphes ne servent pas en anglais (par exemple le grec `0x839F`–`0x83D6`).
   ⚠️ Roman215 utilise déjà une partie du cyrillique comme zone de code
   (`LINE_BREAK_CAVE`, `map_names.CAVES`) : ne pas y toucher.
2. **Écrire les glyphes au build**, après `kern_font()`. Pour chaque lettre
   de `ACCENTS`, lire le glyphe de base, appeler `composer()`, écrire le
   résultat dans l'emplacement choisi, puis calculer sa largeur avec la même
   fonction de crénage.
3. **Étendre `fullwidth()`** (`build_en_tree.py`) avec ces codes, et
   ajouter les accents à `build_freqs()` pour l'arbre de Huffman.
4. **Afficheur ASCII** : l'afficheur des textes système associe un octet à
   un glyphe. Il faut associer des octets libres (`0x80`–`0xFF`) aux mêmes
   lettres composées dans la police 8×10.
5. Passer ces modifications par `CORRECTIFS` dans `outils/injecter.py` (le
   code de l'amont n'est jamais modifié à la main), puis tester en jeu.

gc-ultimate117 a déjà travaillé sur une police française compatible avec
les outils de Roman215 : la première étape est de comparer son approche à
celle-ci et de garder la meilleure.
