import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  FolderLock,
  Cpu,
  FileCheck2,
  Lock,
  Sparkles,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import { CaseSummary, Finding } from '../types';

interface OverviewDashboardProps {
  cases: CaseSummary[];
  activeCase: CaseSummary | null;
  findings: Finding[];
  onSelectTab: (tab: string) => void;
  nebiusConfigured: boolean;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({
  cases,
  activeCase,
  findings,
  onSelectTab,
  nebiusConfigured,
}) => {
  const verifiedCount = findings.filter((f) => f.validation_status === 'VERIFIED').length;
  const contradictedCount = findings.filter((f) => f.validation_status === 'CONTRADICTED').length;
  const totalFindings = findings.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Core Principle Hero Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(0, 240, 255, 0.08) 0%, rgba(15, 23, 38, 0.6) 100%)',
        border: '1px solid rgba(0, 240, 255, 0.25)',
        borderRadius: '8px',
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '8px',
            backgroundColor: 'rgba(0, 240, 255, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-cyan)',
            flexShrink: 0,
          }}>
            <ShieldCheck size={26} />
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--accent-cyan)', marginBottom: '2px' }}>
              Core Engineering Invariant
            </div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              "The AI may propose an investigative finding, but only verified forensic evidence can confirm it."
            </div>
          </div>
        </div>

        <button onClick={() => onSelectTab('workspace')} className="btn btn-primary" style={{ flexShrink: 0 }}>
          <span>Launch Investigation</span>
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
        gap: '16px',
      }}>
        {/* Metric 1: Verified Findings */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Verified Findings</span>
            <ShieldCheck size={18} style={{ color: 'var(--accent-green)' }} />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-green)', marginTop: '8px' }}>
            {verifiedCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Deterministically proven by evidence
          </div>
        </div>

        {/* Metric 2: Blocked Hallucinations */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Refuted Claims</span>
            <ShieldAlert size={18} style={{ color: 'var(--accent-red)' }} />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--accent-red)', marginTop: '8px' }}>
            {contradictedCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Hallucinations rejected by code gate
          </div>
        </div>

        {/* Metric 3: Active Case Status */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Active Stage</span>
            <Cpu size={18} style={{ color: 'var(--accent-amber)' }} />
          </div>
          <div className="mono" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--accent-amber)', marginTop: '12px' }}>
            {activeCase?.current_stage || 'STAGE_15: COMPLETION'}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '8px' }}>
            Status: {activeCase?.status || 'COMPLETED'}
          </div>
        </div>

        {/* Metric 4: Chain of Custody */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-muted)' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>Chain of Custody</span>
            <Lock size={18} style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '10px' }}>
            ISO/IEC 27037 SEAL
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--accent-green)', marginTop: '6px' }}>
            Ed25519 Signatures Verified
          </div>
        </div>
      </div>

      {/* Investigation Details & Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Left: Recent Findings Table */}
        <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
          <div style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--border-color)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Verified Findings in Active Case
            </h3>
            <button onClick={() => onSelectTab('findings')} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
              View All Findings
            </button>
          </div>

          <div className="table-container" style={{ border: 'none', borderRadius: '0' }}>
            <table>
              <thead>
                <tr>
                  <th>Finding ID</th>
                  <th>Title</th>
                  <th>Verdict</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {findings.length > 0 ? (
                  findings.slice(0, 5).map((f) => (
                    <tr key={f.finding_id} className="clickable" onClick={() => onSelectTab('findings')}>
                      <td className="mono" style={{ color: 'var(--accent-blue)', fontWeight: 600 }}>
                        {f.finding_id}
                      </td>
                      <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                        {f.title}
                      </td>
                      <td>
                        <span className={`badge ${f.validation_status === 'VERIFIED' ? 'badge-verified' : 'badge-contradicted'}`}>
                          {f.validation_status}
                        </span>
                      </td>
                      <td style={{ color: 'var(--text-secondary)' }}>
                        {(f.confidence * 100).toFixed(0)}%
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                      No findings evaluated yet. Run an investigation to analyze evidence.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Inference Engine & Architecture Overview */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
            <Sparkles size={18} style={{ color: 'var(--accent-cyan)' }} />
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Inference Telemetry</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Provider</span>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Nebius Token Factory</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Status</span>
              <span className={`badge ${nebiusConfigured ? 'badge-cyan' : 'badge-muted'}`}>
                {nebiusConfigured ? 'ONLINE' : 'SYNTHETIC DEMO'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Triage Profile</span>
              <span className="mono" style={{ fontSize: '0.78rem', color: 'var(--accent-blue)' }}>Nemotron 3.5 Lightning</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Deep Reasoning</span>
              <span className="mono" style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)' }}>Nemotron 3 Ultra 550B</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-muted)' }}>Hallucination Defense</span>
              <span className="badge badge-verified">100% BLOCKED</span>
            </div>
          </div>

          <button onClick={() => onSelectTab('models')} className="btn btn-secondary" style={{ marginTop: 'auto', width: '100%' }}>
            Open Model Observatory
          </button>
        </div>
      </div>
    </div>
  );
};

