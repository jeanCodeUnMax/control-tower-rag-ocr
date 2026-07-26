import { useState, useEffect } from 'react'
import { Activity, Database, Swords, Server, Shield, BrainCircuit, Loader2, FileText, Layers, Cpu, Settings, Edit, Save, X, Check, XCircle, Timer } from 'lucide-react'
import { ProvidersDashboard } from './ProvidersDashboard'
import { BenchmarkDashboard } from './BenchmarkDashboard'

function App() {
  const [activeTab, setActiveTab] = useState('arena')
  const [question, setQuestion] = useState('')
  const [paradigm, setParadigm] = useState('executive')
  const [webSearch, setWebSearch] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleSynthesize = async () => {
    if (!question.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const projectId = (document.getElementById('projectIdInput') as HTMLInputElement)?.value || 'demo'
      const response = await fetch('http://localhost:8000/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          question: question,
          top_k: 5,
          use_web_search: webSearch,
          paradigm: paradigm
        })
      })
      const data = await response.json()
      if (!response.ok) {
        setResult({ error: data.detail || `Erreur serveur: ${response.status}` })
      } else {
        setResult(data)
      }
    } catch (error) {
      console.error(error)
      setResult({ error: "Erreur lors de la communication avec l'API" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#0b0f19] text-gray-300 font-sans">
      {/* Header */}
      <header className="border-b border-cyan-900/50 bg-[#111827]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <BrainCircuit className="h-8 w-8 text-cyan-400" />
            <h1 className="text-xl font-bold text-white tracking-wide">
              CONTROL TOWER <span className="text-cyan-500 font-light">AGI</span>
            </h1>
          </div>
          <div className="flex space-x-2">
            <span className="inline-flex items-center rounded-full bg-emerald-400/10 px-3 py-1 text-xs font-medium text-emerald-400 ring-1 ring-inset ring-emerald-400/20">
              <Server className="h-3 w-3 mr-1" />
              API Online
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex gap-8">
        
        {/* Sidebar Nav */}
        <nav className="w-64 shrink-0 space-y-2">
          <button 
            onClick={() => setActiveTab('ingestion')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'ingestion' ? 'bg-cyan-900/30 text-cyan-400 border border-cyan-500/30' : 'hover:bg-gray-800 text-gray-400'
          }`}>
            <Activity className="h-5 w-5" />
            <span className="font-medium">1. Le Radar</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('observatory')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'observatory' ? 'bg-indigo-900/30 text-indigo-400 border border-indigo-500/30' : 'hover:bg-gray-800 text-gray-400'
          }`}>
            <Database className="h-5 w-5" />
            <span className="font-medium">2. Observatoire Vectoriel</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('arena')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'arena' ? 'bg-fuchsia-900/30 text-fuchsia-400 border border-fuchsia-500/30' : 'hover:bg-gray-800 text-gray-400'
          }`}>
            <Swords className="h-5 w-5" />
            <span className="font-medium">3. L'Arène (Synthèse)</span>
          </button>

          <button 
            onClick={() => setActiveTab('quarantine')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'quarantine' ? 'bg-orange-900/30 text-orange-400 border border-orange-500/30' : 'hover:bg-gray-800 text-gray-400'
          }`}>
            <Shield className="h-5 w-5" />
            <span className="font-medium">4. Tour de Contrôle</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('providers')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'providers' ? 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/30' : 'hover:bg-gray-800 text-gray-400'
          }`}>
            <Cpu className="h-5 w-5" />
            <span className="font-medium">5. Les Providers</span>
          </button>
          
          <button 
            onClick={() => setActiveTab('benchmark')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
            activeTab === 'benchmark' ? 'bg-amber-900/30 text-amber-400 border border-amber-500/30' : 'hover:bg-gray-800 text-gray-400'
          }`}>
            <Timer className="h-5 w-5" />
            <span className="font-medium">6. Le Benchmarker</span>
          </button>
        </nav>

        {/* Dynamic Area */}
        <div className="flex-1 flex flex-col bg-[#111827]/50 rounded-2xl border border-gray-800 shadow-2xl p-6 relative overflow-hidden h-[calc(100vh-10rem)]">
          {/* Ambient Glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cyan-500/10 blur-[120px] rounded-full pointer-events-none" />

          <div className={activeTab === 'arena' ? 'flex flex-col h-full relative z-10' : 'hidden'}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white flex items-center">
                  <Swords className="h-6 w-6 mr-3 text-fuchsia-400" />
                  L'Arène Cognitive
                </h2>
                <span className="text-sm text-gray-500">Testez le RAG et les Paradigmes</span>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-400">Project ID</label>
                  <input 
                    type="text" 
                    defaultValue="demo"
                    id="projectIdInput"
                    className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent outline-none"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-400">Paradigme Cognitif</label>
                  <select 
                    value={paradigm}
                    onChange={(e) => setParadigm(e.target.value)}
                    className="w-full bg-[#0b0f19] border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent outline-none"
                  >
                    <option value="executive">Executive (Direct, Concis)</option>
                    <option value="socratic">Socratic (Questions)</option>
                    <option value="analogy">Analogy (Comparaisons simples)</option>
                    <option value="discovery">Discovery (Créatif, Exploratoire)</option>
                    <option value="json_schema">JSON Schema (Données structurées)</option>
                    <option value="pseudocode">Pseudo-code (Algorithme)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center space-x-3 mb-6 p-4 bg-blue-900/10 border border-blue-500/20 rounded-lg">
                <Shield className="h-5 w-5 text-blue-400" />
                <span className="text-sm text-blue-200">Recherche Web (DuckDuckGo)</span>
                <button 
                  onClick={() => setWebSearch(!webSearch)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${webSearch ? 'bg-blue-500' : 'bg-gray-700'}`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${webSearch ? 'translate-x-6' : 'translate-x-1'}`} />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto mb-6 bg-[#0b0f19] border border-gray-800 rounded-lg p-6">
                {loading ? (
                  <div className="h-full flex flex-col items-center justify-center space-y-4">
                    <Loader2 className="h-10 w-10 text-fuchsia-500 animate-spin" />
                    <p className="text-fuchsia-400 font-medium animate-pulse">Les LLMs débattent... veuillez patienter</p>
                  </div>
                ) : result ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-gray-800 pb-4">
                      <h3 className="text-lg font-bold text-white">Résultat du Consensus</h3>
                      {result.synthesizer && (
                        <span className="text-xs bg-fuchsia-900/50 text-fuchsia-300 px-3 py-1 rounded-full border border-fuchsia-500/30">
                          Juge Final : {result.synthesizer}
                        </span>
                      )}
                    </div>
                    {result.error ? (
                      <div className="text-red-400 bg-red-900/10 p-4 rounded-lg border border-red-500/20 whitespace-pre-wrap">
                        {result.error}
                      </div>
                    ) : (
                      <div className="prose prose-invert prose-cyan max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-gray-300 leading-relaxed bg-transparent p-0">
                          {result.synthesis}
                        </pre>
                        
                        {/* Affichage des sources vectorielles */}
                        {result.rag_sources && result.rag_sources.length > 0 && (
                          <div className="mt-6 pt-4 border-t border-gray-800">
                            <h4 className="text-sm font-semibold text-cyan-400 mb-3 flex items-center">
                              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                              Vecteurs extraits de la base (Qdrant/Zvec)
                            </h4>
                            <div className="space-y-2">
                              {result.rag_sources.map((src: any, idx: number) => (
                                <div key={idx} className="bg-gray-800/50 p-3 rounded text-xs border border-gray-700">
                                  <div className="flex justify-between text-gray-400 mb-1">
                                    <span className="font-mono text-cyan-500/70">{src.document_id}</span>
                                    <span className="text-yellow-500/70">Score: {src.score.toFixed(2)}</span>
                                  </div>
                                  <p className="text-gray-300 italic">"{src.text_snippet}..."</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Action buttons */}
                        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t border-gray-800">
                          <button 
                            onClick={() => {
                              navigator.clipboard.writeText(result.synthesis)
                            }}
                            className="flex items-center px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm rounded-md transition-colors"
                            title="Copier le texte"
                          >
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                            Copier
                          </button>
                          <button 
                            onClick={() => {
                              const blob = new Blob([result.synthesis], { type: 'text/markdown' })
                              const url = URL.createObjectURL(blob)
                              const a = document.createElement('a')
                              a.href = url
                              a.download = `synthese_${new Date().toISOString().replace(/[:.]/g, '-')}.md`
                              a.click()
                              URL.revokeObjectURL(url)
                            }}
                            className="flex items-center px-3 py-1.5 bg-fuchsia-900/50 hover:bg-fuchsia-800/50 text-fuchsia-300 border border-fuchsia-500/30 text-sm rounded-md transition-colors"
                            title="Télécharger en Markdown"
                          >
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                            Enregistrer sous
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-600 italic">
                    Entrez une question et lancez le consensus pour voir le résultat.
                  </div>
                )}
              </div>

              <div className="relative flex items-center">
                <input 
                  type="text" 
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSynthesize()}
                  placeholder="Posez votre question à la Tour de Contrôle..."
                  className="w-full bg-[#0b0f19] border border-gray-700 rounded-xl pl-6 pr-32 py-4 text-lg text-white placeholder-gray-600 focus:ring-2 focus:ring-fuchsia-500 focus:border-transparent outline-none"
                />
                <button 
                  onClick={handleSynthesize}
                  disabled={loading || !question.trim()}
                  className="absolute right-2 px-6 py-2 bg-gradient-to-r from-fuchsia-600 to-indigo-600 hover:from-fuchsia-500 hover:to-indigo-500 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Lancer
                </button>
              </div>
            </div>

          <div className={activeTab === 'ingestion' ? 'h-full' : 'hidden'}>
            <IngestionDashboard />
          </div>
          
          <div className={activeTab === 'observatory' ? 'h-full' : 'hidden'}>
            <VectorObservatory isActive={activeTab === 'observatory'} />
          </div>

          <div className={activeTab === 'quarantine' ? 'h-full' : 'hidden'}>
            <QuarantineDashboard isActive={activeTab === 'quarantine'} />
          </div>

          <div className={activeTab === 'providers' ? 'h-full' : 'hidden'}>
            <ProvidersDashboard isActive={activeTab === 'providers'} />
          </div>
          <div className={activeTab === 'benchmark' ? 'h-full' : 'hidden'}>
            <BenchmarkDashboard isActive={activeTab === 'benchmark'} />
          </div>

        </div>
      </main>
    </div>
  )
}

function VectorObservatory({ isActive }: { isActive?: boolean }) {
  const [projectId, setProjectId] = useState('demo')
  const [stats, setStats] = useState<any>(null)
  const [documents, setDocuments] = useState<string[]>([])
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const [docData, setDocData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [isConsolidating, setIsConsolidating] = useState(false)

  const handleConsolidate = async () => {
    if (!projectId || isConsolidating) return
    setIsConsolidating(true)
    try {
      const res = await fetch(`http://localhost:8000/projects/${projectId}/consolidate`, {
        method: 'POST'
      })
      if (res.ok) {
        await fetchProjectData()
      }
    } catch (err) {
      console.error("Erreur de consolidation:", err)
    } finally {
      setIsConsolidating(false)
    }
  }

  const fetchProjectData = async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const [inspectRes, docsRes] = await Promise.all([
        fetch(`http://localhost:8000/projects/${projectId}/inspect`),
        fetch(`http://localhost:8000/projects/${projectId}/documents`)
      ])
      
      if (inspectRes.ok) {
        const inspectData = await inspectRes.json()
        setStats(inspectData.store)
      }
      
      if (docsRes.ok) {
        const docsData = await docsRes.json()
        setDocuments(docsData.documents)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const fetchDocumentData = async (docId: string) => {
    setSelectedDoc(docId)
    try {
      const res = await fetch(`http://localhost:8000/projects/${projectId}/documents/${docId}`)
      if (res.ok) {
        const data = await res.json()
        setDocData(data)
      }
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    if (isActive !== false) {
      fetchProjectData()
    }
  }, [projectId, isActive])

  const openDocumentFolder = async (docId: string) => {
    try {
      await fetch(`http://localhost:8000/projects/${projectId}/documents/${docId}/open`, {
        method: 'POST'
      })
    } catch (err) {
      console.error("Erreur ouverture dossier:", err)
    }
  }

  return (
    <div className="flex flex-col h-full relative z-10 p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Database className="h-6 w-6 mr-3 text-fuchsia-400" />
          Observatoire Vectoriel
        </h2>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Projet:</label>
          <input 
            type="text" 
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-1 text-white text-sm focus:ring-1 focus:ring-fuchsia-500 outline-none"
          />
          <button onClick={fetchProjectData} className="p-1.5 bg-gray-800 hover:bg-gray-700 rounded-md text-gray-300">
            <Activity className="h-4 w-4" />
          </button>
          <button 
            onClick={handleConsolidate} 
            disabled={isConsolidating}
            className="ml-4 px-3 py-1.5 bg-fuchsia-600/20 hover:bg-fuchsia-600/30 text-fuchsia-400 border border-fuchsia-500/30 rounded-md text-sm font-medium transition-colors flex items-center"
          >
            {isConsolidating ? (
              <Activity className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Database className="h-4 w-4 mr-2" />
            )}
            Nettoyer la base (Consolidation)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-[#0b0f19] border border-gray-800 p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm font-medium">Documents</p>
            <p className="text-3xl font-bold text-white mt-1">{stats?.documents || 0}</p>
          </div>
          <FileText className="h-10 w-10 text-gray-600" />
        </div>
        <div className="bg-[#0b0f19] border border-gray-800 p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm font-medium">Chunks (Atomes)</p>
            <p className="text-3xl font-bold text-cyan-400 mt-1">{stats?.chunks || 0}</p>
          </div>
          <BrainCircuit className="h-10 w-10 text-cyan-900/50" />
        </div>
        <div className="bg-[#0b0f19] border border-gray-800 p-5 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 text-sm font-medium">Chunks Canoniques</p>
            <p className="text-3xl font-bold text-fuchsia-400 mt-1">{stats?.canonical_chunks || 0}</p>
          </div>
          <Layers className="h-10 w-10 text-fuchsia-900/50" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
        <div className="lg:col-span-1 bg-[#0b0f19] border border-gray-800 rounded-xl flex flex-col h-96 lg:h-auto overflow-hidden">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50">
            <h3 className="font-bold text-white text-sm uppercase tracking-wider">Explorateur</h3>
          </div>
          <div className="p-2 flex-1 overflow-y-auto">
            {loading ? (
              <p className="text-gray-500 p-4 text-sm">Chargement...</p>
            ) : documents.length === 0 ? (
              <p className="text-gray-500 p-4 text-sm">Aucun document ingéré.</p>
            ) : (
              documents.map(docId => (
                <button
                  key={docId}
                  onClick={() => fetchDocumentData(docId)}
                  className={`w-full text-left p-3 rounded-lg mb-1 text-sm truncate transition-colors ${selectedDoc === docId ? 'bg-fuchsia-900/30 text-fuchsia-300 border border-fuchsia-800/50' : 'text-gray-400 hover:bg-gray-800'}`}
                  title={docId}
                >
                  <FileText className="h-4 w-4 inline-block mr-2 opacity-70" />
                  {docId.substring(0, 8)}...{docId.substring(docId.length - 8)}
                </button>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-3 bg-[#0b0f19] border border-gray-800 rounded-xl p-6 h-[600px] overflow-y-auto">
          {docData ? (
            <div className="space-y-6">
              <div className="flex justify-between items-start border-b border-gray-800 pb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-white flex items-center gap-4">
                    Document {docData.document_id.substring(0, 8)}...
                    <button 
                      onClick={() => openDocumentFolder(docData.document_id)}
                      className="px-3 py-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs rounded border border-gray-700 transition-colors flex items-center"
                    >
                      <svg className="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" /></svg>
                      Ouvrir le dossier
                    </button>
                  </h3>
                  <p className="text-sm text-gray-500 font-mono mt-1">{docData.document_id}</p>
                </div>
                <span className="bg-cyan-900/30 text-cyan-400 border border-cyan-800 px-3 py-1 rounded-full text-xs font-bold shrink-0">
                  {docData.chunks?.length || 0} Chunks
                </span>
              </div>
              
              <div className="space-y-4">
                {docData.chunks?.map((chunk: any, i: number) => (
                  <div key={chunk.id} className="bg-[#111827] border border-gray-800 rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-mono text-gray-500">#{chunk.ordinal} • {chunk.id.substring(0, 8)}</span>
                      {chunk.payload?.canonical_chunk_id && (
                        <span className="text-xs text-orange-400 flex items-center">
                          <Layers className="h-3 w-3 mr-1" />
                          Double sémantique
                        </span>
                      )}
                    </div>
                    <p className="text-gray-300 text-sm whitespace-pre-wrap font-mono bg-black/30 p-3 rounded border border-gray-800/50">
                      {chunk.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-600">
              <Database className="h-12 w-12 mb-4 opacity-20" />
              <p>Sélectionnez un document pour inspecter ses vecteurs</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function IngestionDashboard() {
  const [file, setFile] = useState<File | null>(null)
  const [projectId, setProjectId] = useState('demo')
  const [chunkSize, setChunkSize] = useState(1024)
  const [overlap, setOverlap] = useState(256)
  const [advancedOcr, setAdvancedOcr] = useState(false)
  const [orthogonalRotation, setOrthogonalRotation] = useState(false)
  const [tags, setTags] = useState('')
  const [ingesting, setIngesting] = useState(false)
  const [ingestResult, setIngestResult] = useState<any>(null)

  const handleUpload = async () => {
    if (!file || !projectId.trim()) return
    setIngesting(true)
    setIngestResult(null)
    
    const formData = new FormData()
    formData.append('project_id', projectId)
    formData.append('chunk_size', chunkSize.toString())
    formData.append('overlap', overlap.toString())
    formData.append('advanced_ocr', advancedOcr.toString())
    formData.append('orthogonal_rotation', orthogonalRotation.toString())
    formData.append('tags', tags)
    formData.append('file', file)

    try {
      const response = await fetch(`http://localhost:8000/projects/${projectId}/ingest`, {
        method: 'POST',
        body: formData
      })
      const data = await response.json()
      if (!response.ok) {
        setIngestResult({ error: data.detail || 'Erreur serveur' })
      } else {
        if (data.status === 'blocked' && data.errors && data.errors[0]?.includes('identique')) {
            if (window.confirm("Ce document existe déjà. Voulez-vous l'écraser ? (L'ancienne version sera supprimée)")) {
                formData.append('force', 'true');
                const forceResponse = await fetch(`http://localhost:8000/projects/${projectId}/ingest`, {
                    method: 'POST',
                    body: formData
                });
                const forceData = await forceResponse.json();
                if (!forceResponse.ok) {
                    setIngestResult({ error: forceData.detail || 'Erreur serveur' });
                } else {
                    setIngestResult(forceData);
                }
                return;
            }
        }
        setIngestResult(data)
      }
    } catch (err) {
      setIngestResult({ error: "Erreur de communication avec l'API." })
    } finally {
      setIngesting(false)
    }
  }

  return (
    <div className="flex flex-col h-full relative z-10">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Activity className="h-6 w-6 mr-3 text-cyan-400" />
          Le Radar (Ingestion & OCR)
        </h2>
        <span className="text-sm text-gray-500">Ajout au système RAG</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 overflow-y-auto pr-2">
        {/* Paramètres d'ingestion */}
        <div className="lg:col-span-1 space-y-6 bg-[#0b0f19] p-5 rounded-xl border border-gray-800 h-fit">
          <h3 className="text-lg font-bold text-white border-b border-gray-800 pb-2">Réglages Avancés</h3>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400">Projet Cible / Session</label>
            <input 
              type="text" 
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              className="w-full bg-[#111827] border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-cyan-500 outline-none text-sm"
              id="projectIdInput"
            />
            <p className="text-xs text-gray-500 italic">Définit le workspace isolé (dossier, collection Qdrant, base Graph). Chaque projet a sa propre base de connaissances vectorielle, SQL et Graph.</p>
          </div>

          <div className="space-y-4 pt-2">
            <label className="text-sm font-medium text-cyan-400 flex items-center">
              Contrôle des Chunks (Atomes)
            </label>
            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Chunk Size</span>
                <span>{chunkSize} chars</span>
              </div>
              <input type="range" min="100" max="8000" step="100" value={chunkSize} onChange={(e) => setChunkSize(Number(e.target.value))} className="w-full accent-cyan-500" />
            </div>
            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Overlap (Recouvrement)</span>
                <span>{overlap} chars</span>
              </div>
              <input type="range" min="0" max="1000" step="50" value={overlap} onChange={(e) => setOverlap(Number(e.target.value))} className="w-full accent-cyan-500" />
            </div>
          </div>

          <div className="space-y-2 pt-2 border-t border-gray-800">
            <label className="text-sm font-medium text-gray-400">Tags Métadonnées (csv)</label>
            <input 
              type="text" 
              placeholder="ex: finance, rapport, 2026"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="w-full bg-[#111827] border border-gray-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-cyan-500 outline-none text-sm"
            />
          </div>

          <div className="space-y-3 pt-2 border-t border-gray-800">
            <label className="text-sm font-medium text-purple-400">Traitement Multimodal</label>
            <label className="flex items-center space-x-3 cursor-pointer">
              <input type="checkbox" checked={advancedOcr} onChange={(e) => setAdvancedOcr(e.target.checked)} className="form-checkbox h-4 w-4 text-purple-500 rounded border-gray-700 bg-[#111827]" />
              <span className="text-sm text-gray-300">Force OCR (Dessins, Manuscrits)</span>
            </label>
            <label className="flex items-center space-x-3 cursor-pointer">
              <input type="checkbox" checked={orthogonalRotation} onChange={(e) => setOrthogonalRotation(e.target.checked)} className="form-checkbox h-4 w-4 text-purple-500 rounded border-gray-700 bg-[#111827]" />
              <span className="text-sm text-gray-300">Retournement Orthogonal (4 angles)</span>
            </label>
          </div>
        </div>

        {/* Drag and drop / Status */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#0b0f19] border-2 border-dashed border-gray-700 hover:border-cyan-500/50 rounded-xl p-8 transition-colors flex flex-col items-center justify-center text-center h-48 relative">
            <input 
              type="file" 
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
              accept=".pdf,.png,.jpg,.jpeg,.md,.txt"
            />
            <Activity className="h-10 w-10 text-cyan-500/50 mb-3" />
            <h3 className="text-lg font-medium text-white mb-1">
              {file ? file.name : "Glissez-Déposez un document"}
            </h3>
            <p className="text-sm text-gray-500">
              {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Support PDF, Images, et Textes"}
            </p>
          </div>

          <button 
            onClick={handleUpload}
            disabled={!file || ingesting}
            className="w-full py-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded-xl transition-all disabled:opacity-50 flex items-center justify-center"
          >
            {ingesting ? (
              <><Loader2 className="h-5 w-5 mr-2 animate-spin" /> Ingestion en cours...</>
            ) : "Lancer l'Ingestion Vectorielle"}
          </button>

          {ingestResult && (
            <div className={`p-5 rounded-xl border ${ingestResult.error ? 'bg-red-900/10 border-red-500/20' : 'bg-emerald-900/10 border-emerald-500/20'}`}>
              <div className="flex justify-between items-center mb-2">
                <h4 className={`font-bold ${ingestResult.error ? 'text-red-400' : 'text-emerald-400'}`}>
                  {ingestResult.error ? "Échec de l'Ingestion" : "Ingestion Terminée"}
                </h4>
                <div className="flex space-x-2">
                  <button 
                    onClick={() => navigator.clipboard.writeText(JSON.stringify(ingestResult, null, 2))} 
                    className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1 rounded border border-gray-600 transition-colors"
                  >
                    Copier JSON
                  </button>
                  <button 
                    onClick={() => {
                      const blob = new Blob([JSON.stringify(ingestResult, null, 2)], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `ingestion_report_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
                      a.click();
                      URL.revokeObjectURL(url);
                    }} 
                    className="text-xs bg-emerald-900/50 hover:bg-emerald-800/80 text-emerald-300 px-3 py-1 rounded border border-emerald-700/50 transition-colors"
                  >
                    Sauvegarder JSON
                  </button>
                </div>
              </div>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap overflow-auto max-h-48 mt-2">
                {JSON.stringify(ingestResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function QuarantineDashboard({ isActive }: { isActive?: boolean }) {
  const [projectId, setProjectId] = useState('demo')
  const [chunks, setChunks] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [vectorizing, setVectorizing] = useState(false)
  const [editedTexts, setEditedTexts] = useState<Record<string, string>>({})

  const fetchQuarantine = async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const res = await fetch(`http://localhost:8000/projects/${projectId}/quarantine`)
      if (res.ok) {
        const data = await res.json()
        setChunks(data.quarantined_chunks || [])
        // Initialize editable texts
        const initialEdits: Record<string, string> = {}
        ;(data.quarantined_chunks || []).forEach((c: any) => {
          initialEdits[c.id] = c.text
        })
        setEditedTexts(initialEdits)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isActive !== false) {
      fetchQuarantine()
    }
  }, [projectId, isActive])

  const handleValidate = async (chunkId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/projects/${projectId}/quarantine/${chunkId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_text: editedTexts[chunkId] })
      })
      if (res.ok) {
        setChunks(chunks.filter(c => c.id !== chunkId))
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleDiscard = async (chunkId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/projects/${projectId}/quarantine/${chunkId}/discard`, {
        method: 'POST'
      })
      if (res.ok) {
        setChunks(chunks.filter(c => c.id !== chunkId))
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleVectorize = async () => {
    if (!projectId || vectorizing) return
    setVectorizing(true)
    try {
      await fetch(`http://localhost:8000/projects/${projectId}/vectorize`, {
        method: 'POST'
      })
      alert("Vectorisation lancée. (Consultez les logs du backend)")
    } catch (err) {
      console.error(err)
    } finally {
      setVectorizing(false)
    }
  }

  return (
    <div className="flex flex-col h-full relative z-10 p-6 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center">
          <Shield className="h-6 w-6 mr-3 text-orange-400" />
          Tour de Contrôle (Quarantaine)
        </h2>
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-400">Projet:</label>
          <input 
            type="text" 
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="bg-[#0b0f19] border border-gray-700 rounded-lg px-3 py-1 text-white text-sm focus:ring-1 focus:ring-orange-500 outline-none"
          />
          <button onClick={fetchQuarantine} className="p-1.5 bg-gray-800 hover:bg-gray-700 rounded-md text-gray-300">
            <Activity className="h-4 w-4" />
          </button>
          <button 
            onClick={handleVectorize} 
            disabled={vectorizing}
            className="ml-4 px-3 py-1.5 bg-orange-600/20 hover:bg-orange-600/30 text-orange-400 border border-orange-500/30 rounded-md text-sm font-medium transition-colors flex items-center"
          >
            {vectorizing ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Database className="h-4 w-4 mr-2" />
            )}
            Vectoriser les Validés
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
           <Loader2 className="h-10 w-10 text-orange-500 animate-spin" />
        </div>
      ) : chunks.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
          <Shield className="h-12 w-12 mb-4 opacity-20 text-orange-500" />
          <p>Aucun chunk en quarantaine pour ce projet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {chunks.map(chunk => (
            <div key={chunk.id} className="bg-[#111827] border border-red-900/30 rounded-xl overflow-hidden flex flex-col">
              <div className="bg-red-900/20 p-3 border-b border-red-900/30 flex justify-between items-center">
                <span className="text-xs font-mono text-gray-400">Doc: {chunk.document_id.substring(0,8)}... | Chunk: {chunk.id.substring(0,6)}...</span>
                <span className="bg-red-900/50 text-red-300 text-xs px-2 py-0.5 rounded border border-red-800/50">Rejeté</span>
              </div>
              <div className="p-4 flex-1 space-y-4">
                <div>
                   <h4 className="text-xs font-bold text-orange-400 mb-1 uppercase tracking-wider">Motif du Juge :</h4>
                   <p className="text-sm text-gray-300 italic border-l-2 border-orange-500/50 pl-2 py-1 bg-black/20">{chunk.judge_feedback}</p>
                </div>
                <div className="flex-1 flex flex-col">
                   <h4 className="text-xs font-bold text-gray-400 mb-1 uppercase tracking-wider">Texte Éditable :</h4>
                   <textarea
                     className="w-full flex-1 min-h-[150px] bg-[#0b0f19] border border-gray-700 rounded-md p-3 text-sm font-mono text-gray-300 focus:ring-1 focus:ring-orange-500 outline-none"
                     value={editedTexts[chunk.id] || ''}
                     onChange={(e) => setEditedTexts({...editedTexts, [chunk.id]: e.target.value})}
                   />
                </div>
              </div>
              <div className="p-3 bg-gray-900/50 border-t border-gray-800 flex justify-between">
                <button 
                  onClick={() => handleDiscard(chunk.id)}
                  className="px-4 py-2 bg-red-900/30 hover:bg-red-900/50 text-red-400 border border-red-500/30 rounded text-sm transition-colors"
                >
                  Jeter définitivement
                </button>
                <button 
                  onClick={() => handleValidate(chunk.id)}
                  className="px-4 py-2 bg-emerald-900/30 hover:bg-emerald-900/50 text-emerald-400 border border-emerald-500/30 rounded text-sm font-bold transition-colors"
                >
                  Forcer la validation
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App
