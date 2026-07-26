import React, { useState, useEffect } from 'react';
import { Cpu, Server, Save, Check, Loader2, Edit, X, Activity } from 'lucide-react';

interface ProviderConfig {
  name: string;
  kind: string;
  enabled: boolean;
  model: string;
  base_url: string | null;
  api_key_env: string | null;
  temperature: number;
  max_retries: number;
  timeout_seconds: number;
  role: string;
  rules: string;
  mcp_enabled: boolean;
  mcp_servers: { server_name: string; access_level: 'authorized' | 'limited' | 'disabled'; rules: string }[];
  priority: number;
  priority: number;
}

const ROLE_PROMPTS: Record<string, string> = {
  general: "Tu es un assistant IA générique, conçu pour aider l'utilisateur avec précision et concision.",
  expert: "Tu es un expert analytique. Ton rôle est d'analyser en profondeur les documents fournis, d'extraire des faits précis et de structurer tes réponses de manière systématique sans hallucination.",
  arbitrator: "Tu es un arbitre neutre. Ton rôle est de confronter les différentes synthèses, d'identifier les contradictions, de peser les sources et de proposer une conclusion équilibrée et justifiée.",
  judge: "Tu es le Juge final. Ton rôle est d'évaluer rigoureusement la qualité, la conformité et la sécurité de la réponse ou du document. Tu dois valider ou rejeter selon des critères stricts."
};

interface ProvidersDashboardProps {
  isActive: boolean;
}

export function ProvidersDashboard({ isActive }: ProvidersDashboardProps) {
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingProvider, setEditingProvider] = useState<ProviderConfig | null>(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{status: 'success' | 'error', message: string} | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [projectId, setProjectId] = useState('demo');
  const [testingMcp, setTestingMcp] = useState(false);
  const [mcpTestResult, setMcpTestResult] = useState<any>(null);
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({});
  const [availableMcpServers, setAvailableMcpServers] = useState<string[]>([]);
  const [healthStats, setHealthStats] = useState<Record<string, any>>({});

  useEffect(() => {
    if (!isActive) return;
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/providers/health');
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'success') {
            setHealthStats(data.health);
          }
        }
      } catch (e) {
        // silencieux
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [isActive]);

  useEffect(() => {
    const input = document.getElementById('projectIdInput') as HTMLInputElement;
    if (input && input.value) {
      setProjectId(input.value);
    }
  }, []);

  useEffect(() => {
    if (isActive) {
      fetchProviders();
    }
  }, [isActive, projectId]);

  useEffect(() => {
    if (editingProvider && !availableModels[editingProvider.kind]) {
      const fetchModelsForKind = async (kind: string) => {
        try {
          const res = await fetch(`http://localhost:8000/models/${kind}`);
          if (res.ok) {
            const data = await res.json();
            if (data.status === 'success') {
              setAvailableModels(prev => ({ ...prev, [kind]: data.models }));
            }
          }
        } catch (e) {
          console.error("Failed to fetch models for", kind);
        }
      };
      fetchModelsForKind(editingProvider.kind);
    }
    
    // Fetch global MCP servers
    const fetchMcpServers = async () => {
      try {
        const res = await fetch(`http://localhost:8000/mcp/servers`);
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'success') {
            setAvailableMcpServers(data.servers || []);
          }
        }
      } catch (e) {
        console.error("Failed to fetch MCP servers");
      }
    };
    fetchMcpServers();
  }, [editingProvider, availableModels]);

  const fetchProviders = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}/config`);
      if (!response.ok) throw new Error(`HTTP Erreur ${response.status} - Le backend n'a peut-être pas rechargé`);
      const data = await response.json();
      
      const rawProviders = data.config?.llm?.providers || [];
      // Sort by priority (lower number = higher priority)
      const sortedProviders = rawProviders.sort((a: ProviderConfig, b: ProviderConfig) => (a.priority || 10) - (b.priority || 10));
      setProviders(sortedProviders);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (!editingProvider) return;
    const newRole = e.target.value;
    const newRules = (!editingProvider.rules || editingProvider.rules.trim() === '' || Object.values(ROLE_PROMPTS).includes(editingProvider.rules.trim())) 
      ? ROLE_PROMPTS[newRole] || ''
      : editingProvider.rules;
      
    setEditingProvider({
      ...editingProvider,
      role: newRole,
      rules: newRules
    });
  };

  const handleTestConnection = async (provider: ProviderConfig) => {
    setTesting(true);
    setTestResult(null);
    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}/providers/${provider.name}/test`, {
        method: 'POST'
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Erreur lors du test de connexion');
      setTestResult({ status: data.status, message: data.message + (data.response ? ` : "${data.response}"` : "") });
    } catch (err: any) {
      setTestResult({ status: 'error', message: err.message });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async (provider: ProviderConfig) => {
    setSaving(true);
    setError(null);
    try {
      // Find index for the patch route
      const index = providers.findIndex(p => p.name === provider.name);
      if (index === -1) throw new Error("Provider introuvable dans la liste");

      const response = await fetch(`http://localhost:8000/projects/${projectId}/config`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          key: `llm.providers.${index}`,
          value: provider
        }),
      });
      if (!response.ok) {
        // Fallback to the specific provider route if the PATCH fails (e.g. if the API was updated after all)
        const putResponse = await fetch(`http://localhost:8000/projects/${projectId}/providers/${provider.name}`, {
           method: 'PUT',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify(provider),
        });
        if (!putResponse.ok) throw new Error(`Erreur lors de la sauvegarde: HTTP ${putResponse.status}`);
      }
      await fetchProviders();
      setEditingProvider(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleEnabled = async (provider: ProviderConfig) => {
    const updated = { ...provider, enabled: !provider.enabled };
    await handleSave(updated);
  };

  if (!isActive) return null;

  return (
    <div className="flex flex-col h-full relative z-10">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Cpu className="h-6 w-6 mr-3 text-emerald-400" />
          Les Providers (Flotte LLM)
        </h2>
        <div className="flex space-x-2">
          <button 
            onClick={async () => {
              setTestingMcp(true);
              setMcpTestResult(null);
              try {
                const response = await fetch(`http://localhost:8000/mcp/test`, { method: 'POST' });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'Erreur lors du test MCP');
                setMcpTestResult(data);
              } catch (err: any) {
                setMcpTestResult({ status: 'error', message: err.message });
              } finally {
                setTestingMcp(false);
              }
            }}
            disabled={testingMcp}
            className="px-3 py-1.5 bg-blue-900/40 hover:bg-blue-800/60 text-blue-300 rounded-md text-sm transition-colors flex items-center border border-blue-700/50"
          >
            {testingMcp ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Activity className="h-4 w-4 mr-2" />}
            Tester MCP (DB)
          </button>
          <button 
            onClick={fetchProviders}
            className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-md text-sm transition-colors"
          >
            Rafraîchir
          </button>
        </div>
      </div>
      
      {mcpTestResult && (
        <div className={`mb-4 p-4 rounded-lg text-sm border ${mcpTestResult.status === 'success' ? 'bg-emerald-900/20 border-emerald-500/30 text-emerald-300' : 'bg-red-900/20 border-red-500/30 text-red-300'}`}>
          <div className="flex justify-between items-start mb-2">
            <h4 className="font-bold">Résultat du test des serveurs MCP</h4>
            <button onClick={() => setMcpTestResult(null)}><X className="h-4 w-4 opacity-50 hover:opacity-100" /></button>
          </div>
          {mcpTestResult.message && <p className="mb-2">{mcpTestResult.message}</p>}
          {mcpTestResult.servers && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 mt-2">
              {Object.entries(mcpTestResult.servers).map(([server, res]: [string, any]) => (
                <div key={server} className="bg-[#0b0f19] p-2 rounded border border-gray-800 flex items-center justify-between">
                  <span className="font-mono text-gray-300">{server}</span>
                  {res.status === 'ok' ? (
                    <span className="text-emerald-400 text-xs flex items-center bg-emerald-900/30 px-2 py-0.5 rounded"><Check className="h-3 w-3 mr-1"/> En ligne ({res.tools_count} outils)</span>
                  ) : (
                    <span className="text-red-400 text-xs truncate max-w-[150px]" title={res.message}>Erreur</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <p className="text-sm text-gray-400 mb-6 bg-gray-800/30 p-2 rounded border border-gray-700/50">
        Cliquez sur <strong>Configurer</strong> pour ajuster les paramètres de chaque modèle (Rôle, API, MCP, Prompt Système...).
      </p>

      {error && (
        <div className="mb-4 p-4 bg-red-900/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading && !providers.length ? (
        <div className="flex-1 flex flex-col items-center justify-center space-y-4">
          <Loader2 className="h-10 w-10 text-emerald-500 animate-spin" />
          <p className="text-emerald-400 font-medium animate-pulse">Chargement de la flotte...</p>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto pr-2 space-y-4">
          {providers.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-48 bg-gray-900/30 border border-gray-800 rounded-xl">
              <Cpu className="h-10 w-10 text-gray-600 mb-2" />
              <p className="text-gray-400 font-medium">Aucun LLM configuré dans ce projet.</p>
            </div>
          )}
          {providers.map(provider => (
            <div key={provider.name} className="bg-[#111827] border border-gray-800 rounded-xl overflow-hidden transition-all hover:border-emerald-900/50">
              {editingProvider?.name === provider.name ? (
                // EDIT MODE
                <div className="p-5">
                  <div className="flex justify-between items-center border-b border-gray-800 pb-4 mb-4">
                    <h3 className="text-lg font-bold text-emerald-400 flex items-center">
                      <Server className="h-5 w-5 mr-2" />
                      Édition: {provider.name}
                    </h3>
                    <button onClick={() => setEditingProvider(null)} className="text-gray-400 hover:text-white">
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Colonne 1: Connexion */}
                    <div className="space-y-4">
                      <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Connexion</h4>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">Modèle</label>
                        <div className="flex gap-2">
                          <select 
                            value={availableModels[editingProvider.kind]?.includes(editingProvider.model) ? editingProvider.model : ""}
                            onChange={(e) => {
                              if (e.target.value) {
                                setEditingProvider({...editingProvider, model: e.target.value});
                              }
                            }}
                            className="w-1/2 bg-[#0b0f19] border border-gray-700 rounded-lg px-2 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                            title="Sélection rapide d'un modèle connu"
                          >
                            <option value="">-- Saisie manuelle --</option>
                            {availableModels[editingProvider.kind]?.map(m => (
                              <option key={m} value={m}>{m}</option>
                            ))}
                          </select>
                          <input 
                            type="text"
                            value={editingProvider.model} 
                            onChange={e => setEditingProvider({...editingProvider, model: e.target.value})}
                            className="w-1/2 bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                            placeholder="Saisie libre du modèle..."
                          />
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">Base URL</label>
                        <input 
                          type="text" 
                          value={editingProvider.base_url || ''} 
                          onChange={e => setEditingProvider({...editingProvider, base_url: e.target.value})}
                          className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">Variable d'env. Clé API</label>
                        <input 
                          type="text" 
                          value={editingProvider.api_key_env || ''} 
                          onChange={e => setEditingProvider({...editingProvider, api_key_env: e.target.value})}
                          className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                        />
                      </div>
                      
                      <div className="flex space-x-4">
                        <div className="flex-1">
                          <label className="block text-xs font-medium text-gray-500 mb-1">Timeout (s)</label>
                          <input 
                            type="number" 
                            value={editingProvider.timeout_seconds} 
                            onChange={e => setEditingProvider({...editingProvider, timeout_seconds: parseInt(e.target.value) || 60})}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                          />
                        </div>
                        <div className="flex-1">
                          <label className="block text-xs font-medium text-gray-500 mb-1">Max Retries</label>
                          <input 
                            type="number" 
                            value={editingProvider.max_retries} 
                            onChange={e => setEditingProvider({...editingProvider, max_retries: parseInt(e.target.value) || 0})}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                          />
                        </div>
                      </div>
                    </div>
                    
                    {/* Colonne 2: Comportement */}
                    <div className="space-y-4">
                      <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Comportement & Rôle</h4>
                      
                      <div className="flex space-x-4">
                        <div className="flex-1">
                          <label className="block text-xs font-medium text-gray-500 mb-1">Rôle</label>
                          <select 
                            value={editingProvider.role} 
                            onChange={handleRoleChange}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                          >
                            <option value="general">Général (Générique)</option>
                            <option value="expert">Expert (Analytique)</option>
                            <option value="arbitrator">Arbitre (Synthèse)</option>
                            <option value="judge">Juge (Validation finale)</option>
                          </select>
                        </div>
                        <div className="flex-1">
                          <label className="block text-xs font-medium text-gray-500 mb-1">Priorité (Rotator)</label>
                          <input 
                            type="number" 
                            value={editingProvider.priority} 
                            onChange={e => setEditingProvider({...editingProvider, priority: parseInt(e.target.value) || 10})}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                          />
                        </div>
                      </div>

                      <div className="flex flex-col space-y-3 p-3 bg-emerald-900/10 border border-emerald-500/20 rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-300">Tools MCP (Agents)</span>
                          <button 
                            onClick={() => setEditingProvider({...editingProvider, mcp_enabled: !editingProvider.mcp_enabled})}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${editingProvider.mcp_enabled ? 'bg-emerald-500' : 'bg-gray-700'}`}
                          >
                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${editingProvider.mcp_enabled ? 'translate-x-6' : 'translate-x-1'}`} />
                          </button>
                        </div>
                        {editingProvider.mcp_enabled && (
                          <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2 mt-4">
                              Accès aux Serveurs MCP (Panneau de Contrôle)
                            </label>
                            <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
                              {availableMcpServers.map(serverName => {
                                const rule = (editingProvider.mcp_servers || []).find((s: any) => 
                                  typeof s === 'string' ? s === serverName : s.server_name === serverName
                                ) || { server_name: serverName, access_level: 'disabled', rules: '' };
                                
                                const normalizedRule = typeof rule === 'string' 
                                  ? { server_name: rule, access_level: 'authorized' as const, rules: '' }
                                  : rule;
                                  
                                return (
                                  <div key={serverName} className="p-3 border-b border-gray-700 last:border-b-0">
                                    <div className="flex items-center justify-between">
                                      <div className="font-medium text-gray-300 flex items-center">
                                        <Server className="h-4 w-4 mr-2 text-indigo-400" />
                                        {serverName}
                                      </div>
                                      <select
                                        className={`bg-gray-900 border text-sm rounded-md px-2 py-1 outline-none ${
                                          normalizedRule.access_level === 'authorized' ? 'border-emerald-500/50 text-emerald-400' : 
                                          normalizedRule.access_level === 'limited' ? 'border-amber-500/50 text-amber-400' : 
                                          'border-gray-600 text-gray-500'
                                        }`}
                                        value={normalizedRule.access_level}
                                        onChange={(e) => {
                                          const newLevel = e.target.value as 'authorized' | 'limited' | 'disabled';
                                          let newServers = [...(editingProvider.mcp_servers || []).map((s: any) => typeof s === 'string' ? { server_name: s, access_level: 'authorized' as const, rules: '' } : s)];
                                          
                                          const existingIdx = newServers.findIndex(s => s.server_name === serverName);
                                          if (newLevel === 'disabled') {
                                            if (existingIdx >= 0) newServers.splice(existingIdx, 1);
                                          } else {
                                            if (existingIdx >= 0) {
                                              newServers[existingIdx].access_level = newLevel;
                                            } else {
                                              newServers.push({ server_name: serverName, access_level: newLevel, rules: '' });
                                            }
                                          }
                                          setEditingProvider({...editingProvider, mcp_servers: newServers as any});
                                        }}
                                      >
                                        <option value="disabled">Désactivé</option>
                                        <option value="authorized">Autorisé (Total)</option>
                                        <option value="limited">Limité (Avec règles)</option>
                                      </select>
                                    </div>
                                    
                                    {normalizedRule.access_level === 'limited' && (
                                      <div className="mt-2 ml-6">
                                        <input
                                          type="text"
                                          placeholder="Règles (ex: 'Uniquement pour lire, interdiction d'écrire')"
                                          className="w-full bg-gray-900/80 border border-amber-900/50 rounded p-1.5 text-xs text-amber-200/80 placeholder-amber-900/50 focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 outline-none"
                                          value={normalizedRule.rules}
                                          onChange={(e) => {
                                            let newServers = [...(editingProvider.mcp_servers || []).map((s: any) => typeof s === 'string' ? { server_name: s, access_level: 'authorized' as const, rules: '' } : s)];
                                            const existingIdx = newServers.findIndex(s => s.server_name === serverName);
                                            if (existingIdx >= 0) {
                                              newServers[existingIdx].rules = e.target.value;
                                              setEditingProvider({...editingProvider, mcp_servers: newServers as any});
                                            }
                                          }}
                                        />
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                              {availableMcpServers.length === 0 && (
                                <div className="p-3 text-sm text-gray-500 italic">
                                  Aucun serveur MCP global trouvé.
                                </div>
                              )}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              Utilisez "Limité" pour ajouter des contraintes spécifiques à ce modèle lors de l'utilisation des outils de ce serveur.
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">Responsabilités (Description)</label>
                        <input 
                          type="text" 
                          value={editingProvider.responsibilities || ''} 
                          onChange={e => setEditingProvider({...editingProvider, responsibilities: e.target.value})}
                          placeholder="Ex: Analyse les documents complexes..."
                          className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                        />
                      </div>
                      
                      <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-gray-800">
                        <div>
                          <label className="block text-[10px] font-medium text-gray-500 mb-1">Failures av. Quarantaine</label>
                          <input 
                            type="number" 
                            min="1"
                            value={editingProvider.circuit_breaker_failures ?? 3} 
                            onChange={e => setEditingProvider({...editingProvider, circuit_breaker_failures: parseInt(e.target.value) || 3})}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-2 py-1 text-white text-xs focus:ring-1 focus:ring-amber-500 outline-none"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-medium text-gray-500 mb-1">Durée Quarantaine (s)</label>
                          <input 
                            type="number" 
                            min="1"
                            value={editingProvider.circuit_breaker_cooldown_seconds ?? 120} 
                            onChange={e => setEditingProvider({...editingProvider, circuit_breaker_cooldown_seconds: parseInt(e.target.value) || 120})}
                            className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-2 py-1 text-white text-xs focus:ring-1 focus:ring-amber-500 outline-none"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Ligne complète: Règles (Prompt) */}
                  <div className="mt-4">
                    <label className="block text-xs font-medium text-gray-500 mb-1">Règles Spécifiques (System Prompt additionnel)</label>
                    <textarea 
                      value={editingProvider.rules || ''} 
                      onChange={e => setEditingProvider({...editingProvider, rules: e.target.value})}
                      className="w-full min-h-[100px] bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-2 text-white font-mono text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                      placeholder="Tu dois toujours répondre en français, être concis..."
                    />
                  </div>

                  {testResult && (
                    <div className={`mt-4 p-3 rounded text-sm ${testResult.status === 'success' ? 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/30' : 'bg-red-900/30 text-red-400 border border-red-500/30'}`}>
                      {testResult.message}
                    </div>
                  )}

                  <div className="mt-6 flex justify-between items-center">
                    <button 
                      onClick={() => handleTestConnection(editingProvider)}
                      disabled={testing}
                      className="px-4 py-2 bg-blue-900/40 hover:bg-blue-800/60 text-blue-300 border border-blue-700/50 rounded-lg text-sm font-medium transition-colors flex items-center"
                    >
                      {testing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Activity className="h-4 w-4 mr-2" />}
                      Tester la connexion
                    </button>
                    <div className="flex space-x-3">
                      <button 
                        onClick={() => { setEditingProvider(null); setTestResult(null); }}
                        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm font-medium transition-colors"
                      >
                        Annuler
                      </button>
                      <button 
                        onClick={() => handleSave(editingProvider)}
                        disabled={saving}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
                      >
                        {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                        Sauvegarder
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                // VIEW MODE
                <div className="p-5 flex items-start justify-between relative overflow-hidden">
                  {/* Health Background Highlight */}
                  {!provider.enabled ? (
                     <div className="absolute top-0 left-0 w-1 h-full bg-gray-600"></div>
                  ) : healthStats[provider.name]?.status === 'quarantined' ? (
                     <div className="absolute top-0 left-0 w-1 h-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]"></div>
                  ) : healthStats[provider.name]?.status === 'degraded' ? (
                     <div className="absolute top-0 left-0 w-1 h-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]"></div>
                  ) : (
                     <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
                  )}
                  
                  <div className="flex items-start space-x-4 pl-2">
                    <div>
                      <div className="flex items-center space-x-3 mb-1">
                        <h3 className="text-lg font-bold text-white">{provider.name}</h3>
                        <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded border border-gray-700 uppercase tracking-wider font-mono">
                          {provider.kind}
                        </span>
                        {provider.role && provider.role !== 'general' && (
                          <span className={`text-xs px-2 py-0.5 rounded border uppercase tracking-wider font-bold
                            ${provider.role === 'expert' ? 'bg-blue-900/50 text-blue-300 border-blue-500/50' : ''}
                            ${provider.role === 'arbitrator' ? 'bg-purple-900/50 text-purple-300 border-purple-500/50' : ''}
                            ${provider.role === 'judge' ? 'bg-fuchsia-900/50 text-fuchsia-300 border-fuchsia-500/50' : ''}
                          `}>
                            {provider.role}
                          </span>
                        )}
                        {provider.mcp_enabled && (
                          <span className="text-xs bg-emerald-900/50 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/50 flex items-center">
                            <Cpu className="h-3 w-3 mr-1" /> MCP
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-400 mb-3">
                        <span><strong className="text-gray-300">Modèle:</strong> {provider.model}</span>
                        <span><strong className="text-gray-300">Prio:</strong> {provider.priority}</span>
                      </div>
                      {provider.responsibilities && (
                        <p className="text-sm text-gray-400 italic mt-2 border-l-2 border-gray-700 pl-3 py-1">
                          {provider.responsibilities}
                        </p>
                      )}
                      
                      {provider.enabled && healthStats[provider.name] && (
                        <div className={`mt-3 text-xs px-3 py-1.5 rounded flex items-center border ${
                            healthStats[provider.name].status === 'quarantined' 
                              ? 'bg-red-900/20 text-red-300 border-red-500/30' 
                              : healthStats[provider.name].status === 'degraded'
                                ? 'bg-amber-900/20 text-amber-300 border-amber-500/30'
                                : 'bg-emerald-900/10 text-emerald-300 border-emerald-500/10'
                        }`}>
                          <Activity className="h-3 w-3 mr-2" />
                          <div className="flex space-x-3">
                            <span>Requêtes: <b>{healthStats[provider.name].success_count}</b></span>
                            {healthStats[provider.name].error_count > 0 && (
                              <span className="text-red-400">Erreurs: <b>{healthStats[provider.name].error_count}</b></span>
                            )}
                            {healthStats[provider.name].status === 'quarantined' && (
                              <span className="font-bold text-red-500">QUARANTAINE ({healthStats[provider.name].cooldown_remaining}s) - {healthStats[provider.name].last_error}</span>
                            )}
                            {healthStats[provider.name].status === 'degraded' && (
                              <span className="font-bold text-amber-500">DÉGRADÉ ({healthStats[provider.name].consecutive_errors}/{provider.circuit_breaker_failures || 3} err)</span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-col space-y-2 items-end">
                    <button 
                      onClick={() => toggleEnabled(provider)}
                      disabled={saving}
                      className={`px-3 py-1.5 rounded text-xs font-bold border transition-colors flex items-center
                        ${provider.enabled 
                          ? 'bg-red-900/20 text-red-400 border-red-500/30 hover:bg-red-900/40' 
                          : 'bg-emerald-900/20 text-emerald-400 border-emerald-500/30 hover:bg-emerald-900/40'
                        }
                      `}
                    >
                      {provider.enabled ? 'Désactiver' : 'Activer'}
                    </button>
                    
                    <button 
                      onClick={() => setEditingProvider(provider)}
                      className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded text-xs transition-colors flex items-center"
                    >
                      <Edit className="h-3 w-3 mr-1" /> Configurer
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
