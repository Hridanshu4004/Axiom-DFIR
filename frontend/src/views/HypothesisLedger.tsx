import React from 'react';
import { GitBranch, CheckCircle2, XCircle, AlertCircle, Shield, HelpCircle } from 'lucide-react';
import { Hypothesis } from '../types';

interface HypothesisLedgerProps {
  hypotheses: Hypothesis[];
}

export const HypothesisLedger: React.FC<HypothesisLedgerProps> = ({ hypotheses }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Principle Banner */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
      }}>
        <GitBranch size={22} style={{ color: 'var(--accent-cyan)', flexShrink: 0 }} />
        <div>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Falsification-First Hypothesis Engine
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            Hypotheses are evaluated by seeking contradicting forensic facts. Contradicting evidence carries double weight; a single verified contradiction refutes a candidate finding.
          </p>
        </div>
      </div>

      {/* Hypothesis Cards Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {hypotheses.length > 0 ? (
          hypotheses.map((h) => {
            const isConfirmed = h.status === 'CONFIRMED';
            const isRefuted = h.status === 'REFUTED';
            const isTesting = h.status === 'TESTING';

            return (
              <div
                key={h.hypothesis_id}
                className="card"
                style={{
                  borderLeft: `4px solid ${isConfirmed ? 'var(--accent-green)' : (isRefuted ? 'var(--accent-red)' : 'var(--accent-amber)')}`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px',
                }}
              >
                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span className="mono" style={{ fontSize: '0.82rem', fontWeight: 800, color: 'var(--accent-blue)' }}>
                        {h.hypothesis_id}
                      </span>
                      <span className={`badge ${isConfirmed ? 'badge-verified' : (isRefuted ? 'badge-contradicted' : 'badge-amber')}`}>
                        {isConfirmed && <CheckCircle2 size={12} />}
                        {isRefuted && <XCircle size={12} />}
                        {isTesting && <AlertCircle size={12} />}
                        {h.status}
                      </span>
                    </div>
                    <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {h.title}
                    </h4>
                  </div>

                  {/* Confidence Bar */}
                  <div style={{ minWidth: '160px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
                      <span>Confidence</span>
                      <span style={{ fontWeight: 700, color: isConfirmed ? 'var(--accent-green)' : (isRefuted ? 'var(--accent-red)' : 'var(--accent-amber)') }}>
                        {(h.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div style={{ height: '6px', backgroundColor: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{
                        width: `${Math.round(h.confidence_score * 100)}%`,
                        height: '100%',
                        backgroundColor: isConfirmed ? 'var(--accent-green)' : (isRefuted ? 'var(--accent-red)' : 'var(--accent-amber)'),
                      }} />
                    </div>
                  </div>
                </div>

                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                  {h.description}
                </p>

                {/* Targeted Entities */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Target Entities:</span>
                  {(h.entities || []).map((ent, idx) => (
                    <code key={idx} style={{ fontSize: '0.75rem' }}>{ent}</code>
                  ))}
                </div>

                {/* Resolution / Decision reason */}
                {h.resolution_reason && (
                  <div style={{
                    padding: '10px 14px',
                    borderRadius: '6px',
                    backgroundColor: isConfirmed ? 'rgba(0, 210, 106, 0.08)' : (isRefuted ? 'rgba(248, 113, 113, 0.08)' : 'rgba(251, 191, 36, 0.08)'),
                    border: `1px solid ${isConfirmed ? 'rgba(0, 210, 106, 0.2)' : (isRefuted ? 'rgba(248, 113, 113, 0.2)' : 'rgba(251, 191, 36, 0.2)')}`,
                    fontSize: '0.84rem',
                    color: 'var(--text-primary)',
                  }}>
                    <strong>Resolution Audit:</strong> {h.resolution_reason}
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="card" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
            No hypotheses generated yet. Launch the investigation to formulate propositions.
          </div>
        )}
      </div>
    </div>
  );
};

