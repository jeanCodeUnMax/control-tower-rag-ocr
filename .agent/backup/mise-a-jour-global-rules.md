# Mise à Jour - global_rules.md

**Date:** 2026-04-06  
**Objectif:** Intégrer l'infrastructure mémoire actuelle dans les règles globales

---

## 📋 Résumé des Lacunes Identifiées

| # | Lacune | Impact | Priorité |
|---|--------|--------|----------|
| 1 | Dual Vector Store non documenté | Routage incomplet | Haute |
| 2 | Graph Memory complémentaire absent | Architecture incomplète | Haute |
| 3 | Optimisation cache non mentionnée | Information obsolète | Moyenne |
| 4 | Dimensions embedding non spécifiées | Configuration floue | Moyenne |
| 5 | Collections vectorielles non listées | Utilisation partielle | Basse |

---

## 🔧 Propositions de Corrections

### 1. Section DISCIPLINE DE MÉMOIRE UNIFIÉE - Ajouter

```markdown
### 5. ARCHITECTURE VECTOR STORE DUAL

#### Dual Vector Store
Le système utilise deux stores vectoriels complémentaires :

| Store | Dimensions | Usage | Collections |
|-------|------------|-------|-------------|
| **Qdrant** | 1536D | Catégorique | code_index, doc_index, config_index, workflow_index, skill_index |
| **Zvec** | 384D | Sémantique | entities, concepts, actions, relations, context, learning_insights |

#### Routage Automatique
- **Tags catégoriques** (type, domain, scope, priority) → Qdrant
- **Tags sémantiques** (concept, action, entity, relation) → Zvec
- **Tags mixtes** → Routage dual (les deux stores)

#### Outils MCP Disponibles
- `qdrant.semantic_search` / `zvec.semantic_search` - Recherche vectorielle
- `qdrant.hybrid_search` / `zvec.hybrid_unified_search` - Recherche hybride
- `zvec.semantic_search_with_cache` - Recherche avec cache optimisé
```

---

### 2. Section DISCIPLINE DE MÉMOIRE UNIFIÉE - Ajouter

```markdown
### 6. GRAPH MEMORY COMPLÉMENTAIRE

#### Deux Bases Graph Complémentaires

| Base | Rôle | Données | Usage |
|------|------|---------|-------|
| **memory_mcp.db** | Knowledge Graph MCP | 82 entités, 131 observations, 584 relations | Entités riches, observations, relations typées |
| **graph-memory.db** | Traversals rapides | 530 edges | Relations simples (from_id, to_id, type) |

#### Quand Utiliser Chacune
- **memory_mcp.db** : Création d'entités, observations détaillées, relations typées
- **graph-memory.db** : Traversals rapides, requêtes de chemin, analyse de connectivité

#### Outils MCP Disponibles
- `memory.create_entities` / `memory.add_observations` / `memory.create_relations` - Memory MCP
- `sqlite-node.execute_query` - Requêtes SQL sur graph-memory.db (lecture seule)
```

---

### 3. Section DISCIPLINE DE MÉMOIRE UNIFIÉE - Modifier

**Remplacer:**
```markdown
- **PORTABILITÉ** : La racine de stockage est définie via la variable d'environnement `CASCADE_DB_ROOT` dans le fichier `.env`.
- **OBLIGATION** : Toute donnée de mémoire persistante (KV, Graph, Vector) DOIT être stockée exclusivement dans `${CASCADE_DB_ROOT}/current_workspace/`.
```

**Par:**
```markdown
- **PORTABILITÉ** : La racine de stockage est définie via la variable d'environnement `CASCADE_DB_ROOT` dans le fichier `.env`.
- **OBLIGATION** : Toute donnée de mémoire persistante (KV, Graph, Vector) DOIT être stockée exclusivement dans `${CASCADE_DB_ROOT}/current_workspace/`.
- **CACHE OPTIMISÉ** : Le système utilise 2 caches runtime optimisés (au lieu de 3) :
  - `semantic-cache-data/runtime-cache.db` - MCP Cache Server
  - `current_workspace/cache/runtime-cache.db` - Système + Agents unifiés
```

---

### 4. Section MCP MEMORY - Ajouter Stats de Référence

```markdown
#### STATISTIQUES ACTUELLES (2026-04-06)

| Composant | Données | Dernière MAJ |
|-----------|---------|--------------|
| memory_mcp.db | 82 entités, 131 observations, 584 relations | 2026-04-05 |
| graph-memory.db | 530 edges | 2026-04-05 |
| Cache runtime | 152 entrées (2 bases) | 2026-04-05 |
| Qdrant | 5 collections (1536D) | 2026-04-05 |
| Zvec | 6 indexs (384D) | 2026-04-05 |
| Score RAG | 100/100 | 2026-04-03 |

#### Documents de Référence
- `ARCHITECTURE-ANALYSIS.md` - Architecture complète multi-bases
- `RAG-AUDIT-REPORT.md` - Audit système RAG (Score: 100/100)
- `CACHE-RUNTIME-UNIFICATION.md` - Optimisation caches (3→2 copies)
- `GRAPH-MEMORY-CLARIFICATION.md` - Rôles graph-memory vs memory_mcp
```

---

## 📝 Version Complète - Section à Remplacer

### Remplacer la section "MCP MEMORY - MÉMOIRE PERSISTANTE" (lignes 170-196) par:

```markdown
### MCP MEMORY - MÉMOIRE PERSISTANTE

#### OBLIGATION D'UTILISATION
L'agent DOIT utiliser le MCP Memory et zvec (sqlite-node: `${CASCADE_DB_ROOT}/memory_mcp.db`) pour :
- **Enregistrer** les préférences utilisateur découvertes au fil des interactions
- **Consulter** l'historique des workspaces et requêtes fréquentes
- **Mettre à jour** les observations existantes avec nouvelles informations
- **Créer des relations** entre entités pour contextualiser les demandes
- **Utiliser l'indexation hybride** pour recherche unifiée (Memory + Zvec)
- **Tirer parti du cache vectoriel** pour optimiser les performances de recherche
- **Bénéficier de la réplication partielle** pour cohérence automatique des données

#### ARCHITECTURE MÉMOIRE COMPLÈTE

| Composant | Type | Usage |
|-----------|------|-------|
| **memory_mcp.db** | Knowledge Graph | Entités, observations, relations riches |
| **graph-memory.db** | Traversals | Edges simples, requêtes de chemin |
| **Qdrant** | Vector 1536D | Recherche catégorique |
| **Zvec** | Vector 384D | Recherche sémantique |
| **Cache Runtime** | KV Store | 2 copies optimisées |

#### STRUCTURE DE LA BASE memory_mcp.db
| Table | Usage |
|-------|-------|
| entities | Utilisateur, Préférences, Workspaces, Requêtes fréquentes |
| observations | Contenu associé à chaque entité |
| relations | Liens entre entités |

#### DÉCLENCHEURS
- **Début de session** : Consulter Utilisateur et Preferences-Globales
- **Nouvelle préférence détectée** : Ajouter observation à l'entité appropriée
- **Requête récurrente** : Enrichir Requetes-Frequentes
- **Interaction significative** : Logger dans Interactions-Session
- **Recherche complexe** : Utiliser hybrid_unified_search pour recherche unifiée Memory + Zvec
- **Performance critique** : Activer semantic_search_with_cache pour optimiser les requêtes fréquentes
- **Mise à jour données** : Laisser la réplication partielle gérer automatiquement la cohérence
- **Recherche catégorique** : Utiliser Qdrant (tags: type, domain, scope)
- **Recherche sémantique** : Utiliser Zvec (tags: concept, action, entity)
- **Recherche mixte** : Routage dual (Qdrant + Zvec)

#### STATISTIQUES ACTUELLES (2026-04-06)
| Composant | Données |
|-----------|---------|
| memory_mcp.db | 82 entités, 131 observations, 584 relations |
| graph-memory.db | 530 edges |
| Cache runtime | 152 entrées (2 bases optimisées) |
| Qdrant | 5 collections (1536D) |
| Zvec | 6 indexs (384D) |
| Score RAG | 100/100 ✅ |

#### DOCUMENTS DE RÉFÉRENCE
- `ARCHITECTURE-ANALYSIS.md` - Architecture complète multi-bases
- `RAG-AUDIT-REPORT.md` - Audit système RAG (Score: 100/100)
- `CACHE-RUNTIME-UNIFICATION.md` - Optimisation caches (3→2 copies)
- `GRAPH-MEMORY-CLARIFICATION.md` - Rôles graph-memory vs memory_mcp
```

---

## ✅ Checklist d'Implémentation

- [ ] Ajouter section "ARCHITECTURE VECTOR STORE DUAL"
- [ ] Ajouter section "GRAPH MEMORY COMPLÉMENTAIRE"
- [ ] Mettre à jour section "ANCORAGE DU STOCKAGE" avec cache optimisé
- [ ] Remplacer section "MCP MEMORY - MÉMOIRE PERSISTANTE" complète
- [ ] Ajouter statistiques actuelles
- [ ] Ajouter documents de référence

---

## 📊 Impact Attendu

| Amélioration | Bénéfice |
|--------------|----------|
| Documentation dual vector | Utilisation optimale Qdrant/Zvec |
| Documentation graph-memory.db | Architecture complète |
| Stats actuelles | Référence pour debugging |
| Score RAG | Confiance dans le système |
| Cache optimisé | Information à jour |
