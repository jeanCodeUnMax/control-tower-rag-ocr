import { useState } from 'react';
import { Timer, Play, Loader2, AlertCircle, Cpu, CheckCircle2 } from 'lucide-react';

export function BenchmarkDashboard({ isActive }: { isActive: boolean }) {
  const [prompt, setPrompt] = useState('Quelle est la capitale de la France en un seul mot ?');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runBenchmark = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const projectId = (document.getElementById('projectIdInput') as HTMLInputElement)?.value || 'demo';
      const response = await fetch(`http://localhost:8000/projects/${projectId}/benchmark`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt, system_prompt: '' })
      });
      
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors du benchmark');
      }
      
      if (data.status === 'success') {
        setResults(data.results);
      } else {
        throw new Error(data.message || 'Erreur inconnue');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isActive) return null;

  return (
    <div className="flex flex-col h-full relative z-10 overflow-y-auto pr-2">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Timer className="h-6 w-6 mr-3 text-amber-400" />
          Benchmarker Multi-Modèles
        </h2>
        <span className="text-sm text-gray-500">Comparez la flotte LLM</span>
      </div>

      <div className="bg-[#111827] border border-gray-800 rounded-xl p-5 mb-6 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.8)]"></div>
        <div className="pl-2">
          <label className="block text-sm font-medium text-gray-300 mb-2">Prompt de test unitaire</label>
          <textarea 
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full min-h-[80px] bg-[#0b0f19] border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none mb-4"
            placeholder="Posez une question de test..."
          />
          <div className="flex justify-between items-center">
            <p className="text-xs text-gray-500 italic">
              Note: Le test s'exécutera séquentiellement sur tous les LLM activés dans "Les Providers".
            </p>
            <button 
              onClick={runBenchmark}
              disabled={loading || !prompt.trim()}
              className="px-6 py-2.5 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm font-bold transition-colors flex items-center shadow-lg shadow-amber-900/20"
            >
              {loading ? <Loader2 className="h-5 w-5 mr-2 animate-spin" /> : <Play className="h-5 w-5 mr-2" />}
              {loading ? 'Test en cours...' : 'Lancer le Benchmark'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-500/30 rounded-lg text-red-400 text-sm flex items-center">
          <AlertCircle className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {results && (
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-gray-200 mb-4 border-b border-gray-800 pb-2">Résultats ({results.length} LLMs testés)</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {results.map((res, i) => (
              <div key={i} className={`bg-[#0b0f19] border ${res.error ? 'border-red-900/50' : 'border-gray-800'} rounded-lg p-4 relative`}>
                <div className="flex justify-between items-start mb-3 border-b border-gray-800/50 pb-2">
                  <div className="flex items-center space-x-2">
                    <Cpu className={`h-4 w-4 ${res.error ? 'text-red-500' : 'text-emerald-500'}`} />
                    <span className="font-bold text-white">{res.name}</span>
                    <span className="text-[10px] bg-gray-800 text-gray-400 px-1.5 py-0.5 rounded uppercase">{res.kind}</span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className={`text-xs font-mono font-bold px-2 py-1 rounded ${res.error ? 'bg-red-900/30 text-red-400' : 'bg-amber-900/20 text-amber-400'}`}>
                      {res.duration_s}s
                    </span>
                  </div>
                </div>
                
                <div className="mb-2">
                  <span className="text-xs text-gray-500">Modèle configuré: </span>
                  <span className="text-xs text-gray-300 font-mono">{res.model}</span>
                </div>
                
                <div className="mt-3 bg-gray-900/50 rounded p-3 text-sm min-h-[60px]">
                  {res.error ? (
                    <div className="text-red-400 flex items-start">
                      <AlertCircle className="h-4 w-4 mr-2 mt-0.5 shrink-0" />
                      <span className="break-all">{res.error}</span>
                    </div>
                  ) : (
                    <div className="text-gray-300 whitespace-pre-wrap">
                      {res.response}
                    </div>
                  )}
                </div>
                
                {!res.error && (
                  <div className="absolute top-4 right-16">
                     <CheckCircle2 className="h-4 w-4 text-emerald-500/50" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
