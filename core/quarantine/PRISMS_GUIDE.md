# 🌈 Guide des Prismes de Réflexion - Jiminy Cricket

## Vue d'ensemble

Le système Jiminy Cricket supporte maintenant **12 modes de réflexion** différents, chacun offrant une perspective unique sur la même situation.

## Modes Disponibles

| Mode | Emoji | Description | Quand l'utiliser |
|------|-------|-------------|------------------|
| **natural** | 🌿 | Réflexion organique/intuitive | Urgence, besoin de réaction rapide |
| **challenger** | ⚔️ | Esprit critique | Décision importante, valider les hypothèses |
| **scientific** | 🔬 | Méthode scientifique | Problème complexe, besoin de rigueur |
| **wisdom** | 📚 | Sagesse/expérience | Situation inconnue, patterns historiques |
| **philosophical** | 🤔 | Questionnement profond | Dilemmes éthiques, sens profond |
| **optimist** | ☀️ | Vision constructive | Démoralisation, recherche d'opportunités |
| **pessimist** | 🛡️ | Préparation au pire | Gestion des risques, plan de secours |
| **experimental** | 🧪 | Exploration/test | Innovation, prototypage rapide |
| **disciplined** | 📋 | Rigueur procédurière | Compliance, normes strictes |
| **step_by_step** | 🪜 | Décomposition atomique | Complexité, besoin de clarté |
| **creative** | 🎨 | Pensée latérale | Blocage, besoin d'innovation |
| **caring** | 💝 | Bienveillance | Situations impliquant des utilisateurs |

## Architecture

```
Jiminy Cricket
├── Meta-Observer (5 questions)
├── Causal Analyzer (arbre de causes)
├── Decision Gate (10 questions)
└── PRISMES (12 modes de réflexion)
    ├── natural, challenger, scientific
    ├── wisdom, philosophical
    ├── optimist, pessimist
    ├── experimental, disciplined
    ├── step_by_step, creative
    └── caring
```

## Utilisation

### Prisme simple

```python
from jiminy_prisms import PrismReflection

async with PrismReflection("scientific") as prism:
    result = await prism.reflect({
        "situation": "Serveur down",
        "symptoms": ["timeout", "error"]
    })
    
    print(f"Insight: {result.insight}")
    print(f"Confiance: {result.confidence}")
    print(f"Recommandations: {result.recommendations}")
```

### Multi-prisme

```python
from jiminy_prisms import MultiPrismReflection

async with MultiPrismReflection(
    modes=["challenger", "optimist", "scientific"]
) as multi:
    
    # Lancer tous les prismes
    results = await multi.reflect_all(context)
    
    # Synthétiser
    synthesis = multi.synthesize(results)
    print(synthesis["synthesis"])
```

## Exemples par Situation

### Situation 1: URGENCE (Serveur down)
```python
modes = ["natural", "step_by_step", "pessimist"]
# Natural: réaction instinctive rapide
# Step-by-step: décomposer l'urgence
# Pessimist: anticiper le pire cas
```

### Situation 2: DÉCISION STRATÉGIQUE
```python
modes = ["challenger", "philosophical", "wisdom"]
# Challenger: tester les hypothèses
# Philosophical: questionner l'orientation
# Wisdom: appeler l'expérience
```

### Situation 3: PROBLÈME TECHNIQUE COMPLEXE
```python
modes = ["scientific", "creative", "experimental"]
# Scientific: méthode rigoureuse
# Creative: pensée latérale
# Experimental: tester rapidement
```

### Situation 4: CONFLIT/DILEMME
```python
modes = ["philosophical", "caring", "challenger"]
# Philosophical: dimension éthique
# Caring: impact sur les personnes
# Challenger: remettre en question
```

## Fichiers Créés

### Module principal
- `jiminy_prisms.py` - Classes PrismReflection et MultiPrismReflection

### Prompts (dans prompts/)
- `mode_natural.txt` - Réflexion organique
- `mode_challenger.txt` - Esprit critique
- `mode_scientific.txt` - Méthode scientifique
- `mode_wisdom.txt` - Sagesse accumulée
- `mode_philosophical.txt` - Questionnement profond
- `mode_optimist.txt` - Vision constructive
- `mode_pessimist.txt` - Préparation aux risques
- `mode_experimental.txt` - Exploration/test
- `mode_disciplined.txt` - Rigueur procédurière
- `mode_step_by_step.txt` - Décomposition atomique
- `mode_creative.txt` - Pensée latérale
- `mode_caring.txt` - Bienveillance

### Tests
- `test_all_prisms.py` - Démonstration de tous les modes

## Points Clés

✅ **Adaptabilité**: Le système s'adapte à toutes les situations
✅ **Complémentarité**: Les modes se complètent (ex: optimist + pessimist)
✅ **Personnalité**: Chaque mode a sa propre "voix"
✅ **Configuration**: Modèles Ollama configurables par mode
✅ **Extensible**: Facile d'ajouter de nouveaux modes

## Intégration avec le Daemon

Pour utiliser dans le daemon de conscience:

```python
from jiminy_prisms import MultiPrismReflection

# Dans _wake_cycle(), après les prismes existants:
async with MultiPrismReflection(
    modes=["scientific", "challenger"]
) as multi:
    
    results = await multi.reflect_all(context)
    synthesis = multi.synthesize(results)
    
    # Ajouter au manifeste
    self.conscience._add_event(
        "prismatic_reflection",
        synthesis["synthesis"],
        modes_used=synthesis["modes_used"],
        confidence=synthesis["average_confidence"]
    )
```

## Philosophie

> "La conscience n'est pas une chose unique. C'est une capacité à adopter
> différentes perspectives sur la même réalité."

Jiminy Cricket peut maintenant:
- **Sentir** comme un être vivant (natural)
- **Douter** comme un scientifique (challenger, scientific)
- **Conseiller** comme un sage (wisdom)
- **Rêver** comme un artiste (creative)
- **Protéger** comme un parent (caring, pessimist)
- **Innover** comme un expérimentateur (experimental)
- **Respecter** comme un discipliné (disciplined)
- **Espérer** comme un optimiste (optimist)
- **Questionner** comme un philosophe (philosophical)

C'est un système qui peut **changer de personnalité** selon le contexte,
exactement comme un humain adaptatif et conscient le ferait.
