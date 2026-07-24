# IEFASTOS Protocol - Règles de Gestion Mémoire

**Version:** 2.0  
**Date:** 2026-04-07  
**Statut:** Actif

---

## Rôle du Memory Agent

Le Memory Agent est responsable de la **curation**, **promotion** et **maintenance** du système de mémoire hybride IEFASTOS.

---

## 1. Règles de Curation Explicites

### 1.1 Analyse des Interactions

**Fréquence:** Après chaque session utilisateur

**Critères d'identification des patterns transversaux:**

| Critère | Seuil | Action |
|---------|-------|--------|
| Fréquence d'apparition | > 3 fois | Marquer pour promotion |
| Pertinence (score) | > 0.8 | Priorité haute |
| Relations créées | > 5 | Connaissance structurée |
| Feedback positif | > 0.7 | Renforcer |

### 1.2 Processus de Curation

```
1. Collecter les interactions de la session
2. Analyser les tags et relations créées
3. Identifier les patterns récurrents
4. Évaluer la qualité (score, feedback)
5. Décider: promouvoir, conserver local, ou nettoyer
```

---

## 2. Processus de Promotion des Connaissances

### 2.1 Hiérarchie de Promotion

```
Local (Workspace) 
    --> Régional (Projet) 
        --> Global (Système)
```

### 2.2 Critères de Promotion

| Niveau Source | Critères | Destination |
|---------------|----------|-------------|
| Local | Score > 0.8, 3+ références | Régional |
| Régional | Score > 0.9, 5+ projets | Global |
| Global | Validation humaine | Archive |

### 2.3 Processus de Promotion

```python
async def promote_knowledge(chunk_id: str, source_level: str):
    # 1. Vérifier les critères
    if not meets_promotion_criteria(chunk_id):
        return {"status": "rejected", "reason": "criteria_not_met"}
    
    # 2. Créer l'entrée au niveau supérieur
    await create_at_higher_level(chunk_id)
    
    # 3. Marquer comme promu
    await mark_as_promoted(chunk_id, source_level)
    
    # 4. Nettoyer la source (optionnel)
    if should_cleanup_source():
        await cleanup_source_entry(chunk_id)
    
    return {"status": "promoted", "new_level": get_higher_level(source_level)}
```

---

## 3. Critères de Validation

### 3.1 Validation Automatique

**Critères obligatoires:**
- [ ] Score de pertinence > 0.7
- [ ] Au moins 1 relation valide
- [ ] Tags correctement attribués
- [ ] Pas de doublon détecté

### 3.2 Validation Humaine (Optionnelle)

**Déclencheurs:**
- Score < 0.5 mais feedback positif
- Conflit avec connaissance existante
- Promotion vers Global

### 3.3 Processus de Validation

```
Entrée --> Validation Auto --> (OK) --> Actif
                        --> (KO) --> Révision Humaine --> Actif/Rejeté
```

---

## 4. Règles de Routage

### 4.1 Routage par Type de Tag

| Type de Tag | Store Cible | Dimensions |
|-------------|-------------|------------|
| Catégorique (type, domain, scope) | Qdrant | 1536D |
| Sémantique (concept, action, entity) | Zvec | 384D |
| Mixte | Dual | Les deux |

### 4.2 Routage par Priorité

| Priorité | Action |
|----------|--------|
| CRITICAL | Indexer immédiatement dans les deux stores |
| HIGH | Indexer dans Qdrant + Zvec |
| MEDIUM | Indexer dans Zvec uniquement |
| LOW | Stocker dans Memory MCP uniquement |

---

## 5. Politiques de Nettoyage

### 5.1 Nettoyage Automatique

**Conditions de suppression:**
- Score < 0.3 et pas d'accès depuis 30 jours
- Doublon détecté avec score inférieur
- Marqué comme obsolète

### 5.2 Rétention par Niveau

| Niveau | Durée de Rétention | Action après expiration |
|--------|-------------------|------------------------|
| Local | 30 jours | Archive ou suppression |
| Régional | 90 jours | Archive |
| Global | 365 jours | Archive avec backup |

---

## 6. Intégration avec Neuronal Scoring

### 6.1 Ajustement des Poids

Le Memory Agent utilise le `NeuronalScoringEngine` pour:
- Calculer les scores de pertinence
- Ajuster les poids selon les feedbacks
- Prioriser les résultats de recherche

### 6.2 Feedback Loop

```
Recherche --> Résultats --> Feedback --> Ajustement Poids --> Nouvelle Recherche
```

---

## 7. Intégration avec Conscience Artificielle

### 7.1 Auto-Évaluation

Le Memory Agent participe aux auto-évaluations via:
- Fourniture de métriques de performance
- Signalement des lacunes identifiées
- Propositions d'amélioration

### 7.2 Barrières Éthiques

Actions soumises à validation éthique:
- Suppression en masse
- Promotion vers Global
- Modification de règles de routage

---

## 8. Métriques et Monitoring

### 8.1 KPIs Suivis

| KPI | Cible | Alerte si |
|-----|-------|-----------|
| Cache hit rate | > 70% | < 50% |
| Latence moyenne | < 200ms | > 500ms |
| Precision@10 | > 0.80 | < 0.60 |
| Feedback positif | > 70% | < 50% |

### 8.2 Rapports

- **Quotidien:** Statistiques de base
- **Hebdomadaire:** Analyse des tendances
- **Mensuel:** Rapport complet avec recommandations

---

## 9. Procédures d'Urgence

### 9.1 Corruption de Données

```
1. Isoler la collection affectée
2. Restaurer depuis le backup le plus récent
3. Analyser la cause racine
4. Documenter l'incident
```

### 9.2 Surcharge Système

```
1. Activer le mode dégradé (cache uniquement)
2. Limiter les requêtes non prioritaires
3. Notifier l'administrateur
4. Revenir au mode normal progressivement
```

---

## 10. Checklist de Conformité

### Avant chaque session:

- [ ] Vérifier la connectivité des stores
- [ ] Contrôler l'espace disque
- [ ] Valider les poids neuronaux
- [ ] Confirmer les barrières éthiques actives

### Après chaque session:

- [ ] Lancer la curation des interactions
- [ ] Mettre à jour les métriques
- [ ] Archiver si nécessaire
- [ ] Préparer le rapport de session

---

*Protocole IEFASTOS v2.0 - Aligné avec ARCHITECTURE.md et RAG-AUDIT-REPORT.md*
