# Politique IA locale et gratuite

## Decision recommandee

**Oui a une IA locale, mais pas dans le moteur de verite du MVP.**

Le produit reste utile sans modele de langage : les faits, heatmaps, seuils et "opportunites de progression" sont calcules par des regles deterministes. Une IA peut ensuite reformuler ces resultats en debrief naturel, adapter le ton ou repondre a une question portant sur des faits deja calcules.

Cette separation est essentielle : un LLM est tres bon pour expliquer, beaucoup moins fiable pour deduire seul une position, une ligne de vue ou une "mauvaise decision" a partir de millions de ticks.

## Ce que l'IA pourrait faire gratuitement

| Usage | Pertinence | Quand |
| --- | --- | --- |
| Transformer une `Insight` structuree en francais clair | Forte | Apres MVP analytics |
| Choisir les 3 constats a expliquer, parmi un score deterministe | Forte | Apres calibration des regles |
| Repondre : "pourquoi cette alerte ?" avec ses preuves | Forte | Apres MVP |
| Inventer une analyse directe de la demo | Faible / risquee | Hors perimetre |
| Evaluer le crosshair, la vision ou l'intention sans donnees structurees | Non | Hors perimetre |

## Solution sans cout d'API

Executer un modele ouvert **en local** avec Ollama, qui peut telecharger et executer des modeles sur l'ordinateur et expose une API locale compatible avec l'application. Les poids Qwen3 sont disponibles en tailles allant de tres petites a grandes ; dans la bibliotheque Ollama, les variantes 4B et 8B occupent respectivement environ 2,5 Go et 5,2 Go au telechargement.

Point important : gratuit ne veut pas dire sans cout technique. Il faut de l'espace disque, de la RAM et, idealement, une carte graphique. Nous ne choisissons aucune taille de modele avant un test rapide sur la machine cible. Si elle est modeste, le produit garde des phrases modelees sans IA : aucune fonction de base ne depend d'un service payant.

## Contrat d'integration futur

L'application n'envoie jamais le fichier `.dem` brut au modele. Elle lui donne uniquement un paquet JSON deja valide, par exemple :

```json
{
  "insight_id": "H-01",
  "confidence": "inferred",
  "facts": {
    "round": 18,
    "zone": "B apartments",
    "trade_within_seconds": null,
    "nearest_teammate_eta_seconds": 3.1
  },
  "allowed_recommendation": "Attendre un timing a deux ou demander une flash avant de reprendre."
}
```

Le modele doit retourner une structure contrainte : titre, explication, recommandation, avertissement. Le programme verifie que :

- chaque nombre cite existe dans les faits ;
- le niveau de confiance est conserve ;
- aucune conclusion tactique non fournie n'est ajoutee ;
- en cas d'echec, le texte deterministe de secours est affiche.

## Etapes avant ajout d'IA

1. Valider l'utilite des alertes a templates sur de vraies demos.
2. Mesurer les faux positifs et stabiliser les definitions.
3. Tester l'experience locale avec un petit modele (Qwen3 4B est le point de depart envisageable).
4. Comparer la sortie IA avec le template sur 30 insights, sans la rendre visible par defaut.
5. Ajouter un interrupteur explicite "explications IA locales".

## Non-negociables

- Aucun abonnement ou cle API requis pour les fonctions principales.
- L'IA ne modifie jamais les donnees, scores ou seuils analytiques.
- Les preuves restent visibles meme quand l'explication est generee.
- Pas de voix, chat ou identifiants Steam transmis au modele dans le MVP.

