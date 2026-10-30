import React from 'react';
import {
  LayoutDashboard,
  FolderLock,
  HardDrive,
  Cpu,
  GitBranch,
  ShieldAlert,
  Network,
  Clock,
  Sparkles,
  FileText,
  ShieldCheck,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  caseId: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, caseId }) => {
  const navItems = [
    { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
    { id: 'cases', label: 'Case Management', icon: FolderLock },
    { id: 'evidence', label: 'Evidence Explorer', icon: HardDrive },
    { id: 'workspace', label: 'Investigation Workspace', icon: Cpu },
    { id: 'hypotheses', label: 'Hypothesis Ledger', icon: GitBranch },
    { id: 'findings', label: 'Finding Verification', icon: ShieldAlert },
    { id: 'graph', label: 'Attack Relationship Graph', icon: Network },
    { id: 'timeline', label: 'Investigation Timeline', icon: Clock },
    { id: 'models', label: 'Model Observatory', icon: Sparkles },
    { id: 'reports', label: 'Investigation Reports', icon: FileText },
  ];

  return (
    <aside style={{
      width: '260px',
      height: '100vh',
      backgroundColor: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px 20px',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'rgba(0, 240, 255, 0.1)',
          border: '1px solid var(--accent-cyan)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--accent-cyan)',
        }}>
          <ShieldCheck size={22} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.05rem', fontWeight: 800, letterSpacing: '0.05em', color: 'var(--text-primary)' }}>
            AXIOM <span style={{ color: 'var(--accent-cyan)' }}>DFIR</span>
          </h1>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Autonomous Forensic AI
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <li key={item.id}>
                <button
                  onClick={() => onSelectTab(item.id)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '10px 14px',
                    borderRadius: '6px',
                    fontSize: '0.86rem',
                    fontWeight: isActive ? 700 : 500,
                    color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                    backgroundColor: isActive ? 'rgba(0, 240, 255, 0.08)' : 'transparent',
                    border: isActive ? '1px solid rgba(0, 240, 255, 0.3)' : '1px solid transparent',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)';
                      e.currentTarget.style.color = 'var(--text-primary)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--text-secondary)';
                    }
                  }}
                >
                  <Icon size={18} style={{ color: isActive ? 'var(--accent-cyan)' : 'var(--text-muted)' }} />
                  <span>{item.label}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Active Case Footer Badge */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid var(--border-color)',
        backgroundColor: 'rgba(0, 0, 0, 0.2)',
      }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
          Active Case Target
        </div>
        <div className="mono" style={{ fontSize: '0.82rem', color: 'var(--accent-blue)', fontWeight: 600 }}>
          {caseId || 'CASE-DEMO-2026'}
        </div>
      </div>
    </aside>
  );
};

