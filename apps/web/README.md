# Interface web — alpha locale

Cette application React constitue l'interface locale du MVP. Elle ne stocke pas de demos brutes : elle appelle uniquement l'API locale et affiche les donnees derivees pseudonymisees.

## Prerequis

- Node.js 22 ou plus recent ;
- pnpm 11.

## Demarrer l'interface

Depuis ce dossier :

```powershell
pnpm install --frozen-lockfile
pnpm dev
```

L'interface est disponible sur `http://localhost:5173`. L'API doit etre demarree sur `http://127.0.0.1:8000` pour importer une demo et consulter une analyse.

Pendant le developpement, Vite relaie automatiquement les appels `/api` vers cette API locale : aucun service externe ni reglage CORS n'est necessaire.

## Controles qualite

```powershell
pnpm typecheck
pnpm lint
pnpm test:run
pnpm build
```

Le fichier `pnpm-workspace.yaml` autorise explicitement le seul script de construction tiers requis : `esbuild`.
