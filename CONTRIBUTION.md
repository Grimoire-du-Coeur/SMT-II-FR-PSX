# 🤝 Contribuer au projet SMT-II-FR-PSX

Merci de votre intérêt pour le projet de traduction française de **Shin Megami Tensei II (PlayStation)** !

Afin de garder une organisation propre et d'éviter que plusieurs personnes écrasent accidentellement le travail des autres, certaines règles doivent être respectées avant toute contribution.

---

# 🌐 Organisation du projet

Pour participer à la traduction, il est **obligatoire de rejoindre le serveur Discord MegaTen [FR]**.

Le serveur permet de :

- organiser la répartition des fichiers entre traducteurs ;
- discuter des choix de traduction ;
- éviter que plusieurs personnes travaillent sur le même fichier en même temps ;
- partager les tests et les retours ;
- suivre l'avancement du projet.

Lien du serveur :

https://discord.gg/anbTYCsK7Y

Avant de commencer la traduction d'un fichier, merci de prévenir l'équipe afin de vérifier qu'il n'est pas déjà attribué à quelqu'un d'autre.

---

# 📌 Comment contribuer sur GitHub

## 1. Créer une Fork du projet

Une **Fork** est une copie du dépôt sur votre propre compte GitHub.

Pour en créer une :

1. Rendez-vous sur la page du dépôt GitHub.
2. Cliquez sur **Fork** en haut à droite.
3. Sélectionnez votre compte GitHub.
4. Une copie du projet sera créée sur votre compte.

Vous pourrez alors effectuer vos modifications sur votre propre copie du projet sans modifier directement le dépôt principal.

---

# ✏️ Modifier les fichiers

Deux méthodes sont possibles.

---

## Option 1 — Modifier directement sur GitHub

GitHub permet de modifier les fichiers depuis votre navigateur.

Pour cela :

1. Ouvrez le fichier que vous souhaitez modifier.
2. Cliquez sur l'icône ✏️ **Edit this file**.
3. Effectuez vos traductions.
4. Cliquez sur **Commit changes**.

Cette méthode convient pour des petites corrections ou des modifications rapides.

---

## Option 2 — Utiliser un éditeur de texte (recommandé)

Pour traduire des fichiers entiers, il est fortement recommandé d'utiliser un éditeur de texte.

Logiciels conseillés :

- **Notepad++**
- **Visual Studio Code**

Téléchargement officiel de Notepad++ :

https://notepad-plus-plus.org/downloads/

Notepad++ est recommandé pour ce projet grâce à sa simplicité, sa recherche rapide et sa bonne gestion des fichiers texte volumineux.

---

# 📤 Envoyer ses modifications

Après avoir terminé vos modifications sur votre Fork :

```bash
git add .
git commit -m "Description des changements"
git push
```

Ensuite, vous pourrez créer une Pull Request afin de proposer vos changements au dépôt principal.

---

# 📩 Créer une Pull Request

Une **Pull Request** permet de proposer votre travail afin qu'il soit vérifié puis intégré au projet.

Pour en créer une :

1. Allez sur votre Fork GitHub.
2. Cliquez sur **Contribute** puis **Open pull request**.
3. Vérifiez que le dépôt de destination est bien **SMT-II-FR-PSX**.
4. Décrivez les fichiers ou parties traduites.
5. Envoyez la Pull Request.

L'équipe vérifiera votre travail avant intégration.

---

# 📝 Guide de traduction SMT2 FR

## Fonctionnement général

Chaque fichier contient généralement :

- une ligne anglaise servant de référence ;
- une ligne française commentée avec un `#` à remplir.

Exemple :

```python
0x0001:["You cannot use the COMP now.",'WT','ED'],
#0x0001:["",'WT','ED'],
```

Pendant toute la phase de traduction :

- le `#` doit rester présent ;
- la ligne anglaise ne doit jamais être supprimée ;
- seules les traductions françaises doivent être modifiées.

L'intégration finale des traductions sera effectuée après validation.

---

# ⚠️ Règles communes

Ces règles s'appliquent à tous les fichiers.

## Ne jamais modifier la structure

Ne supprimez jamais une ligne anglaise.

Elle sert de référence pour la traduction et la vérification.

Ne modifiez jamais :

- les clés (`0x0001:`, `97:`, `0x0bc0:`...) ;
- les virgules ;
- les crochets ;
- les parenthèses ;
- les deux-points ;
- les guillemets.

---

# 🎮 Codes de contrôle

Conservez exactement les codes présents dans la ligne anglaise :

```text
'WT'
'ED'
'CR'
'SY'
'SN'
'PG'
'Fe'
```

Ces codes ne sont pas du texte.

Ils servent au fonctionnement du jeu et ne doivent jamais être :

- traduits ;
- déplacés ;
- supprimés ;
- ajoutés.

Les codes comme :

```text
(0xc095,True)
```

doivent également rester identiques.

---

# 📐 Formatage

Gardez toujours :

- la même indentation ;
- les mêmes espaces importants ;
- les mêmes marqueurs spéciaux.

Conservez :

- `@` dans les noms de cartes ;
- `\n` dans les descriptions ;
- `>` au début des textes de narration ;
- `ћ` pour la monnaie Macca.

---

# ✨ Police française et accents

Une **police française personnalisée** a été créée spécialement pour ce projet.

Elle est compatible avec les outils développés par **Roman215** et permet l'affichage des caractères français nécessaires à la traduction.

Elle permet notamment l'utilisation de caractères comme :

```
é è ê à ç ù ô ï
```

Cependant, certains fichiers possèdent des limitations techniques.

Avant d'utiliser des accents, vérifiez toujours que le fichier concerné les accepte.

Certains textes système utilisent un format limité à l'ASCII simple et peuvent provoquer une erreur lors de la compilation.

---

# 📖 translations_FR.py — Dialogues

Ce fichier contient la majorité des dialogues du jeu.

Exemple :

```python
0x0001:["You cannot use the COMP now.",'WT','ED'],
#0x0001:["",'WT','ED'],
```

Pour traduire :

1. Gardez le `#`.
2. Remplissez le texte entre les guillemets.
3. Ne modifiez pas la ligne anglaise.

Résultat :

```python
0x0001:["You cannot use the COMP now.",'WT','ED'],
#0x0001:["Vous ne pouvez pas utiliser le COMP maintenant.",'WT','ED'],
```

---

# Codes dans les dialogues

Certains codes insèrent automatiquement des informations du jeu.

Exemples :

- `SY`
- `SN`
- `Fe`

Ils peuvent remplacer un nom de démon, un personnage ou une valeur.

Gardez-les au même endroit logique dans la phrase française.

---

# 📚 Dictionnaires

Les dictionnaires fonctionnent avec des clés.

Exemples de fichiers :

| Fichier | Dictionnaire |
|-|-|
| `menu_table_FR.py` | `MENU` |
| `name_tables_FR.py` | `TRAITS_MAP` |
| `sys_strings_FR.py` | `SYS`, `RETRANSLATED`, `ASCII_FIT_ENGLISH`, `AUDITED_SYSTEM_TEXT` |

Pour traduire :

Remplissez uniquement le texte français après le `#`.

Ne modifiez jamais :

- les clés ;
- les adresses ;
- les nombres ;
- les caractères japonais servant de référence.

---

# 📋 Listes

Certains fichiers utilisent des listes où l'ordre est extrêmement important.

Fichiers concernés :

| Fichier | Liste |
|-|-|
| `map_names_FR.py` | `ENGLISH` |
| `name_tables_FR.py` | `DEMONS`, `RACES`, `SPELLS`, `ITEMS`, `LOCATIONS`, `NPCS`, `DRINKS` |
| `menu_table_FR.py` | `AB_MENU` |
| `party_names_FR.py` | `NAMES` |

Règles :

- Ne supprimez aucune entrée.
- Ne changez pas l'ordre.
- Ne déplacez pas les éléments.
- Gardez les `None`.
- Gardez les doublons.

Chaque élément doit rester à sa position originale.

---

# 📏 Longueur des textes

Le français est souvent plus long que l'anglais.

Faites attention aux limites :

- menus ;
- noms de sorts ;
- noms d'objets ;
- noms de lieux ;
- dialogues.

Utilisez des abréviations si nécessaire.

Le but est de garder un texte lisible qui rentre correctement dans l'interface du jeu.

---

# ✅ Vérification avant Pull Request

Avant d'envoyer votre travail :

- [ ] Le `#` est toujours présent sur les traductions françaises.
- [ ] Les lignes anglaises originales sont intactes.
- [ ] Aucun numéro de clé n'a été modifié.
- [ ] Aucun code de contrôle n'a été modifié.
- [ ] Aucun guillemet, crochet ou virgule ne manque.
- [ ] Les listes gardent exactement le même nombre d'éléments.
- [ ] Les accents utilisés sont compatibles avec le fichier.
- [ ] Le travail a été annoncé sur MegaTen [FR].

Merci de contribuer à rendre **Shin Megami Tensei II (PSX)** accessible aux joueurs francophones !
