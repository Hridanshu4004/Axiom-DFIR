import React, { useState } from 'react';
import { HardDrive, ShieldCheck, FileCode, CheckCircle2, Copy, Check, Lock, Database } from 'lucide-react';
import { EvidenceItem } from '../types';

interface EvidenceExplorerProps {
  evidenceItems: EvidenceItem[];
  caseId: string;
}

export const EvidenceExplorer: React.FC<EvidenceExplorerProps> = ({ evidenceItems, caseId }) => {
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const handleCopy = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const totalBytes = evidenceItems.reduce((acc, it) => acc + (it.size_bytes || 0), 0);
  const formattedTotalSize = (totalBytes / (1024 * 1024)).toFixed(2);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Evidence Banner */}
      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '18px 22px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '8px',
            background: 'rgba(56, 189, 248, 0.1)',
            border: '1px solid var(--accent-blue)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-blue)',
          }}>
            <Database size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Content-Addressed Evidence Repository (CAS)
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              All forensic files are ingested read-only (<code style={{ fontSize: '0.75rem' }}>O_RDONLY</code>) and stored by immutable SHA-256 digests.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Artifacts</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{evidenceItems.length}</div>
          </div>
          <div style={{ width: '1px', height: '24px', backgroundColor: 'var(--border-color)' }} />
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Volume Size</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-primary)' }}>{formattedTotalSize} MB</div>
          </div>
          <div style={{ width: '1px', height: '24px', backgroundColor: 'var(--border-color)' }} />
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Write Protection</div>
            <span className="badge badge-verified">
              <Lock size={10} /> ENFORCED
            </span>
          </div>
        </div>
      </div>

      {/* Evidence Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Evidence ID</th>
              <th>Filename</th>
              <th>Artifact Category</th>
              <th>SHA-256 Digest</th>
              <th>Size</th>
              <th>Read-Only</th>
              <th>Acquisition Origin</th>
            </tr>
          </thead>
          <tbody>
            {evidenceItems.length > 0 ? (
              evidenceItems.map((item) => (
                <tr key={item.evidence_id}>
                  <td className="mono" style={{ fontWeight: 700, color: 'var(--accent-blue)' }}>
                    {item.evidence_id}
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    {item.original_filename}
                  </td>
                  <td>
                    <span className="badge badge-amber">
                      {item.artifact_type}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <code style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        {item.sha256_hash.substring(0, 16)}...{item.sha256_hash.substring(item.sha256_hash.length - 8)}
                      </code>
                      <button
                        onClick={() => handleCopy(item.sha256_hash)}
                        title="Copy full SHA-256 hash"
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: copiedHash === item.sha256_hash ? 'var(--accent-green)' : 'var(--text-muted)',
                          cursor: 'pointer',
                        }}
                      >
                        {copiedHash === item.sha256_hash ? <Check size={14} /> : <Copy size={14} />}
                      </button>
                    </div>
                  </td>
                  <td className="mono" style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                    {(item.size_bytes / (1024 * 1024)).toFixed(2)} MB
                  </td>
                  <td>
                    <span className="badge badge-verified">
                      <Lock size={10} /> YES
                    </span>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {item.provenance}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                  No evidence files cataloged in this case manifest.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

