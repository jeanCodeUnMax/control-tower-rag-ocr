# Control Tower RAG — Repository complet V0.5

> Prototype avancé documenté et déployable localement. Consulter impérativement [l’audit V0.5](docs/AUDIT_V0.5.md) et les [limites/roadmap](docs/wiki/12_LIMITS_ROADMAP.md) avant une mise en production.

## Accès rapide

- [Wiki](docs/wiki/README.md)
- [PRD](docs/PRD.md)
- [Dev Book](docs/DEV_BOOK.md)
- [Dev Tracker](docs/DEV_TRACKER.md)
- [Guide du dépôt](docs/REPOSITORY_GUIDE.md)
- [Installation et déploiement](docs/wiki/02_INSTALL_DEPLOY.md)
- [Comment utiliser](docs/wiki/03_USE.md)
- [Comment régler](docs/wiki/04_CONFIGURE.md)
- [Comment expliquer](docs/wiki/05_EXPLAIN.md)
- Interface locale après démarrage : `http://127.0.0.1:8000/ui/`
- Documentation API : `http://127.0.0.1:8000/docs`

---


Tour de contrôle documentaire pour PDF longs. La V0.5 ajoute une alternative exploitable entre ingestion immédiate et traitement multimodal accéléré : préflight, profils, routage page par page, fallbacks, quotas, budget et enrichissement différé du même document.

## Ce que cette version fait réellement

- extraction PDF native, OCR Tesseract et analyse page par page ;
- lots adaptatifs et registre exhaustif des pages ;
- consolidation des chunks et actifs visuels avant indexation ;
- profil `local_fast` pour rendre le texte interrogeable immédiatement ;
- file explicite des pages visuelles différées ;
- profils `balanced`, `cloud_turbo` et `night_deep` ;
- providers OpenAI-compatibles : OpenRouter, Ollama local et Ollama Cloud ;
- provider Gemini REST direct ;
- appels vision indépendants par page et parallélisés dans chaque lot ;
- débit maximal, concurrence, timeout et retries propres à chaque provider ;
- backoff exponentiel avec jitter ;
- circuit breaker après échecs répétés ;
- cascade de providers et repli local sans perdre la page ;
- plafond budgétaire par document ;
- préflight sans appel API ;
- benchmark sur un échantillon représentatif ;
- enrichissement ultérieur des pages différées sans dupliquer le document ;
- remplacement atomique des chunks du document après enrichissement ;
- 30 tests automatisés.

## Installation

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

Puis :

```powershell
control-tower init-project demo
```

## Parcours A — résultat immédiat et économique

Le profil par défaut est `local_fast`.

```powershell
control-tower profile-set --project demo local_fast
control-tower plan-document --project demo "C:\PDF\manuel.pdf"
control-tower ingest --project demo "C:\PDF\manuel.pdf"
```

Le PDF est extrait, contrôlé, atomisé et consolidé. Les pages simples entrent dans le RAG immédiatement. Les pages nécessitant une compréhension visuelle profonde sont inscrites dans :

```text
artifacts/<document_id>/provider_report.json
```

Champ principal :

```json
{
  "deferred_pages": [7, 18, 42]
}
```

## Parcours B — cloud rapide

### OpenRouter avec Qwen3-VL

```powershell
$env:OPENROUTER_API_KEY="..."
control-tower config-set --project demo vision.providers.1.enabled true
control-tower profile-set --project demo cloud_turbo
```

Le provider configuré à l'index `1` est :

```text
openrouter_qwen → qwen/qwen3-vl-32b-instruct
```

Option Flash via OpenRouter :

```powershell
control-tower config-set --project demo vision.providers.2.enabled true
```

### Gemini direct

```powershell
$env:GEMINI_API_KEY="..."
control-tower config-set --project demo vision.providers.3.enabled true
control-tower profile-set --project demo cloud_turbo
```

### Ollama local

```powershell
ollama pull qwen3-vl:4b
control-tower config-set --project demo vision.providers.0.enabled true
control-tower profile-set --project demo balanced
```

### Ollama Cloud

```powershell
$env:OLLAMA_API_KEY="..."
control-tower config-set --project demo vision.providers.4.enabled true
```

Les identifiants de modèles cloud changent selon le catalogue du compte. Ajuste si nécessaire :

```powershell
control-tower config-set --project demo vision.providers.4.model "MODELE_CLOUD"
```

## Préflight obligatoire avant 800 pages

```powershell
control-tower plan-document --project demo "C:\PDF\manuel.pdf"
```

Le résultat contient :

- nombre exact de pages ;
- plan des lots ;
- pages locales ;
- pages cloud ;
- pages différées ;
- clés API détectées ;
- concurrence et RPM configurés ;
- coût cloud minimal estimé ;
- recommandation de profil.

Aucun appel cloud n'est effectué pendant le préflight.

## Benchmark avant ingestion massive

```powershell
control-tower benchmark-vision `
  --project demo `
  --max-pages 12 `
  "C:\PDF\manuel.pdf"
```

Le benchmark sélectionne en priorité des pages complexes, puis des pages réparties dans le document. Il retourne :

- temps total ;
- pages par minute ;
- projection indicative pour 800 pages ;
- provider choisi page par page ;
- retries et erreurs ;
- fallback éventuel ;
- estimation budgétaire.

Le rapport est enregistré dans :

```text
.control_tower/projects/<projet>/benchmarks/<benchmark_id>/benchmark.json
```

La projection 800 pages est une extrapolation du corpus échantillonné, pas une garantie contractuelle.

## Enrichir la nuit sans réingérer le PDF

Après une ingestion `local_fast`, récupère le `document_id`, puis :

```powershell
control-tower enrich-document `
  --project demo `
  --document-id <DOCUMENT_ID> `
  --profile cloud_turbo
```

Ou pour une passe approfondie :

```powershell
control-tower enrich-document `
  --project demo `
  --document-id <DOCUMENT_ID> `
  --profile night_deep
```

Cette commande :

1. reprend uniquement les pages marquées `needs_multimodal_review` ;
2. les rend en image ;
3. exécute la cascade configurée ;
4. met à jour `page_analyses.json` ;
5. ajoute le texte manuscrit ou visuel découvert ;
6. reconstruit les chunks du même `document_id` ;
7. reconsolide les doublons ;
8. remplace atomiquement l'ancien index du document.

Elle ne crée pas une seconde copie logique du PDF dans le RAG.

## Profils

| Profil | Comportement |
|---|---|
| `local_fast` | Texte immédiatement disponible, vision complexe différée |
| `balanced` | Cloud uniquement pour OCR difficile, images, graphes ou dessins |
| `cloud_turbo` | Providers cloud prioritaires, local en dernier secours |
| `night_deep` | Analyse multimodale de toutes les pages |

## Réglages de résilience

Exemple OpenRouter Qwen, index `1` :

```powershell
control-tower config-set --project demo vision.providers.1.max_concurrency 12
control-tower config-set --project demo vision.providers.1.requests_per_minute 240
control-tower config-set --project demo vision.providers.1.max_retries 4
control-tower config-set --project demo vision.providers.1.timeout_seconds 120
control-tower config-set --project demo vision.providers.1.circuit_breaker_failures 5
control-tower config-set --project demo vision.providers.1.circuit_breaker_cooldown_seconds 60
```

Budget :

```powershell
control-tower config-set --project demo vision.max_cost_per_document_usd 15
control-tower config-set --project demo vision.stop_on_budget_exceeded false
```

Avec `stop_on_budget_exceeded=false`, les pages restantes repassent en local et restent signalées pour révision. Avec `true`, le traitement s'arrête explicitement au lieu de dépasser le budget.

## Cascade par défaut

```text
cloud_turbo / night_deep
  OpenRouter Qwen
  → OpenRouter Gemini Flash
  → Gemini direct
  → Ollama Cloud
  → Ollama local
  → analyse locale dégradée
```

Seuls les providers dont `enabled=true` participent à la cascade. Aucune clé n'est requise pour utiliser `local_fast`.

## Contrats HTTP implémentés

- OpenRouter/Ollama : API Chat Completions OpenAI-compatible, image en base64 et sortie JSON ;
- OpenRouter : objet `provider` pour le tri par débit, fallbacks et refus de collecte ;
- Gemini : `generateContent`, image inline et schéma JSON ;
- chaque réponse est validée par le modèle Pydantic `PageAnalysis` ;
- une réponse sans le numéro de page attendu est rejetée.

## Artefacts supplémentaires V0.5

```text
artifacts/<document_id>/
├── provider_report.json
├── renders_enrichment/
└── pages/page_XXXXX.json

benchmarks/<benchmark_id>/
└── benchmark.json
```

## Tests

```powershell
pytest -q
```

Les tests couvrent notamment :

- routage local/cloud/différé ;
- cascade après erreur `429` ;
- retries avant succès ;
- budget insuffisant ;
- contrats OpenRouter/Ollama et Gemini ;
- préflight ;
- benchmark local ;
- enrichissement différé ;
- remplacement sans duplication du document ;
- tests OCR, PDF long et consolidation des versions précédentes.

## Limites honnêtes

- aucun appel réel OpenRouter ou Gemini n'est exécuté sans tes clés ;
- les prix par page dans le YAML sont des estimations configurables, pas une facture calculée par tokens ;
- le parallélisme inter-lots reste séquentiel : la vision est parallélisée à l'intérieur de chaque lot adaptatif ;
- le benchmark doit être exécuté sur tes PDF pour régler la concurrence et les RPM ;
- Mistral OCR Batch et PaddleOCR ne sont pas encore branchés comme providers natifs ;
- la recherche finale reste lexicale ;
- le consensus-less n'est pas encore dans la décision d'indexation.

Voir :

- `docs/PROVIDER_ROUTING_V0.5.md`
- `docs/TASK_BREAKDOWN_V0.5.md`
- `CHANGES_V0.5.md`
