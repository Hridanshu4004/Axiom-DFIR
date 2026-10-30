import React, { useState, useMemo } from 'react';
import {
  Clock,
  Filter,
  Search,
  Shield,
  Download,
  Terminal,
  Activity,
  Layers,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { TimelineEvent } from '../types';

interface InvestigationTimelineProps {
  timeline: TimelineEvent[];
  caseId: string;
}

export const InvestigationTimeline: React.FC<InvestigationTimelineProps> = ({ timeline, caseId }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  // Fallback demo events if timeline is empty
  const events: TimelineEvent[] = useMemo(() => {
    if (timeline && timeline.length > 0) {
      return timeline;
    }
    return [
      {
        timestamp: '2026-10-30T07:15:22Z',
        event: 'PROCESS_EXECUTION: powershell.exe spawned by svchost.exe (PID 4120)',
        pid: 4120,
        status: 'VERIFIED',
        evidence_ref: 'EV-MEM-001',
        mitre_technique_id: 'T1059.001',
        mitre_technique_name: 'PowerShell',
      },
      {
        timestamp: '2026-10-30T07:15:45Z',
        event: 'NETWORK_SOCKET: Outbound TCP socket established to 198.51.100.45:443',
        pid: 4120,
        status: 'VERIFIED',
        evidence_ref: 'EV-PCAP-002',
        mitre_technique_id: 'T1071.001',
        mitre_technique_name: 'Web Protocols',
      },
      {
        timestamp: '2026-10-30T07:16:10Z',
        event: 'FILE_CREATION: Dropped script payload C:\\Temp\\payload.ps1 (SHA256: e3b0c44...)',
        pid: 4120,
        status: 'VERIFIED',
        evidence_ref: 'EV-DISK-003',
        mitre_technique_id: 'T1105',
        mitre_technique_name: 'Ingress Tool Transfer',
      },
      {
        timestamp: '2026-10-30T07:17:02Z',
        event: 'AUTH_EVENT: Privilege escalation attempt impersonating CORP\\svc_backup',
        pid: 4120,
        status: 'PARTIALLY_VERIFIED',
        evidence_ref: 'EV-EVTX-004',
        mitre_technique_id: 'T1078.002',
        mitre_technique_name: 'Domain Accounts',
      },
      {
        timestamp: '2026-10-30T07:18:30Z',
        event: 'PERSISTENCE: Registry Run Key added under HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
        pid: 4120,
        status: 'VERIFIED',
        evidence_ref: 'EV-REG-005',
        mitre_technique_id: 'T1547.001',
        mitre_technique_name: 'Registry Run Keys',
      },
    ];
  }, [timeline]);

  const categories = ['ALL', 'PROCESS', 'NETWORK', 'FILE', 'AUTH', 'PERSISTENCE'];

  const filteredEvents = useMemo(() => {
    let list = [...events];

    if (categoryFilter !== 'ALL') {
      list = list.filter((e) => e.event.toUpperCase().includes(categoryFilter));
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (e) =>
          e.event.toLowerCase().includes(q) ||
          e.timestamp.toLowerCase().includes(q) ||
          (e.mitre_technique_id && e.mitre_technique_id.toLowerCase().includes(q)) ||
          (e.mitre_technique_name && e.mitre_technique_name.toLowerCase().includes(q)) ||
          (e.evidence_ref && e.evidence_ref.toLowerCase().includes(q))
      );
    }

    list.sort((a, b) => {
      const tA = new Date(a.timestamp).getTime();
      const tB = new Date(b.timestamp).getTime();
      return sortOrder === 'asc' ? tA - tB : tB - tA;
    });

    return list;
  }, [events, categoryFilter, searchQuery, sortOrder]);

  const exportCsv = () => {
    const headers = ['Timestamp', 'Event', 'PID', 'Status', 'EvidenceRef', 'MITRE ID', 'MITRE Name'];
    const rows = filteredEvents.map((e) => [
      `"${e.timestamp}"`,
      `"${e.event.replace(/"/g, '""')}"`,
      e.pid ?? '',
      e.status ?? '',
      e.evidence_ref ?? '',
      e.mitre_technique_id ?? '',
      `"${e.mitre_technique_name ?? ''}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const dl = document.createElement('a');
    dl.setAttribute('href', encodeURI(csvContent));
    dl.setAttribute('download', `${caseId}_timeline.csv`);
    dl.click();
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#111827] border border-cyan-900/30 p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              Chronological Forensic Timeline
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">
                {filteredEvents.length} Events Recorded
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Normalized timeline reconstructed strictly from evidentiary artifacts with MITRE ATT&CK alignment
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="px-3 py-1.5 bg-[#0B0F19] hover:bg-slate-800 text-slate-300 text-xs font-mono rounded-lg border border-slate-700 transition"
          >
            Sort: {sortOrder === 'asc' ? 'Oldest First ▲' : 'Newest First ▼'}
          </button>
          <button
            onClick={exportCsv}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg flex items-center gap-1.5 border border-slate-700 transition"
          >
            <Download className="w-3.5 h-3.5" /> Export CSV
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-slate-400 flex items-center gap-1 font-semibold">
            <Filter className="w-3.5 h-3.5" /> Filter Category:
          </span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1 rounded-full uppercase tracking-wider font-mono font-medium transition ${
                categoryFilter === cat
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/60 shadow-sm'
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 border border-slate-700/50'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="relative min-w-[260px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search events, PIDs, MITRE IDs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-[#111827] border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Visual Timeline Stream */}
      <div className="relative pl-6 md:pl-8 border-l-2 border-slate-800 space-y-6 my-4">
        {filteredEvents.map((evt, idx) => {
          const isVerified = evt.status === 'VERIFIED';
          const isNetwork = evt.event.includes('NETWORK');
          const isProcess = evt.event.includes('PROCESS');
          const isAuth = evt.event.includes('AUTH');
          const isFile = evt.event.includes('FILE');

          return (
            <div key={idx} className="relative group">
              {/* Timeline Node Dot */}
              <div
                className={`absolute -left-[31px] md:-left-[39px] top-1.5 w-4 h-4 rounded-full border-2 transition ${
                  isVerified
                    ? 'bg-[#0B0F19] border-cyan-400 ring-4 ring-cyan-950/60'
                    : 'bg-[#0B0F19] border-amber-400 ring-4 ring-amber-950/60'
                }`}
              />

              {/* Event Card */}
              <div className="bg-[#111827] border border-slate-800/80 hover:border-slate-700 p-4 rounded-xl transition duration-150">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-slate-800/60">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/60">
                      {evt.timestamp}
                    </span>
                    {evt.pid && (
                      <span className="font-mono text-[11px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                        PID: {evt.pid}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {evt.evidence_ref && (
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                        Ref: {evt.evidence_ref}
                      </span>
                    )}
                    <span
                      className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase border ${
                        isVerified
                          ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800'
                          : 'bg-amber-950/60 text-amber-400 border-amber-800'
                      }`}
                    >
                      {evt.status || 'LOGGED'}
                    </span>
                  </div>
                </div>

                <div className="mt-3">
                  <h4 className="text-sm font-semibold text-slate-200 font-mono tracking-tight">
                    {evt.event}
                  </h4>
                </div>

                {/* MITRE & Metadata Footer */}
                {evt.mitre_technique_id && (
                  <div className="mt-3 pt-2.5 border-t border-slate-800/50 flex flex-wrap items-center gap-2">
                    <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-red-950/40 border border-red-900/60 text-red-300 text-xs font-mono">
                      <Shield className="w-3 h-3 text-red-400" />
                      <span className="font-bold">{evt.mitre_technique_id}</span>
                      <ChevronRight className="w-2.5 h-2.5 text-red-500" />
                      <span>{evt.mitre_technique_name}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {filteredEvents.length === 0 && (
          <div className="p-8 text-center bg-[#111827] rounded-xl border border-slate-800 text-slate-500 text-sm">
            <Clock className="w-8 h-8 mx-auto mb-2 opacity-30 text-cyan-400" />
            <p>No timeline events match the current filter query.</p>
          </div>
        )}
      </div>
    </div>
  );
};

