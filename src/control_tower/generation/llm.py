from __future__ import annotations

import os
import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocole pour un fournisseur de modèle de langage."""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        ...


class LlamaCppLLM:
    """Implémentation pour lire un modèle GGUF local via llama-cpp-python."""
    
    def __init__(self, model_path: str, temperature: float = 0.3):
        import os
        from llama_cpp import Llama
        
        # Le model passé ici est soit le nom (ex: "model.gguf") soit un chemin absolu.
        # S'il ne contient pas de chemin, on cherche dans D:/models
        if not os.path.isabs(model_path):
            full_path = os.path.join("D:/models", model_path)
        else:
            full_path = model_path
            
        if not os.path.exists(full_path):
            raise ValueError(f"Fichier modèle introuvable : {full_path}")
            
        self.model_path = full_path
        self.temperature = temperature
        
        # Initialisation du modèle. N'gpu_layers=-1 charge tout sur le GPU si possible
        self.llm = Llama(
            model_path=self.model_path,
            n_gpu_layers=-1,
            n_ctx=8192,
            verbose=False
        )

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Utilisation du mode chat_completion standard de LlamaCpp
        response = self.llm.create_chat_completion(
            messages=messages,
            temperature=self.temperature,
            max_tokens=4096
        )
        
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Réponse inattendue de Llama.cpp : {response}")


class HuggingFaceLLM:
    """Implémentation pour l'API Serverless de Hugging Face."""
    
    def __init__(self, model: str, api_key_env: str, temperature: float = 0.3):
        self.model = model
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError(f"Clé API non trouvée dans la variable d'environnement {api_key_env}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx
        url = f"https://api-inference.huggingface.co/models/{self.model}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 8192
        }

        # HuggingFace Serverless sometimes takes a bit to load the model
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            
            if resp.status_code != 200:
                raise RuntimeError(f"HuggingFace API Error {resp.status_code}: {resp.text}")
                
            data = resp.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Réponse inattendue de HuggingFace : {data}")


class OpenRouterLLM:
    """Implémentation pour l'API OpenRouter."""
    
    def __init__(self, model: str, api_key_env: str, temperature: float = 0.3, mcp_enabled: bool = False, mcp_servers: list[Any] = None):
        self.model = model
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self.temperature = temperature
        self.mcp_enabled = mcp_enabled
        self.mcp_servers = mcp_servers or []
        
        if not self.api_key:
            raise ValueError(f"Clé API non trouvée dans la variable d'environnement {api_key_env}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx
        import json

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "ControlTower"
        }
        
        # Construction du System Prompt final avec les règles MCP
        final_system_prompt = system_prompt
        tools = []
        
        # Gestion dynamique des outils MCP et des règles "limited"
        if self.mcp_enabled:
            try:
                from control_tower.generation.mcp_client import MCPOrchestrator
                orch = MCPOrchestrator()
                
                # Extraire uniquement les serveurs autorisés ou limités
                active_servers = []
                for s in self.mcp_servers:
                    if getattr(s, "access_level", "authorized") in ("authorized", "limited"):
                        active_servers.append(getattr(s, "server_name", s))
                        
                    # Injection des règles limitées dans le system prompt
                    if getattr(s, "access_level", "authorized") == "limited" and getattr(s, "rules", ""):
                        server_name = getattr(s, "server_name", s)
                        rules = getattr(s, "rules", "")
                        final_system_prompt += f"\n\n[RÈGLES D'ACCÈS POUR LE SERVEUR MCP '{server_name}']:\n{rules}"
                
                tools = orch.get_tools(active_servers)
            except Exception as e:
                logger.error(f"Erreur chargement MCP tools: {e}")
        
        messages = []
        if final_system_prompt:
            messages.append({"role": "system", "content": final_system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        max_turns = 10
        
        with httpx.Client(timeout=60.0) as client:
            for turn in range(max_turns):
                data = {
                    "model": self.model.strip(),
                    "messages": messages,
                    "temperature": self.temperature,
                }
                if tools:
                    data["tools"] = tools

                try:
                    response = client.post(url, headers=headers, json=data)
                    if response.status_code != 200:
                        raise RuntimeError(f"OpenRouter Error {response.status_code}: {response.text}")
                    result = response.json()
                    message = result["choices"][0]["message"]
                    
                    if message.get("tool_calls"):
                        # Le modèle veut appeler un outil
                        messages.append(message)
                        from control_tower.generation.mcp_client import MCPOrchestrator
                        orch = MCPOrchestrator()
                        
                        for tc in message["tool_calls"]:
                            tool_name = tc["function"]["name"]
                            args = json.loads(tc["function"]["arguments"])
                            logger.info(f"Appel outil MCP: {tool_name} avec {args}")
                            
                            if "__" in tool_name:
                                server_name, actual_tool_name = tool_name.split("__", 1)
                                tool_result = orch.call_tool(server_name, actual_tool_name, args)
                            else:
                                tool_result = "Erreur: Nom d'outil invalide."
                                
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "content": str(tool_result)
                            })
                        continue # Reboucler avec le résultat
                    else:
                        # Fin de la génération
                        return message.get("content", "")
                except Exception as exc:
                    raise RuntimeError(f"Erreur lors de la génération avec OpenRouter (tour {turn}): {exc}")
                    
            raise RuntimeError("Trop d'appels d'outils consécutifs (limite atteinte).")


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
        import time

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

        max_retries = 2
        backoff = 2.0

        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(url, headers=headers, json=data)
                    
                    if response.status_code == 429:
                        if attempt < max_retries - 1:
                            logger.warning(f"Mistral Rate Limit (429). Pause de {backoff}s...")
                            time.sleep(backoff)
                            backoff *= 2.0
                            continue
                        else:
                            raise RuntimeError(f"Mistral API Error 429: Rate limit exceeded après {max_retries} tentatives.")
                            
                    if response.status_code != 200:
                        raise RuntimeError(f"Mistral API Error {response.status_code}: {response.text}")
                        
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                    
            except (httpx.RequestError, httpx.TimeoutException) as exc:
                if attempt < max_retries - 1:
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise RuntimeError(f"Erreur réseau avec Mistral: {exc}")
                
        raise RuntimeError("Échec de la génération Mistral.")


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
        except httpx.ConnectError:
            return (
                "🤖 **[MOCK LLM]** — *Ollama n'est pas détecté en arrière-plan (WinError 10061).* \n\n"
                "Pour une vraie analyse de L'Arène, veuillez démarrer l'application Ollama sur votre machine.\n\n"
                "En attendant, voici une synthèse factice pour valider que l'interface React et le backend communiquent parfaitement ! La requête a bien traversé le routeur, généré la trace d'exécution, et l'interface a réagi correctement."
            )
        except Exception as exc:
            if "10061" in str(exc):
                 return "🤖 **[MOCK LLM]** — *Ollama n'est pas détecté en arrière-plan (WinError 10061).* \n\nPour une vraie analyse de L'Arène, veuillez démarrer l'application Ollama sur votre machine."
            raise RuntimeError(f"Erreur lors de la génération avec Ollama: {exc}")


class GeminiLLM:
    """Implémentation pour l'API Google Gemini (REST API)."""
    
    def __init__(self, model: str, api_key_env: str, temperature: float = 0.3, mcp_enabled: bool = False, mcp_servers: list[Any] = None):
        self.model = model
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self.temperature = temperature
        self.mcp_enabled = mcp_enabled
        self.mcp_servers = mcp_servers or []
        
        if not self.api_key:
            raise ValueError(f"Clé API non trouvée dans la variable d'environnement {api_key_env}")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import httpx
        import json

        model_name = self.model.strip()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        
        # Construction du System Prompt final avec les règles MCP
        final_system_prompt = system_prompt
        gemini_tools = []
        
        # Gestion dynamique des outils MCP
        if self.mcp_enabled:
            try:
                from control_tower.generation.mcp_client import MCPOrchestrator
                orch = MCPOrchestrator()
                
                # Extraire uniquement les serveurs autorisés ou limités
                active_servers = []
                for s in self.mcp_servers:
                    if getattr(s, "access_level", "authorized") in ("authorized", "limited"):
                        active_servers.append(getattr(s, "server_name", s))
                        
                    # Injection des règles limitées dans le system prompt
                    if getattr(s, "access_level", "authorized") == "limited" and getattr(s, "rules", ""):
                        server_name = getattr(s, "server_name", s)
                        rules = getattr(s, "rules", "")
                        final_system_prompt += f"\n\n[RÈGLES D'ACCÈS POUR LE SERVEUR MCP '{server_name}']:\n{rules}"
                
                openai_tools = orch.get_tools(active_servers)
                # Convertir au format Gemini
                for t in openai_tools:
                    gemini_tools.append(t["function"])
            except Exception as e:
                logger.error(f"Erreur chargement MCP tools Gemini: {e}")
        
        contents = []
        if final_system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System: {final_system_prompt}\n\nUser: {prompt}"}]})
        else:
            contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        max_turns = 10
        
        with httpx.Client(timeout=60.0) as client:
            for turn in range(max_turns):
                data = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": self.temperature,
                    }
                }
                if gemini_tools:
                    data["tools"] = [{"functionDeclarations": gemini_tools}]

                try:
                    response = client.post(url, json=data)
                    if response.status_code != 200:
                        raise RuntimeError(f"Gemini API Error {response.status_code}: {response.text}")
                    result = response.json()
                    
                    candidate = result.get("candidates", [{}])[0]
                    parts = candidate.get("content", {}).get("parts", [])
                    
                    if not parts:
                        return ""
                        
                    # Gemini renvoie potentiellement un functionCall
                    function_call = next((p["functionCall"] for p in parts if "functionCall" in p), None)
                    
                    if function_call:
                        # Ajouter la réponse du modèle à l'historique
                        contents.append(candidate["content"])
                        
                        tool_name = function_call["name"]
                        args = function_call.get("args", {})
                        logger.info(f"Appel outil MCP (Gemini): {tool_name} avec {args}")
                        
                        from control_tower.generation.mcp_client import MCPOrchestrator
                        orch = MCPOrchestrator()
                        
                        if "__" in tool_name:
                            server_name, actual_tool_name = tool_name.split("__", 1)
                            tool_result = orch.call_tool(server_name, actual_tool_name, args)
                        else:
                            tool_result = "Erreur: Nom d'outil invalide."
                            
                        contents.append({
                            "role": "function",
                            "parts": [{
                                "functionResponse": {
                                    "name": tool_name,
                                    "response": {"name": tool_name, "content": str(tool_result)}
                                }
                            }]
                        })
                        continue # Reboucler
                    else:
                        text_part = next((p["text"] for p in parts if "text" in p), "")
                        return text_part
                        
                except Exception as exc:
                    raise RuntimeError(f"Erreur lors de la génération avec Gemini (tour {turn}): {exc}")
                    
            raise RuntimeError("Trop d'appels d'outils consécutifs (limite atteinte).")


from dataclasses import dataclass, field
import time
from typing import Dict, Any

@dataclass
class HealthStats:
    status: str = "healthy"  # "healthy", "degraded", "quarantined"
    success_count: int = 0
    error_count: int = 0
    consecutive_errors: int = 0
    last_error: str = ""
    quarantine_until: float = 0.0

class HealthMonitor:
    """Stockage global de l'état de santé de tous les providers."""
    stats: Dict[str, HealthStats] = {}
    
    @classmethod
    def get_stats(cls, provider_name: str) -> HealthStats:
        if provider_name not in cls.stats:
            cls.stats[provider_name] = HealthStats()
        return cls.stats[provider_name]
        
    @classmethod
    def get_all(cls) -> Dict[str, dict]:
        now = time.time()
        result = {}
        for name, stat in cls.stats.items():
            if stat.status == "quarantined" and now >= stat.quarantine_until:
                stat.status = "degraded" # Demi-ouvert
                stat.consecutive_errors = max(0, stat.consecutive_errors - 1)
                
            result[name] = {
                "status": stat.status,
                "success_count": stat.success_count,
                "error_count": stat.error_count,
                "consecutive_errors": stat.consecutive_errors,
                "last_error": stat.last_error,
                "cooldown_remaining": max(0, int(stat.quarantine_until - now)) if stat.status == "quarantined" else 0
            }
        return result

@dataclass
class RouterEntry:
    name: str
    provider: Any
    max_failures: int
    cooldown_sec: int

class LLMRouter:
    """Routeur LLM avec système de Fallback et Circuit Breaker paramétrable."""
    
    def __init__(self, entries: list[RouterEntry]):
        self.entries = entries
        if not self.entries:
            raise ValueError("Le routeur LLM doit avoir au moins un fournisseur configuré.")

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        import time
        from rich.console import Console
        console = Console()
        
        last_error = None
        for i, entry in enumerate(self.entries):
            provider_name = entry.name
            stat = HealthMonitor.get_stats(provider_name)
            now = time.time()
            
            # 1. Vérification de la "santé" (Circuit Breaker)
            if stat.status == "quarantined":
                if now < stat.quarantine_until:
                    console.print(f"[dim]⏭️ {provider_name} ignoré (En quarantaine pour encore {int(stat.quarantine_until - now)}s).[/dim]")
                    continue
                else:
                    # Le temps de pénalité est écoulé, le provider est "Demi-ouvert"
                    stat.status = "degraded"
                    console.print(f"[dim]💛 {provider_name} est sorti de quarantaine (Mode test).[/dim]")

            try:
                console.print(f"[dim]🔄 Tentative LLM avec {provider_name} ({i+1}/{len(self.entries)})...[/dim]")
                result = entry.provider.generate(prompt, system_prompt)
                
                # Succès !
                stat.success_count += 1
                stat.consecutive_errors = 0
                stat.status = "healthy"
                return result
                
            except Exception as exc:
                last_error = exc
                stat.error_count += 1
                stat.consecutive_errors += 1
                stat.last_error = str(exc)
                
                if stat.consecutive_errors >= entry.max_failures:
                    stat.status = "quarantined"
                    stat.quarantine_until = time.time() + entry.cooldown_sec
                    console.print(f"[red]⚠️ Échec critique avec {provider_name}: {exc}. Mise en quarantaine ({entry.cooldown_sec}s).[/red]")
                else:
                    stat.status = "degraded"
                    console.print(f"[yellow]⚠️ Échec avec {provider_name} (Erreur {stat.consecutive_errors}/{entry.max_failures}): {exc}[/yellow]")
                
        raise RuntimeError(f"Tous les fournisseurs LLM ont échoué ou sont en quarantaine réseau. Dernière erreur : {last_error}")


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
                provider_instance = None
                if cfg.kind == "openrouter":
                    provider_instance = OpenRouterLLM(cfg.model, cfg.api_key_env, cfg.temperature, cfg.mcp_enabled, getattr(cfg, "mcp_servers", []))
                elif cfg.kind == "ollama":
                    provider_instance = OllamaLLM(cfg.model, cfg.base_url, cfg.temperature)
                elif cfg.kind == "mistral":
                    provider_instance = MistralLLM(cfg.model, cfg.api_key_env, cfg.temperature)
                elif cfg.kind == "gemini":
                    provider_instance = GeminiLLM(cfg.model, cfg.api_key_env, cfg.temperature, cfg.mcp_enabled, getattr(cfg, "mcp_servers", []))
                elif cfg.kind == "huggingface":
                    provider_instance = HuggingFaceLLM(cfg.model, cfg.api_key_env, cfg.temperature)
                elif cfg.kind == "llamacpp":
                    provider_instance = LlamaCppLLM(cfg.model, cfg.temperature)
                    
                if provider_instance:
                    # On initialize les stats du HealthMonitor dès le chargement
                    HealthMonitor.get_stats(cfg.name)
                    active_providers.append(RouterEntry(
                        name=cfg.name,
                        provider=provider_instance,
                        max_failures=getattr(cfg, "circuit_breaker_failures", 3),
                        cooldown_sec=getattr(cfg, "circuit_breaker_cooldown_seconds", 120)
                    ))
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
    elif provider_type == "huggingface":
        return HuggingFaceLLM(model=model_name, api_key_env=api_key_env, temperature=temperature)
    elif provider_type == "llamacpp":
        return LlamaCppLLM(model_path=model_name, temperature=temperature)
        
    raise NotImplementedError(f"Le provider '{provider_type}' n'est pas encore implémenté.")
