import React, { useState, useMemo } from 'react';
import {
  Share2,
  Filter,
  Download,
  Info,
  Maximize2,
  Minimize2,
  ShieldAlert,
  Server,
  Globe,
  FileCode,
  User,
  ArrowRight,
  Layers,
  Cpu
} from 'lucide-react';
import { GraphData, GraphNode, GraphEdge } from '../types';

interface AttackGraphProps {
  graphData: GraphData | null;
  caseId: string;
}

export const AttackGraph: React.FC<AttackGraphProps> = ({ graphData, caseId }) => {
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [causalityFilter, setCausalityFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Fallback demo graph if graphData is empty or has 0 nodes
  const nodes: GraphNode[] = useMemo(() => {
    if (graphData && graphData.nodes && graphData.nodes.length > 0) {
      return graphData.nodes;
    }
    return [
      { id: 'proc:powershell:4120', label: 'powershell.exe (PID 4120)', type: 'process', evidence_ref: 'EV-MEM-001' },
      { id: 'net:198.51.100.45:443', label: '198.51.100.45:443 (C2)', type: 'network', evidence_ref: 'EV-PCAP-002' },
      { id: 'file:payload.ps1', label: 'C:\\Temp\\payload.ps1', type: 'file', evidence_ref: 'EV-DISK-003' },
      { id: 'user:svc_backup', label: 'CORP\\svc_backup', type: 'identity', evidence_ref: 'EV-EVTX-004' },
      { id: 'proc:svchost:892', label: 'svchost.exe (PID 892)', type: 'process', evidence_ref: 'EV-MEM-001' },
      { id: 'reg:runkey:updater', label: 'HKLM\\Software\\...\\Run', type: 'persistence', evidence_ref: 'EV-REG-005' },
    ];
  }, [graphData]);

  const edges: GraphEdge[] = useMemo(() => {
    if (graphData && graphData.edges && graphData.edges.length > 0) {
      return graphData.edges;
    }
    return [
      { source: 'proc:svchost:892', target: 'proc:powershell:4120', label: 'spawned', causality: 'CAUSAL', confidence: 0.98 },
      { source: 'proc:powershell:4120', target: 'net:198.51.100.45:443', label: 'established_c2', causality: 'CAUSAL', confidence: 0.95 },
      { source: 'proc:powershell:4120', target: 'file:payload.ps1', label: 'dropped_file', causality: 'CAUSAL', confidence: 0.99 },
      { source: 'proc:powershell:4120', target: 'user:svc_backup', label: 'impersonated', causality: 'TEMPORAL', confidence: 0.88 },
      { source: 'file:payload.ps1', target: 'reg:runkey:updater', label: 'registered_persistence', causality: 'CAUSAL', confidence: 0.94 },
    ];
  }, [graphData]);

  // Node type categories
  const nodeTypes = ['ALL', 'process', 'network', 'file', 'identity', 'persistence'];

  // Filtered nodes
  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const matchType = typeFilter === 'ALL' || n.type.toLowerCase().includes(typeFilter.toLowerCase());
      const matchSearch =
        n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.id.toLowerCase().includes(searchQuery.toLowerCase());
      return matchType && matchSearch;
    });
  }, [nodes, typeFilter, searchQuery]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  // Filtered edges
  const filteredEdges = useMemo(() => {
    return edges.filter((e) => {
      const sourceIn = filteredNodeIds.has(e.source);
      const targetIn = filteredNodeIds.has(e.target);
      const matchCausality = causalityFilter === 'ALL' || e.causality === causalityFilter;
      return sourceIn && targetIn && matchCausality;
    });
  }, [edges, filteredNodeIds, causalityFilter]);

  // Node Icon Helper
  const getNodeIcon = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('proc')) return <Cpu className="w-4 h-4 text-cyan-400" />;
    if (t.includes('net') || t.includes('ip')) return <Globe className="w-4 h-4 text-amber-400" />;
    if (t.includes('file')) return <FileCode className="w-4 h-4 text-purple-400" />;
    if (t.includes('user') || t.includes('ident')) return <User className="w-4 h-4 text-emerald-400" />;
    return <ShieldAlert className="w-4 h-4 text-red-400" />;
  };

  const getNodeColor = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('proc')) return { border: 'border-cyan-500/60', bg: 'bg-cyan-950/40', text: 'text-cyan-300' };
    if (t.includes('net') || t.includes('ip')) return { border: 'border-amber-500/60', bg: 'bg-amber-950/40', text: 'text-amber-300' };
    if (t.includes('file')) return { border: 'border-purple-500/60', bg: 'bg-purple-950/40', text: 'text-purple-300' };
    if (t.includes('user') || t.includes('ident')) return { border: 'border-emerald-500/60', bg: 'bg-emerald-950/40', text: 'text-emerald-300' };
    return { border: 'border-red-500/60', bg: 'bg-red-950/40', text: 'text-red-300' };
  };

  const exportJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify({ nodes: filteredNodes, edges: filteredEdges }, null, 2));
    const dl = document.createElement('a');
    dl.setAttribute('href', dataStr);
    dl.setAttribute('download', `${caseId}_attack_graph.json`);
    dl.click();
  };

  // Connected edges for selected node
  const selectedNodeEdges = useMemo(() => {
    if (!selectedNode) return [];
    return edges.filter((e) => e.source === selectedNode.id || e.target === selectedNode.id);
  }, [selectedNode, edges]);

  return (
    <div className={`space-y-6 ${isFullscreen ? 'fixed inset-0 z-50 bg-[#0B0F19] p-6 overflow-y-auto' : ''}`}>
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#111827] border border-cyan-900/30 p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
            <Share2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              Attack Graph & Relationship Visualizer
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                {filteredNodes.length} Nodes • {filteredEdges.length} Edges
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Evidence-backed directed provenance relationships (Processes, Network Sockets, Identities, Files)
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Search */}
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-3 py-1.5 bg-[#0B0F19] border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />

          {/* Causality Filter */}
          <select
            value={causalityFilter}
            onChange={(e) => setCausalityFilter(e.target.value)}
            className="px-3 py-1.5 bg-[#0B0F19] border border-slate-700 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Causality</option>
            <option value="CAUSAL">Causal Links Only</option>
            <option value="TEMPORAL">Temporal Correlation</option>
            <option value="EVIDENTIARY">Evidentiary</option>
          </select>

          {/* Export JSON */}
          <button
            onClick={exportJson}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-1.5 border border-slate-700 transition"
          >
            <Download className="w-3.5 h-3.5" /> Export JSON
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition"
            title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Node Type Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-400 flex items-center gap-1 font-semibold">
          <Filter className="w-3.5 h-3.5" /> Entity Filter:
        </span>
        {nodeTypes.map((type) => (
          <button
            key={type}
            onClick={() => setTypeFilter(type)}
            className={`px-3 py-1 rounded-full uppercase tracking-wider font-mono font-medium transition ${
              typeFilter === type
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/60 shadow-sm'
                : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 border border-slate-700/50'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Main Workspace: Visual Grid Canvas + Node Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Graph Canvas / Node Relationship Cards */}
        <div className="lg:col-span-2 bg-[#111827] border border-slate-800 rounded-xl p-5 relative overflow-hidden min-h-[500px]">
          {/* Subtle Grid Background */}
          <div
            className="absolute inset-0 opacity-10 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, #38bdf8 1px, transparent 1px)',
              backgroundSize: '24px 24px',
            }}
          />

          <div className="relative z-10 flex justify-between items-center mb-4">
            <span className="text-xs uppercase font-mono tracking-wider text-slate-400">
              Interactive Relationship Topology
            </span>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Causal
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Temporal
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Identity
              </span>
            </div>
          </div>

          {/* Node Cards Layout */}
          <div className="relative z-10 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {filteredNodes.map((node) => {
              const colors = getNodeColor(node.type);
              const isSelected = selectedNode?.id === node.id;
              const nodeOutEdges = edges.filter((e) => e.source === node.id);
              const nodeInEdges = edges.filter((e) => e.target === node.id);

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`p-4 rounded-xl border cursor-pointer transition transform hover:-translate-y-0.5 ${
                    isSelected
                      ? 'border-cyan-400 bg-cyan-950/50 shadow-lg shadow-cyan-950/50 ring-1 ring-cyan-400'
                      : `${colors.border} ${colors.bg} hover:border-slate-500`
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-md bg-slate-900 border border-slate-700/60">
                        {getNodeIcon(node.type)}
                      </div>
                      <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                        {node.type}
                      </span>
                    </div>
                    {node.evidence_ref && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-cyan-400 border border-slate-800">
                        {node.evidence_ref}
                      </span>
                    )}
                  </div>

                  <h3 className={`text-sm font-semibold truncate ${colors.text}`}>{node.label}</h3>
                  <p className="text-[11px] font-mono text-slate-500 truncate mt-0.5">{node.id}</p>

                  <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                    <span>{nodeInEdges.length} Inbound</span>
                    <span className="text-slate-600">•</span>
                    <span>{nodeOutEdges.length} Outbound</span>
                  </div>
                </div>
              );
            })}
          </div>

          {filteredNodes.length === 0 && (
            <div className="relative z-10 h-64 flex flex-col items-center justify-center text-slate-500 text-sm">
              <Share2 className="w-10 h-10 mb-2 opacity-30 text-cyan-400" />
              <p>No graph nodes match current filters.</p>
            </div>
          )}
        </div>

        {/* Selected Node Details & Connected Edges Inspector */}
        <div className="bg-[#111827] border border-slate-800 rounded-xl p-5 flex flex-col">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800 mb-4">
            <Info className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider font-mono">
              Entity Inspector
            </h3>
          </div>

          {selectedNode ? (
            <div className="space-y-4 flex-1">
              <div className="bg-[#0B0F19] p-3.5 rounded-lg border border-slate-800">
                <div className="text-[10px] font-mono text-slate-500 uppercase">Entity ID</div>
                <div className="text-xs font-mono text-cyan-300 break-all select-all font-semibold mt-0.5">
                  {selectedNode.id}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-[#0B0F19] p-2.5 rounded-lg border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">Type</div>
                  <div className="text-xs font-semibold text-slate-200 capitalize mt-0.5">
                    {selectedNode.type}
                  </div>
                </div>
                <div className="bg-[#0B0F19] p-2.5 rounded-lg border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">Evidence Ref</div>
                  <div className="text-xs font-mono text-cyan-400 font-semibold mt-0.5">
                    {selectedNode.evidence_ref || 'Synthetic Inferred'}
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-mono font-bold text-slate-400 uppercase mb-2 flex items-center justify-between">
                  <span>Connected Relationships</span>
                  <span className="text-[10px] text-cyan-400 font-normal">
                    {selectedNodeEdges.length} links
                  </span>
                </h4>

                <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                  {selectedNodeEdges.map((e, idx) => {
                    const isSource = e.source === selectedNode.id;
                    const otherNodeId = isSource ? e.target : e.source;
                    const causalityColor =
                      e.causality === 'CAUSAL'
                        ? 'text-cyan-400 border-cyan-800 bg-cyan-950/40'
                        : e.causality === 'TEMPORAL'
                        ? 'text-amber-400 border-amber-800 bg-amber-950/40'
                        : 'text-purple-400 border-purple-800 bg-purple-950/40';

                    return (
                      <div
                        key={idx}
                        className="bg-[#0B0F19] p-2.5 rounded-lg border border-slate-800 text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between">
                          <span
                            className={`text-[9px] font-mono px-1.5 py-0.5 rounded border uppercase font-bold ${causalityColor}`}
                          >
                            {e.causality || 'LINK'}
                          </span>
                          {e.confidence && (
                            <span className="text-[10px] font-mono text-slate-400">
                              {(e.confidence * 100).toFixed(0)}% Conf
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-1.5 text-slate-300">
                          <span className="font-mono text-[10px] text-slate-500 truncate max-w-[90px]">
                            {isSource ? 'Self' : otherNodeId}
                          </span>
                          <ArrowRight className="w-3 h-3 text-cyan-400 flex-shrink-0" />
                          <span className="text-xs font-semibold text-cyan-200 truncate">
                            {e.label}
                          </span>
                          <ArrowRight className="w-3 h-3 text-cyan-400 flex-shrink-0" />
                          <span className="font-mono text-[10px] text-slate-500 truncate max-w-[90px]">
                            {isSource ? otherNodeId : 'Self'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                  {selectedNodeEdges.length === 0 && (
                    <p className="text-xs text-slate-500 italic py-2">
                      No direct graph relationships registered.
                    </p>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-center p-6">
              <Layers className="w-8 h-8 mb-2 opacity-40 text-cyan-400" />
              <p className="text-xs font-semibold text-slate-400">No Node Selected</p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-[200px]">
                Click any process, socket, identity, or file node on the topology grid to inspect evidence links and causality.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

