# 🚀 Control Tower RAG & OCR - Synthèse du Projet

> **Projet de développement d'un pipeline RAG (Retrieval-Augmented Generation) avancé, multi-modèles (Ollama, Mistral, OpenRouter) doté d'une Arène de Consensus Cognitive.**

## 📖 Synthèse du Projet
Control Tower est un système de gestion documentaire intelligent qui ne se contente pas d'ingérer bêtement des documents. Il déduplique les fichiers, atomise le texte, évalue sa cohérence à travers des paradigmes cognitifs (Maïeutique, Kant, Pseudocode) et consolide le tout dans une base de données vectorielle (Qdrant / Zvec). 
La grande force du projet est son **Arène de Consensus** : face à une question, plusieurs LLMs débattent en parallèle, puis un modèle "Juge" (ex: Mistral) compile une réponse exécutive et strictement factuelle (anti-hallucination) à l'aide d'une température très basse (0.1) et d'un contexte vectoriel ultra-précis extrait sous vos yeux.

---

## ⚙️ Comment ça fonctionne ? (Architecture)

1. **Ingestion & Déduplication** : Le système calcule un hash unique (SHA-256) du document. Si le document existe déjà à l'identique, l'ingestion est bloquée pour éviter de polluer la base.
2. **Extraction & Atomisation** : Le document est découpé en fragments (chunks) sémantiques.
3. **Réflexion & Enrichissement** : Avant l'indexation, des LLMs enrichissent les fragments via différents "Paradigmes Cognitifs" (questionnement socratique, synthèse philosophique, etc.) pour augmenter la qualité de la donnée.
4. **Vectorisation** : Les fragments sont plongés (embedded) et stockés dans notre base vectorielle locale (Qdrant / Zvec).
5. **L'Arène de Consensus (QA)** : 
   - L'utilisateur pose une question.
   - Les vecteurs les plus pertinents sont extraits de la base.
   - 3 à 5 LLMs tentent de répondre en parallèle.
   - Le "Juge Final" utilise le paradigme **Executive** pour livrer la vérité froide et factuelle.

---

## 💻 Comment ça s'installe ?

### 1. Backend (Python)
```powershell
# Créer l'environnement virtuel et l'activer
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
```

### 2. Frontend (React)
```powershell
cd frontend
npm install
npm run dev
```

### 3. Services tiers
- Assurez-vous d'avoir **Ollama** lancé en local avec les modèles téléchargés (ex: `llama3`).
- Exportez vos clés API dans votre environnement (ex: `MISTRAL_API_KEY`).

---

## 🎮 Comment ça s'utilise ?

### Via l'Interface Web (Recommandé)
Accédez à `http://localhost:5173` (ou le port indiqué par Vite) pour utiliser l'interface graphique. Vous pourrez sélectionner vos LLMs, interroger l'Arène, voir les "Vecteurs extraits de la base" et activer la recherche Web en temps réel.

### Via le Terminal (CLI)
- **Initier un projet** : `.venv\Scripts\python.exe src/control_tower/cli.py init-project demo`
- **Ingérer un document** : `.venv\Scripts\python.exe src/control_tower/cli.py ingest --project demo "chemin/vers/doc.pdf"`
- **Lancer l'Arène (Consensus)** : `.venv\Scripts\python.exe src/control_tower/cli.py synthesize --project demo "Votre question ?" --paradigm executive`

---

## 🛠 Comment ça se règle ?

Toute la puissance de Control Tower réside dans ses réglages :
- **Paradigmes cognitifs** : Modifiables depuis l'UI (Executive, Socratic, Analogy, Discovery). L'Executive est forcé à une température de `0.1` pour éviter formellement les hallucinations.
- **Routage des modèles** : Géré dans la configuration du projet (ex: `.control_tower/projects/demo/config.yaml`), vous pouvez activer/désactiver les providers (OpenRouter, Gemini, Mistral, Ollama) et définir vos priorités.
- **Moteur Vectoriel** : Le moteur est configurable (Qdrant local ou base Zvec distante).

---

## 🎯 Ce qu'il reste à faire (Roadmap)

1. [ ] **Mise à jour Intelligente des Documents** : Implémenter un scan des "2 premières pages" pour détecter les nouvelles versions d'un même document, afin d'*écraser* dynamiquement l'ancienne version vectorisée (au lieu de simplement bloquer par hash).
2. [ ] **Nettoyage de la Base Vectorielle** : Créer une commande de maintenance (Garbage Collector) pour purger les vieux documents "fantômes" de Qdrant et synchroniser proprement le RAG avec les fichiers réels.
3. [ ] **Quality Scoring des Ingestions** : Assigner une "note de cohérence" lors de l'ingestion par un modèle Juge. Si la note est trop faible, le système relance l'extraction avec de meilleurs conseils avant de passer à l'embedding.
4. [ ] **Hybridation de la Recherche** : Combiner la recherche purement sémantique (vecteurs) avec la recherche full-text classique (BM25) pour une précision infaillible.
