# Postulo

Application d'aide à la recherche d'emploi assistée par IA : collecte d'offres, scoring, génération de CV et lettres, suivi des candidatures.

## Stack

- `apps/web` : Next.js + TypeScript + Tailwind
- `apps/api` : FastAPI (Python, géré avec uv)
- PostgreSQL + pgvector, Docker Compose

## Démarrer

```bash
cp .env.example .env
docker compose up -d
```
