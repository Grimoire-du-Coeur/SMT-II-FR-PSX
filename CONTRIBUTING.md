# Contribuer à SMT-II-FR-PSX

Merci de vouloir aider à traduire *Shin Megami Tensei II* ! Ce guide tient
en trois idées :

1. **On s'organise sur Discord** avant de traduire.
2. **On ne touche qu'aux champs `"fr"`** des fichiers de `trad/`.
3. **Un terme se traduit toujours pareil** : le [Dictionnaire](docs/Dictionnaire.md) fait foi.

---

## 1. Avant de commencer

Rejoins le Discord **[MegaTen \[FR\]](https://discord.gg/anbTYCsK7Y)** et
annonce le fichier que tu prends (par exemple `trad/dialogues/0x02xx.json`).
Ça évite que deux personnes traduisent la même page, et c'est là qu'on
discute des choix de traduction.

## 2. Le format d'un fichier

Chaque fichier de `trad/` est une liste d'entrées :

```json
{
  "id": "0x0008",
  "en": "Its alignment is incompatible.{CR}It cannot be summoned.{ED}",
  "fr": "Son alignement est incompatible.{CR}Impossible de l'invoquer.{ED}"
}
```

| Champ | Rôle | Tu peux le modifier ? |
|---|---|---|
| `id` | repère de l'entrée dans le jeu | **non** |
| `en` | le texte anglais de Roman215, ta référence | **non** |
| `fr` | ta traduction ; vide = l'anglais reste en jeu | **oui** |
| `note` | contexte laissé par Roman215 dans son code | non |
| `max_octets` | place disponible dans le jeu (textes système) | non |
| `a_revoir` | l'anglais a changé depuis ta traduction : relis, puis supprime ce champ | oui (le supprimer) |
| `commentaire` | une note libre pour les relecteurs | oui |

Un fichier **peut être traduit à moitié** : une entrée vide garde son
anglais en jeu. Envoie ton travail par petits morceaux plutôt qu'en une
fois.

## 3. Les balises

Les dialogues contiennent des balises entre accolades. **Ce ne sont pas du
texte** : il faut les garder toutes, **dans le même ordre**, sans en
ajouter ni en retirer. Le validateur refuse une traduction dont les
balises diffèrent de l'anglais.

| Balise | Effet |
|---|---|
| `{CR}` | retour à la ligne |
| `{WT}` | attend que le joueur appuie sur un bouton |
| `{PG}` | efface la boîte (nouvelle page) |
| `{ED}` | fin du message |
| `{SY}` `{MG}` `{IT}` `{AL}` `{MH}` `{ZK}` `{SE}` `{PP}` `{OT}`… | insèrent un nom (personnage, démon, objet, sort, race…) |
| `{AG}` | insère le nom du chef du groupe (en français, le nom seul : accorde le verbe au singulier) |
| `{A0F}` `{A65}`… | codes des négociations avec les démons |
| `{0xc095,True}` | symbole spécial du jeu (curseur, icône) |

Tu peux déplacer le **texte** autour d'une balise d'insertion pour que la
phrase sonne bien en français, tant que l'**ordre des balises** reste le
même. Exemple :

```text
en : Dismiss {MG}?{ED}
fr : Congédier {MG}?{ED}
```

Les lignes de narration commencent par `>` : garde-le. Le symbole `ћ` est
la monnaie (Macca) : `ћ200`.

## 4. La place à l'écran

- **Dialogues : environ 30 caractères par ligne**, trois lignes par boîte.
  Le français est plus long que l'anglais : coupe avec `{CR}` aux mêmes
  endroits que l'anglais, et resserre la phrase plutôt que de déborder.
  Comme les balises doivent rester identiques, on ne peut pas ajouter de
  `{CR}` : si ça ne rentre pas, reformule.
- **Menus, noms, objets, sorts** : vise une longueur proche de l'anglais.
  Ces textes vivent dans des tables de taille fixe. Le validateur signale
  ceux qui sont plus longs, et le build refuse ceux qui ne rentrent pas.
- **Noms du groupe** (`trad/equipe/`) : 8 caractères au maximum.

## 5. Les règles d'écriture

### Typographie (comme Persona 1 FR)

| | On écrit | On n'écrit pas |
|---|---|---|
| Avant `!` `?` `:` | `Invoquer qui?` | ~~`Invoquer qui ?`~~ |
| Guillemets | `"comme ça"` | ~~`« comme ça »`~~ |
| Apostrophe | `qu'une` | ~~`qu’une`~~ |
| Ligature | `coeur`, `soeur` | ~~`cœur`~~ (pas de glyphe `œ`) |

Ce n'est pas la typographie française idéale, c'est un choix assumé : la
place est comptée et la cohérence prime. Les **accents**, eux, s'écrivent
normalement (`é è ê à â ù û ô î ï ç`), même si la police française n'est
pas encore branchée (voir [police/README.md](police/README.md)).

### Le ton

- **Système et narration** (COMP, menus, lignes `>`) : on **vouvoie** le
  joueur. « Votre inventaire est plein. »
- **Personnages** : chacun garde sa voix. Okamoto tutoie Hawk, les
  marchands vouvoient leurs clients, les démons parlent selon leur
  caractère (le Dictionnaire liste les cas déjà tranchés).
- **Les tics de langage** se traduisent par un tic français équivalent
  (« it does! » → « c'est sûr! »), pas mot à mot.
- **Les bégaiements** restent : « W-What » → « Qu-Quoi ».
- **Ne corrige pas l'anglais.** Si une ligne de Roman215 te semble fausse,
  traduis le sens voulu et laisse un `commentaire`.

## 6. Envoyer sa traduction

**Depuis le navigateur** (le plus simple) : ouvre le fichier sur GitHub,
clique sur ✏️, remplis les `"fr"`, puis *Commit changes* → *Propose
changes*. GitHub crée la copie (fork) et la Pull Request pour toi.

**Avec Git** :

```bash
git clone --recursive https://github.com/<ton-compte>/SMT-II-FR-PSX.git
cd SMT-II-FR-PSX
git checkout -b trad-0x02xx
# ... remplis les "fr" ...
python outils/valider.py trad/dialogues/0x02xx.json
git commit -am "Traduction : dialogues 0x0200-0x02ff"
git push -u origin trad-0x02xx
```

Éditeurs conseillés : [VS Code](https://code.visualstudio.com/) ou
[Notepad++](https://notepad-plus-plus.org/downloads/). Enregistre toujours
en **UTF-8**.

## 7. La vérification automatique

À chaque Pull Request, `outils/valider.py` relit les fichiers modifiés et
pose ses remarques **directement sur les lignes** :

- **Erreur** (bloquant) : balises différentes de l'anglais, caractère
  absent de la police, JSON cassé, champ `en` ou `id` modifié, texte trop
  long pour son emplacement.
- **Avertissement** (à regarder) : ligne trop large, texte plus long que
  l'anglais, terme du Dictionnaire non respecté, espace avant `?`…

Tu peux lancer la même vérification chez toi avec Python 3.10+ :

```bash
python outils/valider.py              # tout le dépôt
python outils/valider.py trad/menus/commandes.json
```

## 8. Check-list avant la Pull Request

- [ ] Je n'ai modifié que des champs `"fr"` (et éventuellement `commentaire`).
- [ ] Les balises sont les mêmes, dans le même ordre, que dans `"en"`.
- [ ] J'ai suivi le [Dictionnaire](docs/Dictionnaire.md), ou j'y ai proposé le nouveau terme.
- [ ] Aucune ligne de dialogue ne dépasse ~30 caractères.
- [ ] Le fichier est annoncé sur MegaTen [FR].

Merci de rendre *Shin Megami Tensei II* accessible aux joueurs francophones !
