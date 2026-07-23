# V0.4 — PDF long, vision structurée et consolidation

## Ajouts

- planificateur adaptatif de lots 1–5 pages ;
- estimation de charge à partir du texte, des images et dessins ;
- registre exhaustif des pages avec états, tentatives et lots ;
- checkpoint atomique après chaque lot ;
- division récursive des lots fautifs ;
- blocage de l'indexation si une page échoue en mode strict ;
- artefact JSON par page ;
- analyse locale structurée et adaptateur multimodal OpenAI ;
- fusion du texte manuscrit/multimodal avec le texte OCR ;
- module pseudocode ;
- consolidation exacte, quasi exacte et sémantique optionnelle ;
- déduplication des actifs visuels par SHA-256 et dHash ;
- preuves d'occurrence conservées sur le canonique ;
- recherche canonique par défaut ;
- script reproductible de preuve 800 pages.

## Validation

- 19 tests automatisés ;
- preuve réelle : 800/800 pages terminées, 0 échec, 0 page manquante ;
- 800 chunks bruts consolidés en 8 chunks canoniques ;
- 24 actifs visuels consolidés en 3 actifs canoniques.

## Non couvert

- appel multimodal réel sans clé API ;
- reprise d'une ingestion interrompue par redémarrage ;
- index vectoriel de recherche ;
- consensus-less dans le chemin principal.
