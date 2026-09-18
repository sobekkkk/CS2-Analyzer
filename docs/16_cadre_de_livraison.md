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

## Definition of Done

Une fonctionnalite n'est terminee que si :

1. le code est relu et reste limite au besoin ;
2. les tests unitaires et d'integration pertinents passent ;
3. les contrats API et la documentation changent avec le code ;
4. lint et formatage sont verts ;
5. les donnees sensibles restent locales et pseudonymisees ;
6. le rollback ou la suppression locale sont compris ;
7. une demonstration sur une vraie demo est faite quand la fonctionnalite touche le parsing ou les regles ;
8. l'observabilite minimale existe : erreur structuree, version de regle et hash de source.

## Pyramide de tests

| Niveau | Attendu dans l'alpha |
| --- | --- |
| Unitaire | Obligatoire pour les regles, validations, transformations et securite de chemin |
| Integration | Obligatoire pour parser, stockage Parquet, API locale et staging temporaire |
| Contrat | OpenAPI fige avant branchement du front ; rupture intentionnelle documentee |
| E2E | Import -> selection -> rapport, avec Playwright des que le front existe |
| Accessibilite | Navigation clavier et assertions axe sur les parcours critiques front |
| Acceptation | Demo reelle et criteres de story, avec retour joueur a la beta |

La couverture est suivie comme signal secondaire. Aucun seuil global ne remplace des tests sur les regles H-01 a H-04 et les parcours a risque.

## Qualite et securite

- Backend : `ruff check`, `ruff format --check`, `pytest` a chaque PR et dans la CI.
- Frontend : lint TypeScript, tests de composants, Playwright et tests d'accessibilite a chaque parcours critique.
- Les demos et SteamID bruts ne sont ni commits ni envoyes dans la CI.
- Les dependances et les actions GitHub sont versionnees et revues.
- Toute vulnerabilite est traitee en dehors des issues publiques ; la politique `SECURITY.md` sera ecrite apres confirmation explicite du perimetre de signalement et de severite.

## Git et GitHub

- `main` est protegee : aucun push direct, PR obligatoire, CI verte avant fusion.
- Branches courtes : `codex/<sujet>` ou `feature/<sujet>` ; une branche ne vit pas plusieurs semaines.
- Toute PR indique objectif, test, impact securite, migration/rollback et captures si interface.
- Au moins une approbation avant merge ; deux pour parsing, stockage, secrets ou politique securite quand une equipe existe.
- Les fonctionnalites inachevees sont cachees derriere un feature flag local ; aucun demi-parcours n'est expose par defaut.

Apres le premier push, la configuration GitHub a appliquer sur `main` est :

- pull request obligatoire, avec au moins une approbation ;
- controle CI `quality` obligatoire et branche a jour avant fusion ;
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
