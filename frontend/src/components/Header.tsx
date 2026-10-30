import React from 'react';
import { RefreshCw, ShieldAlert, Cpu, Sparkles } from 'lucide-react';

interface HeaderProps {
  caseId: string;
  stage: string;
  integrityStatus: string;
  nebiusConfigured: boolean;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  caseId,
  stage,
  integrityStatus,
  nebiusConfigured,
  onRefresh,
  isRefreshing,
}) => {
  return (
    <header style={{
      height: '64px',
      borderBottom: '1px solid var(--border-color)',
      backgroundColor: 'var(--bg-secondary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 28px',
      flexShrink: 0,
    }}>
      {/* Left: Investigation Context Indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Case:</span>
          <span className="mono" style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-blue)' }}>
            {caseId || 'CASE-DEMO-2026'}
          </span>
        </div>

        <div style={{ width: '1px', height: '18px', backgroundColor: 'var(--border-color)' }} />

        {/* Stage Badge */}
        <span className="badge badge-amber" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Cpu size={12} />
          {stage || 'STAGE_01_CASE_INITIALIZATION'}
        </span>

        {/* Integrity Status */}
        <span className={`badge ${integrityStatus === 'MATCH' || integrityStatus === 'BASELINED' ? 'badge-verified' : 'badge-contradicted'}`}>
          <ShieldAlert size={12} />
          {integrityStatus === 'MATCH' ? 'SHA256 INTACT' : (integrityStatus || 'PENDING')}
        </span>

        {/* Nebius Model Mode */}
        <span className={`badge ${nebiusConfigured ? 'badge-cyan' : 'badge-muted'}`}>
          <Sparkles size={12} />
          {nebiusConfigured ? 'NEBIUS LIVE INFERENCE' : 'SYNTHETIC REASONING (DEMO)'}
        </span>
      </div>

      {/* Right: Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="btn btn-secondary"
          style={{ padding: '6px 14px', fontSize: '0.8rem' }}
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          <span>Refresh State</span>
        </button>
      </div>
    </header>
  );
};

