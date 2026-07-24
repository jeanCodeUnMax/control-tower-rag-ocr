---
description: Changements apportés aux filtres d'exclusion pour réduire le bruit dans les logs de surveillance
---

# Changements apportés aux filtres d'exclusion

## Problème initial
Les logs du terminal de surveillance étaient pollués par des modifications inutiles de fichiers système, notamment les fichiers temporaires de Git comme `FETCH_HEAD`, `maintenance.lock`, et divers fichiers `.lock`.

## Modifications effectuées
1. **Mise à jour du script `ingest-workspace.ps1`** : 
   - Ajout d'une logique de filtrage avant l'affichage des logs dans le terminal pour ignorer les fichiers exclus selon la configuration.
   - Correction pour utiliser des chemins relatifs lors de la comparaison avec les patterns d'exclusion, permettant aux règles comme `**/.git/**` de fonctionner correctement.
2. **Mise à jour de la configuration `ingestion.config.json`** :
   - Ajout d'exclusions spécifiques pour les fichiers Git temporaires : `**/.git/FETCH_HEAD`, `**/.git/objects/maintenance.lock`, et `**/*.lock`.

## Résultat
Après ces changements, les logs du terminal sont beaucoup plus propres, ne montrant que les modifications pertinentes aux fichiers du projet.
