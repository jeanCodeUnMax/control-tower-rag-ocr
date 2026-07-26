from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class AtomizerConfig(BaseModel):
    max_chars: int = Field(default=700, ge=50, le=50_000)
    overlap_chars: int = Field(default=80, ge=0, le=10_000)


class OCRConfig(BaseModel):
    engine: str = Field(default="tesseract", pattern="^(tesseract|paddle)$")
    mode: str = Field(default="auto", pattern="^(auto|text_only|force_ocr)$")
    languages: str = "fra+eng"
    dpi: int = Field(default=200, ge=72, le=600)
    min_native_chars_per_page: int = Field(default=40, ge=0, le=100_000)
    max_pages: int = Field(default=2_000, ge=1, le=20_000)
    psm: int = Field(default=6, ge=0, le=13)
    oem: int = Field(default=3, ge=0, le=3)
    grayscale: bool = True
    autocontrast: bool = True
    tesseract_cmd: str | None = None
    paddle_lang: str = "fr"
    paddle_use_gpu: bool = False


class BatchConfig(BaseModel):
    """Bornes de traitement des PDF longs.

    max_context_units est une estimation interne, pas la fenêtre exacte d'un modèle.
    Une unité correspond approximativement à un token texte ou à une charge visuelle.
    """

    enabled: bool = True
    min_pages: int = Field(default=1, ge=1, le=20)
    max_pages: int = Field(default=5, ge=1, le=20)
    max_context_units: int = Field(default=18_000, ge=1_000, le=2_000_000)
    image_context_units: int = Field(default=2_000, ge=100, le=100_000)
    drawing_context_units: int = Field(default=600, ge=50, le=100_000)
    retry_limit: int = Field(default=2, ge=0, le=10)
    split_on_failure: bool = True
    strict_completeness: bool = True
    checkpoint_every_batch: bool = True

    @model_validator(mode="after")
    def validate_page_bounds(self) -> "BatchConfig":
        if self.min_pages > self.max_pages:
            raise ValueError("batching.min_pages doit être <= batching.max_pages")
        return self


class VisionProviderConfig(BaseModel):
    """Endpoint multimodal interchangeable.

    Les providers OpenAI-compatible couvrent OpenRouter, Ollama local et Ollama Cloud.
    Gemini utilise son endpoint REST natif. Aucun provider cloud n'est obligatoire.
    """

    name: str
    kind: Literal["openai_compatible", "gemini"] = "openai_compatible"
    enabled: bool = False
    model: str
    base_url: str
    api_key_env: str | None = None
    allow_missing_api_key: bool = False
    max_concurrency: int = Field(default=4, ge=1, le=128)
    requests_per_minute: int = Field(default=60, ge=1, le=100_000)
    timeout_seconds: int = Field(default=120, ge=5, le=900)
    max_retries: int = Field(default=4, ge=0, le=20)
    backoff_base_seconds: float = Field(default=0.5, ge=0.0, le=60.0)
    backoff_max_seconds: float = Field(default=20.0, ge=0.1, le=900.0)
    circuit_breaker_failures: int = Field(default=5, ge=1, le=100)
    circuit_breaker_cooldown_seconds: int = Field(default=60, ge=1, le=3600)
    estimated_cost_per_page_usd: float = Field(default=0.0, ge=0.0, le=100.0)
    strict_json_schema: bool = True
    headers: dict[str, str] = Field(default_factory=dict)
    provider_options: dict[str, Any] = Field(default_factory=dict)


def default_vision_providers() -> list[VisionProviderConfig]:
    return [
        VisionProviderConfig(
            name="ollama_local",
            enabled=False,
            model="qwen3-vl:4b",
            base_url="http://localhost:11434/v1",
            allow_missing_api_key=True,
            max_concurrency=1,
            requests_per_minute=120,
            strict_json_schema=False,
        ),
        VisionProviderConfig(
            name="openrouter_qwen",
            enabled=False,
            model="qwen/qwen3-vl-32b-instruct",
            base_url="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEY",
            max_concurrency=12,
            requests_per_minute=240,
            estimated_cost_per_page_usd=0.002,
            provider_options={
                "sort": "throughput",
                "allow_fallbacks": True,
                "require_parameters": True,
                "data_collection": "deny",
            },
        ),
        VisionProviderConfig(
            name="openrouter_gemini_flash",
            enabled=False,
            model="~google/gemini-flash-latest",
            base_url="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEY",
            max_concurrency=12,
            requests_per_minute=240,
            estimated_cost_per_page_usd=0.004,
            provider_options={
                "sort": "throughput",
                "allow_fallbacks": True,
                "require_parameters": True,
                "data_collection": "deny",
            },
        ),
        VisionProviderConfig(
            name="gemini_direct",
            kind="gemini",
            enabled=False,
            model="gemini-3.6-flash",
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key_env="GEMINI_API_KEY",
            max_concurrency=8,
            requests_per_minute=120,
            estimated_cost_per_page_usd=0.006,
        ),
        VisionProviderConfig(
            name="ollama_cloud",
            enabled=False,
            model="qwen3-vl:32b-cloud",
            base_url="https://ollama.com/v1",
            api_key_env="OLLAMA_API_KEY",
            max_concurrency=3,
            requests_per_minute=60,
            strict_json_schema=False,
        ),
    ]


class VisionConfig(BaseModel):
    """Analyse visuelle et routage adaptatif.

    local_fast rend le texte disponible immédiatement et diffère la vision complexe.
    balanced ne sollicite le cloud que pour les pages réellement complexes.
    cloud_turbo privilégie la vitesse et la cascade cloud.
    night_deep analyse toutes les pages par un provider multimodal.
    """

    enabled: bool = True
    provider: str = Field(default="router", pattern="^(local|openai|router)$")
    profile: str = Field(
        default="local_fast",
        pattern="^(local_fast|balanced|cloud_turbo|night_deep)$",
    )
    model: str = "gpt-5"
    detail: str = Field(default="high", pattern="^(low|high|auto)$")
    render_dpi: int = Field(default=144, ge=72, le=300)
    api_key_env: str = "OPENAI_API_KEY"
    timeout_seconds: int = Field(default=120, ge=5, le=900)
    require_provider_success: bool = False
    include_native_text_in_prompt: bool = True
    max_workers: int = Field(default=5, ge=1, le=128)
    max_cost_per_document_usd: float = Field(default=15.0, ge=0.0, le=100_000.0)
    stop_on_budget_exceeded: bool = False
    defer_complex_pages_in_fast_mode: bool = True
    provider_order: list[str] = Field(
        default_factory=lambda: [
            "ollama_local",
            "openrouter_qwen",
            "openrouter_gemini_flash",
            "gemini_direct",
            "ollama_cloud",
        ]
    )
    providers: list[VisionProviderConfig] = Field(default_factory=default_vision_providers)



class ConsolidationConfig(BaseModel):
    enabled: bool = True
    exact_text: bool = True
    near_text: bool = True
    semantic_embeddings: bool = False
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key_env: str = "OPENAI_API_KEY"
    near_duplicate_threshold: float = Field(default=0.93, ge=0.0, le=1.0)
    semantic_duplicate_threshold: float = Field(default=0.96, ge=0.0, le=1.0)
    minimum_text_chars: int = Field(default=40, ge=1, le=100_000)
    image_deduplication: bool = True
    image_phash_distance: int = Field(default=6, ge=0, le=64)
    vector_drawing_deduplication: bool = True
    canonical_policy: str = Field(default="first", pattern="^(first|longest)$")


class RetrievalConfig(BaseModel):
    top_k: int = Field(default=5, ge=1, le=100)
    hydration_budget_chars: int = Field(default=3000, ge=100, le=200_000)
    canonical_only: bool = True


class FeatureConfig(BaseModel):
    pseudocode: bool = True
    maieutic: bool = True
    kant_glove: bool = True
    reflection: bool = True
    web_search: bool = True
    consensusless: bool = False
    background_consolidation: bool = False


class PolicyConfig(BaseModel):
    mode: str = "enforce"
    max_ingest_bytes: int = Field(default=500_000_000, ge=1)
    blocked_extensions: list[str] = Field(
        default_factory=lambda: [".exe", ".dll", ".bat", ".cmd", ".sh", ".ps1"]
    )
    allowed_extensions: list[str] = Field(
        default_factory=lambda: [
            ".txt", ".md", ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"
        ]
    )


class MCPAccessRule(BaseModel):
    server_name: str
    access_level: Literal["authorized", "limited", "disabled"] = "authorized"
    rules: str = ""

class LLMProviderConfig(BaseModel):
    name: str
    kind: str = Field(pattern="^(openrouter|gemini|ollama|mistral|huggingface|llamacpp)$")
    enabled: bool = True
    model: str
    base_url: str | None = None
    api_key_env: str | None = None
    temperature: float = 0.3
    max_retries: int = 2
    timeout_seconds: int = 60
    role: str = "general"
    responsibilities: str = ""
    rules: str = ""
    mcp_enabled: bool = False
    mcp_servers: list[MCPAccessRule] = Field(default_factory=list)
    circuit_breaker_failures: int = Field(default=3, ge=1, le=100)
    circuit_breaker_cooldown_seconds: int = Field(default=120, ge=1, le=3600)
    
    @model_validator(mode='before')
    @classmethod
    def migrate_mcp_servers(cls, data: dict) -> dict:
        if "mcp_servers" in data and isinstance(data["mcp_servers"], list):
            new_servers = []
            for s in data["mcp_servers"]:
                if isinstance(s, str):
                    new_servers.append({"server_name": s, "access_level": "authorized", "rules": ""})
                else:
                    new_servers.append(s)
            data["mcp_servers"] = new_servers
        return data
    priority: int = 10


class LLMConfig(BaseModel):
    provider: str = Field(default="router", pattern="^(openrouter|gemini|router)$")
    
    # Pour la compatibilité avec l'ancienne configuration simple
    model: str = "openrouter/auto"
    api_key_env: str = "OPENROUTER_API_KEY"
    temperature: float = 0.3
    
    provider_order: list[str] = Field(
        default_factory=lambda: [
            "mistral_api",
            "openrouter_auto",
            "ollama_local",
            "gemini_flash",
        ]
    )
    providers: list[LLMProviderConfig] = Field(
        default_factory=lambda: [
            LLMProviderConfig(
                name="ollama_local",
                kind="ollama",
                enabled=False,
                model="llama3",
                base_url="http://localhost:11434/v1",
            ),
            LLMProviderConfig(
                name="ollama_cloud",
                kind="ollama",
                enabled=False,
                model="llama3",
                base_url="https://api.ollama.com/v1", # Exemple, à adapter
                api_key_env="OLLAMA_API_KEY",
            ),
            LLMProviderConfig(
                name="openrouter_auto",
                kind="openrouter",
                enabled=True,
                model="openrouter/auto",
                api_key_env="OPENROUTER_API_KEY",
            ),
            LLMProviderConfig(
                name="gemini_flash",
                kind="gemini",
                enabled=False,
                model="gemini-1.5-flash",
                api_key_env="GEMINI_API_KEY",
            ),
            LLMProviderConfig(
                name="mistral_api",
                kind="mistral",
                enabled=True,
                model="mistral-large-latest",
                api_key_env="MISTRAL_API_KEY",
            ),
            LLMProviderConfig(
                name="huggingface_api",
                kind="huggingface",
                enabled=False,
                model="Qwen/Qwen2.5-72B-Instruct",
                api_key_env="HF_TOKEN",
            ),
        ]
    )


class EmbeddingsConfig(BaseModel):
    provider: str = Field(default="local", pattern="^(local|gemini|openrouter|mistral)$")
    model: str = "all-MiniLM-L6-v2"
    api_key_env: str | None = None


class VectorStoreConfig(BaseModel):
    engine: str = Field(default="qdrant", pattern="^(qdrant|chroma)$")
    url: str = "http://localhost:6333"
    api_key_env: str | None = None
    collection_name: str = "control_tower_chunks"


class ProjectConfig(BaseModel):
    schema_version: str = "1.5"
    atomizer: AtomizerConfig = Field(default_factory=AtomizerConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    batching: BatchConfig = Field(default_factory=BatchConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    consolidation: ConsolidationConfig = Field(default_factory=ConsolidationConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    policy: PolicyConfig = Field(default_factory=PolicyConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


class RuntimeSettings(BaseModel):
    workspace_root: Path = Path(os.getenv("CONTROL_TOWER_HOME", ".control_tower")) / "projects"


settings = RuntimeSettings()


def default_project_config() -> ProjectConfig:
    return ProjectConfig()


def load_project_config(path: Path) -> ProjectConfig:
    if not path.exists():
        return default_project_config()
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ProjectConfig.model_validate(raw)


def write_project_config(path: Path, config: ProjectConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(config.model_dump(mode="python"), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def parse_cli_value(raw: str) -> Any:
    """Convertit 'true', '42', '[a,b]'... en valeur YAML typée."""
    return yaml.safe_load(raw)


def set_nested_value(data: dict[str, Any], dotted_key: str, value: Any) -> dict[str, Any]:
    """Modifie une clé pointée, y compris un index de liste (`providers.1.enabled`)."""
    parts = [part for part in dotted_key.split(".") if part]
    if not parts:
        raise ValueError("La clé de configuration est vide.")
    cursor: Any = data
    for position, part in enumerate(parts[:-1]):
        next_part = parts[position + 1]
        if isinstance(cursor, dict):
            if part not in cursor:
                cursor[part] = [] if next_part.isdigit() else {}
            cursor = cursor[part]
        elif isinstance(cursor, list):
            if not part.isdigit():
                raise ValueError(f"Un index numérique est requis à la place de '{part}'.")
            index = int(part)
            if index < 0 or index >= len(cursor):
                raise ValueError(f"Index de configuration hors limites: {index}.")
            cursor = cursor[index]
        else:
            raise ValueError(f"La clé intermédiaire '{part}' n'est ni un objet ni une liste.")

    last = parts[-1]
    if isinstance(cursor, dict):
        cursor[last] = value
    elif isinstance(cursor, list):
        if not last.isdigit():
            raise ValueError(f"Un index numérique est requis à la place de '{last}'.")
        index = int(last)
        if index < 0 or index >= len(cursor):
            raise ValueError(f"Index de configuration hors limites: {index}.")
        cursor[index] = value
    else:
        raise ValueError(f"Impossible de modifier '{dotted_key}'.")
    return data

