import React, { useState } from 'react';
import { FolderLock, Plus, CheckCircle2, Search, ArrowRight, ShieldCheck, Database } from 'lucide-react';
import { CaseSummary } from '../types';

interface CaseManagementProps {
  cases: CaseSummary[];
  activeCaseId: string;
  onSelectCase: (caseId: string) => void;
  onCreateCase: (caseId: string, evidencePath: string, desc: string) => Promise<void>;
}

export const CaseManagement: React.FC<CaseManagementProps> = ({
  cases,
  activeCaseId,
  onSelectCase,
  onCreateCase,
}) => {
  const [showCreate, setShowCreate] = useState(false);
  const [newCaseId, setNewCaseId] = useState('');
  const [newEvidencePath, setNewEvidencePath] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCaseId.trim() || !newEvidencePath.trim()) {
      setError('Please provide both a Case ID and Evidence Path.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await onCreateCase(newCaseId.trim(), newEvidencePath.trim(), newDesc.trim());
      setShowCreate(false);
      setNewCaseId('');
      setNewEvidencePath('');
      setNewDesc('');
    } catch (err: any) {
      setError(err.message || 'Failed to create case');
    } finally {
      setLoading(false);
    }
  };

  const filteredCases = cases.filter((c) =>
    c.case_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, maxWidth: '400px' }}>
          <div style={{ position: 'relative', width: '100%' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '10px', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search forensic cases..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: '100%', paddingLeft: '36px' }}
            />
          </div>
        </div>

        <button onClick={() => setShowCreate(!showCreate)} className="btn btn-primary">
          <Plus size={16} />
          <span>{showCreate ? 'Cancel' : 'Register New Case'}</span>
        </button>
      </div>

      {/* Create Case Form Drawer */}
      {showCreate && (
        <div className="card" style={{ borderLeft: '4px solid var(--accent-cyan)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '14px', color: 'var(--text-primary)' }}>
            Register New Forensic Investigation Target
          </h3>
          {error && (
            <div style={{ color: 'var(--accent-red)', fontSize: '0.85rem', marginBottom: '12px' }}>
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr 1fr auto', gap: '12px', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Case ID
              </label>
              <input
                type="text"
                placeholder="e.g. INCIDENT-2026-ALPHA"
                value={newCaseId}
                onChange={(e) => setNewCaseId(e.target.value)}
                style={{ width: '100%' }}
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Evidence File / Directory Path
              </label>
              <input
                type="text"
                placeholder="e.g. /evidence/memdump.raw or sample_evidence"
                value={newEvidencePath}
                onChange={(e) => setNewEvidencePath(e.target.value)}
                style={{ width: '100%' }}
                required
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px', textTransform: 'uppercase' }}>
                Incident Notes (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Lateral movement suspicion"
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Creating...' : 'Initialize'}
            </button>
          </form>
        </div>
      )}

      {/* Case List Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Status</th>
              <th>Current Stage</th>
              <th>Integrity Baseline</th>
              <th>Artifact Items</th>
              <th>Verified Findings</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCases.map((c) => {
              const isActive = c.case_id === activeCaseId;
              return (
                <tr key={c.case_id} className="clickable" onClick={() => onSelectCase(c.case_id)}>
                  <td className="mono" style={{ fontWeight: 700, color: isActive ? 'var(--accent-cyan)' : 'var(--accent-blue)' }}>
                    {c.case_id} {isActive && <span className="badge badge-cyan" style={{ fontSize: '0.65rem', marginLeft: '6px' }}>ACTIVE</span>}
                  </td>
                  <td>
                    <span className={`badge ${c.status === 'COMPLETED' ? 'badge-verified' : (c.status === 'RUNNING' ? 'badge-cyan' : 'badge-amber')}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {c.current_stage}
                  </td>
                  <td>
                    <span className={`badge ${c.integrity_status === 'MATCH' || c.integrity_status === 'BASELINED' ? 'badge-verified' : 'badge-contradicted'}`}>
                      {c.integrity_status === 'MATCH' ? 'SHA256 INTACT' : (c.integrity_status || 'PENDING')}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-primary)' }}>
                    {c.evidence_items_count} files
                  </td>
                  <td style={{ color: 'var(--accent-green)', fontWeight: 700 }}>
                    {c.verified_findings_count} / {c.total_findings_count}
                  </td>
                  <td>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectCase(c.case_id);
                      }}
                      className="btn btn-secondary"
                      style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                    >
                      <span>Open Workspace</span>
                      <ArrowRight size={12} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

