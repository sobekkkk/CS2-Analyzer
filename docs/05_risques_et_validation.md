# Risques et plan de validation

## Risques principaux

| Risque | Consequence | Mitigation avant lancement code |
| --- | --- | --- |
| Patch CS2 casse le parser | Analyse fausse ou indisponible | Isoler l'adaptateur, stocker la version, corpus multi-patches |
| Demo POV incomplete/differente | Faux diagnostic | Declarer la provenance, prioriser demos CSTV/compatibles, tests de cas limites |
| "No trade" mal interprete | Perte de confiance | Employer "pas de trade possible estime", montrer distance/delai et permettre le feedback |
| Coordonnees map incorrectes | Heatmaps inutiles | Valider visuellement 20 points connus par carte |
| Parsing de fichier hostile | Crash, ressource epuisee | Worker isole, taille/CPU/RAM/timeout limites |
| Vie privee | Donnees perso exposees | Local par defaut, pseudonymisation, aucun voice/chat |
| Perimetre qui explose | Projet jamais fini | MVP mono-carte et 4 questions de heatmap |
| Rejet legal/fair-play | Risque produit | Post-match hors processus, audit des conditions Valve avant commercialisation |

## Corpus golden obligatoire

Constituer legalement un dossier prive de 10 demos, sans les redistribuer sans autorisation. Le premier lot Vitality/Mirage est enregistre dans [`corpus/manifest.v0.yml`](corpus/manifest.v0.yml). Il apporte de bons cas professionnels homogenes, mais ne suffit pas seul : ajouter ensuite des parties de niveaux, de patches et de sources differents.

Objectif de corpus complet :

- 3 matchmaking/Premier recents ;
- 2 demos FACEIT ou autre plateforme (si autorisees) ;
- 1 match avec overtime ;
- 1 match avec pause/timeout ;
- 1 demo POV pour tester les limites ;
- 1 demo volontairement tronquee ;
- 1 demo issue d'un ancien patch raisonnable.

Pour chaque demo, creer une fiche manuelle : score, rounds, joueurs, kills, 5 morts du joueur cible, 5 damages et 3 situations 5v4. Cette fiche devient la reference de test, pas une intuition.

## Validation de chaque regle

1. Ecrire la regle dans `02_regles_analytics.md` avant le code.
2. Etiqueter 20 a 30 exemples manuellement sur les demos golden.
3. Executer la regle.
4. Classer les sorties : vrai positif, acceptable mais incomplet, faux positif, donnees insuffisantes.
5. Ajuster un seuil uniquement avec une note de decision.
6. Montrer 5 resultats a des joueurs et demander "utile ? comprehensible ? juste dans le contexte ?".

## Criteres de qualite avant beta

- 0 crash sur le corpus golden.
- Score final, nombre de rounds et kills egalent la reference pour chaque demo supportee.
- 100 % des observations ont des preuves navigables.
- Aucune heatmap ne cache son echantillon `n`.
- Les cas ambigus sont marques "a verifier" ou absents.
- Suppression locale d'un match possible et verifiee.

## Decision log a tenir

Pour chaque decision durable, conserver : date, contexte, options, choix, raison, consequence. Exemples : seuil trade, cartes supportees, conservation des demos, choix de parser. Cela evitera de rediscuter des suppositions une fois le code lance.
