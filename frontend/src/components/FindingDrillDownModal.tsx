import React from 'react';
import { X, CheckCircle2, XCircle, AlertTriangle, Shield, ExternalLink, Terminal } from 'lucide-react';
import { Finding } from '../types';

interface FindingDrillDownModalProps {
  finding: Finding | null;
  onClose: () => void;
}

export const FindingDrillDownModal: React.FC<FindingDrillDownModalProps> = ({ finding, onClose }) => {
  if (!finding) return null;

  const isVerified = finding.validation_status === 'VERIFIED';
  const isContradicted = finding.validation_status === 'CONTRADICTED';
  const isPartial = finding.validation_status === 'PARTIALLY_VERIFIED';

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(5, 8, 14, 0.85)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '760px',
          maxWidth: '100%',
          maxHeight: '90vh',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          borderRadius: '10px',
          overflowY: 'auto',
          boxShadow: '0 25px 60px rgba(0, 0, 0, 0.8)',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-secondary)',
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="mono" style={{ fontSize: '0.8rem', color: 'var(--accent-blue)', fontWeight: 700 }}>
                {finding.finding_id}
              </span>
              <span className={`badge ${isVerified ? 'badge-verified' : (isContradicted ? 'badge-contradicted' : (isPartial ? 'badge-amber' : 'badge-muted'))}`}>
                {finding.validation_status}
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Confidence: {(finding.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {finding.title}
            </h2>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '4px',
              borderRadius: '4px',
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Explanation Banner */}
          <div style={{
            padding: '14px 18px',
            borderRadius: '6px',
            backgroundColor: isVerified
              ? 'rgba(0, 210, 106, 0.08)'
              : (isContradicted ? 'rgba(248, 113, 113, 0.08)' : 'rgba(251, 191, 36, 0.08)'),
            border: `1px solid ${isVerified ? 'rgba(0, 210, 106, 0.25)' : (isContradicted ? 'rgba(248, 113, 113, 0.25)' : 'rgba(251, 191, 36, 0.25)')}`,
          }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px', color: isVerified ? 'var(--accent-green)' : (isContradicted ? 'var(--accent-red)' : 'var(--accent-amber)') }}>
              Deterministic Validation Decision
            </div>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-primary)' }}>
              {finding.rejection_reason || 'All decomposed atomic claims deterministically match ground-truth evidence tables.'}
            </p>
          </div>

          {/* Section: Original AI Claimed Values */}
          <div>
            <h4 style={{ fontSize: '0.82rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px', letterSpacing: '0.04em' }}>
              Original AI Candidate Claims
            </h4>
            <div style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '12px 16px',
            }}>
              <pre className="mono" style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)' }}>
                {JSON.stringify(finding.claims || { finding_id: finding.finding_id, title: finding.title }, null, 2)}
              </pre>
            </div>
          </div>

          {/* Section: Deterministic Validation Checks */}
          <div>
            <h4 style={{ fontSize: '0.82rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px', letterSpacing: '0.04em' }}>
              Evidence Rule Evaluations & Cross-Checks
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(finding.checks && finding.checks.length > 0) ? (
                finding.checks.map((c, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '6px',
                      padding: '12px 16px',
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: '12px',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <code style={{ fontSize: '0.75rem' }}>{c.claim_type}</code>
                        {c.matched && (
                          <span className="badge badge-verified" style={{ fontSize: '0.65rem' }}>
                            <CheckCircle2 size={10} /> MATCHED
                          </span>
                        )}
                        {c.contradicted && (
                          <span className="badge badge-contradicted" style={{ fontSize: '0.65rem' }}>
                            <XCircle size={10} /> CONTRADICTED
                          </span>
                        )}
                        {!c.matched && !c.contradicted && (
                          <span className="badge badge-amber" style={{ fontSize: '0.65rem' }}>
                            <AlertTriangle size={10} /> UNVERIFIED
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                        {c.detail}
                      </div>
                    </div>

                    {c.evidence_ref && (
                      <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--accent-blue)', whiteSpace: 'nowrap' }}>
                        Ref: {c.evidence_ref}
                      </span>
                    )}
                  </div>
                ))
              ) : (
                <div style={{ padding: '12px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  No individual check items recorded.
                </div>
              )}
            </div>
          </div>

          {/* Section: Evidence Provenance & References */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
          }}>
            <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '14px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-green)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
                Corroborating Evidence
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(finding.corroborating_evidence_refs && finding.corroborating_evidence_refs.length > 0) ? (
                  finding.corroborating_evidence_refs.map((r, i) => (
                    <span key={i} className="mono badge badge-verified" style={{ fontSize: '0.72rem' }}>
                      {r}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None recorded</span>
                )}
              </div>
            </div>

            <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '14px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-red)', fontWeight: 700, textTransform: 'uppercase', marginBottom: '6px' }}>
                Contradicting Evidence
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                {(finding.contradicting_evidence_refs && finding.contradicting_evidence_refs.length > 0) ? (
                  finding.contradicting_evidence_refs.map((r, i) => (
                    <span key={i} className="mono badge badge-contradicted" style={{ fontSize: '0.72rem' }}>
                      {r}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>None (Zero Contradictions)</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-secondary)',
          display: 'flex',
          justifyContent: 'flex-end',
        }}>
          <button onClick={onClose} className="btn btn-secondary">
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};

