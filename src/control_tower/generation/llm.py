from __future__ import annotations

import os
import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocole pour un fournisseur de modèle de langage."""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        ...


class OpenRouterLLM:
    """Implémentation pour l'API OpenRouter."""
    
    def __init__(self, model: str, api_key_env: str, temperature: float = 0.3):
        self.model = model
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError(f"Clé API non trouvée dans la variable d'environnement {api_key_env}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/jeanCodeUnMax/control-tower-rag-ocr",
            "X-Title": "Control Tower OCR",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=data)
                if response.status_code != 200:
                    raise RuntimeError(f"OpenRouter Error {response.status_code}: {response.text}")
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Erreur lors de la génération avec OpenRouter: {exc}")


class MistralLLM:
    """Implémentation pour l'API Officielle Mistral."""
    
    def __init__(self, model: str, api_key_env: str, temperature: float = 0.3):
        self.model = model
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError(f"Clé API non trouvée dans la variable d'environnement {api_key_env}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx

        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, headers=headers, json=data)
                if response.status_code != 200:
                    raise RuntimeError(f"Mistral API Error {response.status_code}: {response.text}")
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Erreur lors de la génération avec Mistral: {exc}")


class OllamaLLM:
    """Implémentation pour Ollama local (100% hors ligne)."""
    
    def __init__(self, model: str, base_url: str = "http://localhost:11434/v1", temperature: float = 0.3):
        self.model = model
        self.base_url = os.environ.get("OLLAMA_BASE_URL", base_url)
        self.temperature = temperature

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx

        # Utiliser l'API Native Ollama en forçant l'IPv4
        url = "http://127.0.0.1:11434/api/chat"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": self.model.strip(),
            "messages": messages,
            "options": {
                "temperature": self.temperature,
            },
            "stream": False
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=data)
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama Error {response.status_code}: {response.text}")
                result = response.json()
                return result["message"]["content"]
        except Exception as exc:
            raise RuntimeError(f"Erreur lors de la génération avec Ollama: {exc}")


class GeminiLLM:
    """Implémentation pour l'API Google Gemini (REST API)."""
    
    def __init__(self, model: str, api_key_env: str, temperature: float = 0.3):
        self.model = model
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError(f"Clé API non trouvée dans la variable d'environnement {api_key_env}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # Gemini utilise un format légèrement différent (contents/parts)
        contents = []
        if system_prompt:
            # Note: Le system prompt est géré différemment sur l'API REST v1beta, on va l'injecter avec le texte
            contents.append({"role": "user", "parts": [{"text": f"System: {system_prompt}\n\nUser: {prompt}"}]})
        else:
            contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
            }
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(url, json=data)
                if response.status_code != 200:
                    raise RuntimeError(f"Gemini API Error {response.status_code}: {response.text}")
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as exc:
            raise RuntimeError(f"Erreur lors de la génération avec Gemini: {exc}")


class LLMRouter:
    """Routeur LLM avec système de Fallback."""
    
    def __init__(self, providers: list[LLMProvider]):
        self.providers = providers
        if not self.providers:
            raise ValueError("Le routeur LLM doit avoir au moins un fournisseur configuré.")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        from rich.console import Console
        console = Console()
        
        last_error = None
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__
            try:
                console.print(f"[dim]🔄 Tentative LLM avec {provider_name} ({i+1}/{len(self.providers)})...[/dim]")
                return provider.generate(prompt, system_prompt)
            except Exception as exc:
                last_error = exc
                console.print(f"[yellow]⚠️ Échec avec {provider_name}: {exc}. Passage au fournisseur suivant...[/yellow]")
                
        raise RuntimeError(f"Tous les fournisseurs LLM ont échoué. Dernière erreur : {last_error}")


def get_llm_provider(provider_type: str, config_obj=None, model_name: str = "", api_key_env: str = "", temperature: float = 0.3) -> LLMProvider:
    """Factory pour récupérer le LLM selon la configuration."""
    
    # 1. Mode Router avancé
    if provider_type == "router" and config_obj is not None:
        active_providers = []
        for provider_name in config_obj.provider_order:
            # Trouver la conf correspondante
            cfg = next((p for p in config_obj.providers if p.name == provider_name and p.enabled), None)
            if not cfg:
                continue
                
            try:
                if cfg.kind == "openrouter":
                    active_providers.append(OpenRouterLLM(cfg.model, cfg.api_key_env, cfg.temperature))
                elif cfg.kind == "ollama":
                    active_providers.append(OllamaLLM(cfg.model, cfg.base_url, cfg.temperature))
                elif cfg.kind == "mistral":
                    active_providers.append(MistralLLM(cfg.model, cfg.api_key_env, cfg.temperature))
                elif cfg.kind == "gemini":
                    active_providers.append(GeminiLLM(cfg.model, cfg.api_key_env, cfg.temperature))
            except ValueError as ve:
                logger.debug(f"Fournisseur {cfg.name} ignoré: {ve}")
                
        if not active_providers:
            raise ValueError("Aucun fournisseur LLM activé et valide n'a pu être chargé dans le Rotator.")
            
        return LLMRouter(active_providers)
        
    # 2. Modes simples (rétro-compatibilité)
    if provider_type == "openrouter":
        return OpenRouterLLM(model=model_name, api_key_env=api_key_env, temperature=temperature)
    elif provider_type == "mistral":
        return MistralLLM(model=model_name, api_key_env=api_key_env, temperature=temperature)
    elif provider_type == "gemini":
        return GeminiLLM(model=model_name, api_key_env=api_key_env, temperature=temperature)
    elif provider_type == "ollama":
        return OllamaLLM(model=model_name, temperature=temperature)
        
    raise NotImplementedError(f"Le provider '{provider_type}' n'est pas encore implémenté.")
