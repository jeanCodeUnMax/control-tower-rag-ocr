import os
import json
import logging
import asyncio
import threading
from typing import Any, Dict, List, Optional
from pathlib import Path

# Tentative d'import du SDK mcp
try:
    from mcp.client.stdio import stdio_client, StdioServerParameters
    from mcp.client.session import ClientSession
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

logger = logging.getLogger(__name__)

class MCPServerContext:
    def __init__(self, name: str, params: "StdioServerParameters"):
        self.name = name
        self.params = params
        self.session: Optional["ClientSession"] = None
        self._exit_stack = None

class MCPOrchestrator:
    """Gestionnaire global des serveurs MCP. Utilise un thread dédié pour l'event loop asyncio."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MCPOrchestrator, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: str = None):
        if self._initialized:
            return
            
        if config_path is None:
            # Pointe vers le fichier copié dans le projet
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            config_path = str(base_dir / "mcp_config.json")
            
        self.config_path = config_path
        self.servers: Dict[str, MCPServerContext] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready_event = threading.Event()
        
        if not MCP_AVAILABLE:
            logger.warning("Le package 'mcp' n'est pas installé. MCPOrchestrator sera inactif.")
            self._initialized = True
            return
            
        self._load_config()
        self._start_loop_in_thread()
        self._initialized = True

    def _load_config(self):
        if not os.path.exists(self.config_path):
            logger.warning(f"Fichier MCP non trouvé: {self.config_path}")
            return
            
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            mcp_servers = data.get("mcpServers", {})
            for name, config in mcp_servers.items():
                if config.get("disabled", False):
                    continue
                    
                command = config.get("command", "node")
                args = config.get("args", [])
                env = config.get("env", {})
                
                # Fusionner avec l'env système courant
                full_env = os.environ.copy()
                full_env.update(env)
                
                params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=full_env
                )
                self.servers[name] = MCPServerContext(name, params)
                logger.info(f"Serveur MCP configuré: {name}")
                
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {self.config_path}: {e}")

    def _start_loop_in_thread(self):
        """Démarre une event loop asyncio dans un thread séparé pour maintenir les sessions MCP."""
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.call_soon_threadsafe(self._ready_event.set)
            self._loop.run_forever()
            
        self._thread = threading.Thread(target=run_loop, daemon=True, name="MCP_Loop")
        self._thread.start()
        self._ready_event.wait()
        
        # Initialiser les serveurs
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._init_all_servers(), self._loop)

    async def _init_all_servers(self):
        from contextlib import AsyncExitStack
        for name, ctx in self.servers.items():
            try:
                ctx._exit_stack = AsyncExitStack()
                read, write = await ctx._exit_stack.enter_async_context(stdio_client(ctx.params))
                ctx.session = await ctx._exit_stack.enter_async_context(ClientSession(read, write))
                await ctx.session.initialize()
                logger.info(f"Serveur MCP '{name}' initialisé avec succès.")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation du serveur MCP '{name}': {e}")
                if ctx._exit_stack:
                    await ctx._exit_stack.aclose()
                    ctx._exit_stack = None

    def get_tools(self, allowed_servers: List[str] = None) -> List[Dict[str, Any]]:
        """Récupère les schémas d'outils (synchronement) depuis les serveurs autorisés."""
        if not MCP_AVAILABLE or not self._loop:
            return []
            
        async def _get():
            tools = []
            for name, ctx in self.servers.items():
                if allowed_servers is not None and name not in allowed_servers:
                    continue
                if ctx.session:
                    try:
                        result = await ctx.session.list_tools()
                        # result.tools est une liste de Tool
                        for t in result.tools:
                            # Convertir le schéma MCP au format OpenAI (compatible OpenRouter/Gemini)
                            tools.append({
                                "type": "function",
                                "function": {
                                    "name": f"{name}__{t.name}", # ex: filesystem__read_file
                                    "description": t.description or "",
                                    "parameters": t.inputSchema
                                }
                            })
                    except Exception as e:
                        logger.error(f"Erreur get_tools sur {name}: {e}")
            return tools

        future = asyncio.run_coroutine_threadsafe(_get(), self._loop)
        return future.result(timeout=10) # Attendre jusqu'à 10s

    def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> str:
        """Exécute un outil (synchronement)."""
        if not MCP_AVAILABLE or not self._loop:
            return "Erreur: MCP non disponible."
            
        ctx = self.servers.get(server_name)
        if not ctx or not ctx.session:
            return f"Erreur: Serveur MCP '{server_name}' non trouvé ou non connecté."
            
        async def _call():
            try:
                result = await ctx.session.call_tool(tool_name, arguments)
                # result.content est une liste de TextContent, etc.
                text_outputs = []
                for content in result.content:
                    if content.type == "text":
                        text_outputs.append(content.text)
                return "\n".join(text_outputs)
            except Exception as e:
                return f"Erreur lors de l'appel de l'outil {tool_name}: {e}"

        future = asyncio.run_coroutine_threadsafe(_call(), self._loop)
        return future.result(timeout=60)
