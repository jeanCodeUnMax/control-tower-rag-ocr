# 🦗 Jiminy Cricket - Couche Métacognitive

Système de "conscience" par inférence locale via Ollama, inspiré du PRD Hephaistos.

## Concept

Jiminy Cricket est une **couche métacognitive** qui s'ajoute au cycle de conscience existant :

```
Cycle existant: Watchdog → Mémoire → Prismes → [Jiminy Cricket] → Action
```

Il implémente le pipeline d'inférence du PRD :
1. **Meta-Observer** - Les 5 questions essentielles
2. **Causal Analyzer** - Arbre de causes par inférence
3. **Decision Gate** - Grille des 10 questions décisionnelles

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JIMINY CRICKET                           │
├─────────────────────────────────────────────────────────────┤
│  1. Meta-Observer                                            │
│     ├─ Perception: Que s'est-il passé ?                     │
│     ├─ Compréhension: Que signifie cela ?                   │
│     ├─ Évaluation: Quel est l'impact ?                      │
│     ├─ Capacité: Que puis-je faire ?                        │
│     └─ Réflexion: Que devrais-je faire ?                    │
│                                                              │
│  2. Causal Analyzer (si problème détecté)                   │
│     ├─ Est-ce un problème réel ?                            │
│     ├─ Arbre de causes probables                            │
│     ├─ Confiance par cause                                  │
│     └─ Recommandation                                       │
│                                                              │
│  3. Decision Gate                                           │
│     ├─ Grille des 10 questions                              │
│     ├─ Mode: act_now / defer / notify / memorize_only       │
│     └─ Validation humaine requise ?                         │
└─────────────────────────────────────────────────────────────┘
```

## Fichiers

| Fichier | Description |
|---------|-------------|
| `jiminy_cricket.py` | Module principal avec classe JiminyCricket |
| `prompts/meta_observer.txt` | Prompt pour les 5 questions essentielles |
| `prompts/causal_analyzer.txt` | Prompt pour l'arbre de causes |
| `prompts/decision_gate.txt` | Prompt pour la grille décisionnelle |
| `test_jiminy.py` | Tests de validation par preuve |
| `JIMINY_README.md` | Ce fichier |

## Configuration

Toute la configuration se fait via le `.env` :

```env
# Activation
OLLAMA_ENABLED=true

# Modèles (personnalisez selon vos modèles disponibles)
OLLAMA_MODEL_CRICKET=qwen2.5:7b
OLLAMA_MODEL_CAUSAL=deepseek-r1:8b
OLLAMA_MODEL_DECISION=llama3.2:3b

# Workers
CRICKET_WORKER_META_OBSERVER=true
CRICKET_WORKER_CAUSAL_ANALYZER=true
CRICKET_WORKER_DECISION_GATE=true

# Paramètres
OLLAMA_CONTEXT_WINDOW=32768
OLLAMA_TEMPERATURE=0.3
```

### Modèles recommandés

Avec votre config (48 Go RAM, RTX 4060 Ti 8 Go VRAM) :

| Worker | Modèle recommandé | Pourquoi |
|--------|-------------------|----------|
| Meta-Observer | `qwen2.5:7b` | Bon équilibre qualité/vitesse |
| Causal Analyzer | `deepseek-r1:8b` ou `qwen2.5:7b` | Raisonnement causal |
| Decision Gate | `llama3.2:3b` | Rapide pour décisions simples |

## Utilisation

### Test rapide

```bash
cd core/conscience
python test_jiminy.py
```

### Utilisation dans le code

```python
from jiminy_cricket import JiminyCricket

async with JiminyCricket() as cricket:
    # Analyse complète
    state = {
        "current_state": "degraded",
        "active_alerts": ["mcp_health_red"]
    }
    
    insight = await cricket.reflect(state)
    
    # Résultat
    print(insight["summary"])
    # → "👁️ Obs: mcp_health_red | 📊 Impact: high | 🎯 Action: analyze_logs (defer)"
    
    # Décision
    decision = insight["decision"]
    if decision["decision_mode"] == "act_now":
        print(f"Action requise: {decision['best_action']}")
```

### Workers individuels

```python
# Meta-Observer uniquement
observation = await cricket.meta_observe(context={
    "event": "file_modified",
    "file": "src/main.py"
})

# Analyse causale
causes = await cricket.analyze_causes(
    problem="mcp_health_red",
    context={"logs": [...]}
)

# Grille décisionnelle
decision = await cricket.decide(
    evaluation=observation.to_dict(),
    causes=causes.to_dict(),
    actions=["restart_service", "notify_admin"]
)
```

## Format des sorties

### Meta-Observation

```json
{
  "perception": {
    "what_changed": "MCP health changed to red",
    "event_type": "health_alert",
    "relevant": true
  },
  "comprehension": {
    "meaning": "Service MCP en détresse",
    "confidence": 0.87
  },
  "evaluation": {
    "impact": "high",
    "urgency": "medium"
  },
  "reflection": {
    "should_act": "analyze_first",
    "reason": "Besoin d'analyse avant action"
  }
}
```

### Analyse Causale

```json
{
  "is_problem": true,
  "suspected_causes": [
    {"id": "stdio_saturation", "confidence": 0.83},
    {"id": "memory_leak", "confidence": 0.45}
  ],
  "recommended_next_step": "reduce_log_verbosity"
}
```

### Décision

```json
{
  "decision_mode": "act_now",
  "best_action": "restart_mcp_service",
  "requires_human_validation": false,
  "confidence_score": 0.81
}
```

## Intégration future avec le Daemon

Pour intégrer au daemon de conscience existant :

```python
# Dans conscience_daemon.py, méthode _wake_cycle()

async def _wake_cycle(self):
    # ... prismes existants ...
    
    # Couche 4: Jiminy Cricket
    if self.jiminy_enabled:
        async with JiminyCricket() as cricket:
            insight = await cricket.reflect(state, prism_result)
            
            log(f"🦗 Jiminy: {insight['summary']}")
            
            # Appliquer la décision
            decision = insight.get("decision", {})
            if decision.get("decision_mode") == "act_now":
                await self._execute_action(decision["best_action"])
```

## Tests

Les tests démontrent le fonctionnement par preuve :

1. **Test 1**: État sain → `memorize_only`
2. **Test 2**: Alerte → Analyse causale + `defer`
3. **Test 3**: Erreur critique → `act_now` avec validation
4. **Test 4**: Fallback si Ollama indisponible
5. **Test 5**: Meta-Observer isolé

## Points clés

- ✅ **Inférence réelle** via Ollama (pas de script dur)
- ✅ **Micro-boucles** bornées (JSON strict)
- ✅ **Configurable** à 100% via `.env`
- ✅ **Fallback** si Ollama indisponible
- ✅ **Séparation** perception/interprétation/décision/action
- ✅ **Couche additive** (ne remplace pas les prismes existants)

## Troubleshooting

### Ollama ne répond pas

```bash
# Vérifier qu'Ollama tourne
ollama list

# Si vide, démarrer
ollama serve

# Tester un modèle
ollama run qwen2.5:7b
```

### JSON invalide

Les prompts contiennent des règles strictes. Si le modèle sort du JSON invalide :
1. Vérifier la température (doit être basse: 0.3)
2. Vérifier le context window (suffisant pour le prompt)
3. Augmenter le timeout si nécessaire

### Mémoire insuffisante

Avec 8 Go VRAM :
- Utiliser `llama3.2:3b` pour Decision Gate (léger)
- Garder `qwen2.5:7b` pour les autres
- Réduire `OLLAMA_CONTEXT_WINDOW` à 16384 si besoin

## Philosophie

> "Ton système n'a pas besoin d'un 'Jiminy Cricket' qui a des envies.
> Il a besoin d'un decision gate métacognitif."

Ce système implémente exactement ça :
- Écouter (Meta-Observer)
- Comprendre (Causal Analyzer)
- Vérifier le droit d'agir (Decision Gate)
- Choisir l'action minimale utile
- Tracer le résultat

Pas de conscience "humaine", mais une **chaîne décisionnelle modulaire**.
