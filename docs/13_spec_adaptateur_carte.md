# Specification - adaptateur de carte Mirage

## Decision

Les heatmaps de v0.1 sont limitees a `de_mirage`. Elles reposent sur un adaptateur de carte versionne, separe du parsing et des regles de coaching.

`demoparser2` reste le parseur unique de demos. **Awpy 2.0.2+** est un candidat pour les donnees/operations de navigation et de visualisation : ne pas parser la meme demo deux fois avec deux bibliotheques differentes.

Awpy documente le parsing de donnees tick-level, des nav meshes, des distances et des visualisations CS2. Sa bibliotheque est MIT, mais son miroir de donnees `maps/navs` a retourne une erreur 404 lors de la verification du 18 septembre 2026. Nous ne faisons donc pas dependre l'alpha d'un telechargement externe non fiable.

Decision : le moteur d'analyse reste independant des assets. L'alpha affiche une **grille spatiale** explicitement nommee ainsi ; une vraie image radar et les callouts ne sont actives qu'apres acquisition et validation d'une source versionnee. Cela evite de dessiner une fausse carte Mirage ou d'inventer des zones.

## Interface interne

```python
class MapAdapter(Protocol):
    map_id: str
    version: str

    def to_radar(self, world_x: float, world_y: float) -> RadarPoint: ...
    def locate(self, world_x: float, world_y: float) -> ZoneLocation: ...
    def route_distance(self, start: WorldPoint, end: WorldPoint) -> DistanceResult: ...
```

```json
{
  "map_id": "de_mirage",
  "adapter_version": "mirage-0.1",
  "world": { "x": -650.2, "y": -892.7 },
  "radar": { "x": 0.41, "y": 0.63 },
  "zone": {
    "kind": "nav_place",
    "id": "connector",
    "label": "Connector",
    "confidence": "direct"
  }
}
```

`radar.x` et `radar.y` sont normalises entre 0 et 1. L'interface rend ensuite ce point sur une image/version de radar dont elle connait la provenance.

## Resolution de zone

1. Si un nav mesh valide est disponible, trouver la nav area contenant la position.
2. Si la nav area possede un `place_name` stable, retourner `nav_place` et son label.
3. Sinon, retourner la cellule de secours : `grid:<col>:<row>` de 256 unites monde.
4. Si la position est hors carte ou invalide, retourner `unknown` et ne pas l'utiliser dans une heatmap de tendance.

Le produit affiche "zone de grille" pour un fallback. Il ne doit jamais transformer une cellule en callout invente.

## Calcul de distance

`route_distance` est reserve aux regles futures demandant une distance de deplacement : exposition isolee, timing de reprise, regroupement. La v0.1 H-01 n'en depend pas.

Le resultat explicite sa methode :

```json
{
  "distance_units": 982.4,
  "method": "navmesh_path",
  "confidence": "inferred"
}
```

La distance euclidienne peut servir a des diagnostics internes mais ne doit pas produire un conseil de placement visible au joueur.

## Assets et versions

Le repository ne versionne pas automatiquement d'assets Valve extraits du jeu. Avant une distribution publique, documenter separement :

- source de l'image radar et conditions de redistribution ;
- version de nav mesh ;
- build CS2 associe ;
- hash de chaque asset derive ;
- methode de mise a jour apres patch.

Pendant le prototype local, les assets sont stockes hors Git sous `data/maps/de_mirage/<version>/`.

### Statut actuel et porte de sortie

| Niveau produit | Representation autorisee | Condition |
| --- | --- | --- |
| Alpha local | Grille monde normalisee, libellee "zone de grille" | Disponible maintenant ; aucune image Mirage redistribuee |
| Beta privee | Radar Mirage + callouts `nav_place` | 12 points connus et source/version/hash verifies |
| Distribution publique | Meme beta, plus audit des droits de redistribution | Aucune dependance a un fichier Valve copie dans le depot |

Le telechargeur Awpy sera reconsidere seulement quand son artefact de build sera disponible et reproductible. Il ne bloque ni le parsing, ni les quatre regles, ni l'interface alpha.

## Tests obligatoires

### Points connus

Constituer au moins 12 positions de reference reparties entre : A Ramp, Palace, Tetris, Top Mid, Window, Connector, Jungle, Underpass, B Apps, Market, B Site et Short.

Pour chaque point :

- coordonnees monde ;
- callout attendu ou cellule fallback attendue ;
- point radar attendu a une tolerance de 1 % de la largeur/hauteur ;
- capture du replay CS2 ou autre preuve de verification.

### Invariants

- `to_radar` retourne toujours des coordonnees finies dans `[0, 1]` pour un point valide.
- Deux positions d'une meme nav area ont le meme `zone.id`.
- Une position invalide ne devient jamais un callout valide.
- Changer `adapter_version` invalide les agregats de carte precedents et declenche un recalcul.

## Criteres de sortie

L'adaptateur Mirage beta est pret quand :

- 12/12 points connus se placent dans la bonne zone ou tolerance radar ;
- les quatre agregats H-01 a H-04 affichent un `n` et un lien de round pour chaque zone ;
- le fallback de grille est visible et comprehensible ;
- une mise a jour d'asset ne modifie pas silencieusement des rapports existants.

L'adaptateur alpha est pret quand la grille est stable, clairement etiquetee et que chaque cellule garde son `n` et ses liens vers les incidents sources.
