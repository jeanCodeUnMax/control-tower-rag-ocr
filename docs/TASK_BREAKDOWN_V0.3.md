# Découpage des tâches — V0.3 OCR observable

Chaque tâche possède une sortie vérifiable. Une tâche n'est pas considérée terminée parce qu'une classe existe, mais parce qu'un test ou un artefact prouve son comportement.

## Lot A — Contrats d'extraction

### T-A1 — Modèle page extraite — TERMINÉ

**Sortie :** `src/control_tower/ocr/models.py`

**Critères d'acceptation :**

- numéro de page ;
- texte extrait ;
- méthode d'extraction ;
- dimensions quand une image est rendue ;
- avertissements page par page.

### T-A2 — Traçabilité des chunks — TERMINÉ

**Sorties :** `AtomicChunk.source_pages` et `AtomicChunk.extraction_method`.

**Preuve :** le test d'intégration vérifie qu'un chunk PDF pointe vers la page 1 et la méthode `native_pdf`.

## Lot B — Routeur documentaire

### T-B1 — TXT/Markdown — TERMINÉ

Lecture UTF-8 stricte et erreur explicite pour un encodage incompatible.

### T-B2 — PDF natif — TERMINÉ

Extraction page par page avec PyMuPDF sans appeler Tesseract quand suffisamment de texte natif existe.

### T-B3 — PDF scanné — TERMINÉ

Rendu de la page puis OCR Tesseract lorsque la page ne contient pas assez de texte natif.

### T-B4 — Images — TERMINÉ

Support de PNG, JPG, JPEG, TIFF, BMP et WebP avec préparation grayscale/autocontrast configurable.

## Lot C — Configuration projet

### T-C1 — Réglages OCR — TERMINÉ

Clés actives :

- `ocr.mode` : `auto`, `text_only`, `force_ocr` ;
- `ocr.languages` ;
- `ocr.dpi` ;
- `ocr.min_native_chars_per_page` ;
- `ocr.max_pages` ;
- `ocr.psm` et `ocr.oem` ;
- `ocr.grayscale` et `ocr.autocontrast` ;
- `ocr.tesseract_cmd`.

### T-C2 — Extensions autorisées — TERMINÉ

Le Policy Checker bloque une extension inconnue avant l'extraction.

## Lot D — Observabilité

### T-D1 — Artefact JSON — TERMINÉ

Chemin : `artifacts/<document_id>/extraction.json`.

Il contient les pages, méthodes, avertissements et métriques.

### T-D2 — Texte extrait — TERMINÉ

Chemin : `artifacts/<document_id>/extracted.txt`.

C'est exactement le texte transmis à l'atomiseur.

### T-D3 — Inspection d'un document — TERMINÉ

Commande :

```bash
control-tower inspect-document --project demo --document-id <ID>
```

## Lot E — Validation

### T-E1 — Tests déterministes — TERMINÉ

Douze tests : pipeline, policies, configuration, état, recherche, PDF natif, PDF scanné simulé, image simulée et artefacts.

### T-E2 — Preuve Tesseract réelle — TERMINÉE DANS L'ENVIRONNEMENT DE CONSTRUCTION

Commande :

```bash
python scripts/prove_ocr.py
```

Elle crée une image et un PDF scanné, les ingère avec le vrai Tesseract et affiche le texte extrait.

## Lot suivant recommandé — V0.4, sans ajout de “Brain” supplémentaire

1. table `documents` avec statut d'ingestion ;
2. idempotence par hash du fichier ;
3. réingestion contrôlée et invalidation ciblée ;
4. score qualité OCR et seuil de revue humaine ;
5. coordonnées de provenance par bloc ;
6. tests sur un corpus de documents réels.
