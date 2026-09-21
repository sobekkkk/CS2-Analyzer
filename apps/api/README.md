# API locale - lot 1

Ce premier lot inspecte une demo locale sans conserver le fichier : signature, hash, carte, participants, cadence de tick et borne de fin de phase knife.

Depuis la racine du projet, avec les dependances locales deja installees :

```powershell
$env:PYTHONPATH = "$PWD\.tools\python;$PWD\apps\api\src"
& 'C:\Users\drago\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m uvicorn cs2_analyzer.main:app --app-dir apps/api/src --reload
```

L'API est alors disponible sur `http://127.0.0.1:8000`, avec la documentation interactive sur `/docs`.

L'endpoint `POST /api/v1/demos` accepte un fichier `.dem` en multipart sous le champ `file`. Le fichier est place dans un dossier temporaire puis supprime apres l'inspection.

Apres `POST /api/v1/analyses/{analysis_id}/player`, le client peut lire uniquement les
tables derivees via :

- `GET /api/v1/matches/{match_id}/overview` ;
- `GET /api/v1/matches/{match_id}/timeline?round_number=12` ;
- `GET /api/v1/matches/{match_id}/heatmaps/damage?cell_size=256`.
- `GET /api/v1/matches/{match_id}/heatmaps/five-vs-four?cell_size=256`.

Les cellules de dommages sont des coordonnees monde agregees, pas encore des
callouts ni un radar Mirage. La carte 5v4 conserve uniquement les positions
echantillonnees utiles a cette regle, jamais les ticks complets. Les fichiers
`.dem` bruts ne sont pas conserves. Les evenements de timeline exposent les
pseudonymes observes dans la demo pour les deux joueurs concernes, mais jamais
les SteamID bruts.
