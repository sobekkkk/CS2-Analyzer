# Cadre de livraison - agile pragmatique

## Rythme adapte au projet

Le projet suit un **Kanban pilote par la valeur et le risque**, avec une revue toutes les deux semaines. Cela garde la souplesse d'un projet en construction tout en donnant le rythme d'un sprint.

- Chaque item est une petite tranche livrable, de preference en moins de trois jours.
- Limite de travail en cours : une fonctionnalite backend et une fonctionnalite frontend au maximum.
- Revue de livraison : demonstration sur une vraie demo, jamais seulement sur des maquettes.
- Retrospective : noter une amelioration concrete du processus apres chaque lot significatif.
- Le backlog est priorise par : valeur joueur, risque de faux positif, dependances, effort.

## Etats du backlog

`idee` -> `pret` -> `en_cours` -> `revue` -> `termine` -> `mesure`

Un element bloque porte la cause et la prochaine action. Les labels GitHub sont : `feature`, `bug`, `security`, `technical-debt`, `documentation`, `incident`, `blocked` et `good-first-issue`.

## Definition of Ready

Une story peut commencer si elle contient :

- valeur joueur et critere d'acceptation ;
- impact donnees / vie privee identifie ;
- exemple de demo ou fixture permettant de la tester ;
- dependances et risque principal connus ;
- comportement attendu en cas de donnees insuffisantes.
- niveau de test automatise attendu et exemple observable de sortie (contrat API, regle ou parcours interface).

## Regle TDD : red -> green -> refactor

Chaque changement de comportement suit ce cycle, y compris lorsqu'il est developpe avec une IA :

1. ecrire le critere d'acceptation et l'exemple concret de sortie attendue ;
2. ecrire le test automatise correspondant **avant** l'implementation et constater son echec ;
3. implementer le minimum necessaire pour le faire passer ;
4. refactorer seulement avec toute la suite verte ;
5. executer les controles locaux pertinents avant le push ;
6. pousser une branche courte, laisser la CI refaire les memes controles, puis ne fusionner que si elle est verte.

Un bug constate sur une vraie demo commence par un test de non-regression qui reproduit le cas, puis seulement par le correctif. Les fixtures sont pseudonymisees et minimales : aucune demo brute ne sert de donnee de CI.

Le TDD ne remplace pas une validation manuelle de l'interface ni une lecture de replay ; il garantit que les comportements deja specifies ou deja rencontres ne regressent pas silencieusement.

## Definition of Done

Une fonctionnalite n'est terminee que si :

1. le code est relu et reste limite au besoin ;
2. les tests unitaires et d'integration pertinents passent ;
3. le test ayant defini le comportement a ete ecrit avant le code, ou l'exception (documentation, style sans comportement) est justifiee dans la PR ;
4. les contrats API et la documentation changent avec le code ;
5. lint et formatage sont verts ;
6. les donnees sensibles restent locales et pseudonymisees ;
7. le rollback ou la suppression locale sont compris ;
8. une demonstration sur une vraie demo est faite quand la fonctionnalite touche le parsing ou les regles ;
9. l'observabilite minimale existe : erreur structuree, version de regle et hash de source.

## Pyramide de tests

| Niveau | Attendu dans l'alpha |
| --- | --- |
| Unitaire | Obligatoire pour les regles, validations, transformations et securite de chemin |
| Integration | Obligatoire pour parser, stockage Parquet, API locale et staging temporaire |
| Contrat | OpenAPI fige avant branchement du front ; rupture intentionnelle documentee |
| E2E | Import -> selection -> rapport, avec Playwright dans Chromium ; API mockee pour rendre le parcours deterministe |
| Accessibilite | Navigation clavier et assertions axe sur les parcours critiques front |
| Acceptation | Demo reelle et criteres de story, avec retour joueur a la beta |

La couverture est suivie comme signal secondaire. Aucun seuil global ne remplace des tests sur les regles H-01 a H-04 et les parcours a risque.

## Qualite et securite

- Backend : `ruff check`, `ruff format --check`, `pytest` a chaque PR et dans la CI.
- Frontend : lint TypeScript, tests de composants, Playwright dans Chromium et tests d'accessibilite a chaque parcours critique.
- Les demos et SteamID bruts ne sont ni commits ni envoyes dans la CI.
- Les dependances et les actions GitHub sont versionnees et revues.
- Toute vulnerabilite est traitee en dehors des issues publiques ; la politique `SECURITY.md` sera ecrite apres confirmation explicite du perimetre de signalement et de severite.

## Git et GitHub

- `main` est protegee : aucun push direct, PR obligatoire, CI verte avant fusion.
- Branches courtes : `codex/<sujet>` ou `feature/<sujet>` ; une branche ne vit pas plusieurs semaines.
- Toute PR indique objectif, test, impact securite, migration/rollback et captures si interface.
- En phase solo : PR et CI verte obligatoires, mais aucune approbation ne peut etre imposee sans se bloquer soi-meme. Des le premier contributeur supplementaire : une approbation est obligatoire ; deux pour parsing, stockage, secrets ou politique securite.
- Les fonctionnalites inachevees sont cachees derriere un feature flag local ; aucun demi-parcours n'est expose par defaut.

Apres le premier push, la configuration GitHub a appliquer sur `main` est :

- pull request obligatoire ; activer une approbation obligatoire des l'arrivee d'un second contributeur ;
- controles CI `API quality and tests`, `Web quality and tests` et `Web end-to-end tests` obligatoires et branche a jour avant fusion ;
- pas de force-push, pas de suppression de branche par erreur ;
- revues CODEOWNERS obligatoires des qu'il y a plus d'un contributeur.

Les types d'issues demarrent avec `bug`, `feature`, `documentation`, `security`,
`technical-debt`, `incident` et `triage`. Les formulaires inclus imposent de
decrire un probleme reproductible ou une valeur joueur mesurable.

## Indicateurs utiles

- lead time d'un item `pret` a `termine` ;
- nombre d'elements bloques et temps de blocage ;
- regressions detectees par CI avant fusion ;
- bugs echappes apres demonstration ;
- frequence de livraison et taux de rework de regles analytiques.

Ces indicateurs servent a ameliorer le flux, jamais a gonfler artificiellement la vitesse.
