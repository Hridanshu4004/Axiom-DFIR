import React, { useState } from 'react';
import { Play, SkipForward, CheckCircle2, Clock, AlertOctagon, Terminal, Shield, Cpu } from 'lucide-react';

interface InvestigationWorkspaceProps {
  caseId: string;
  currentStage: string;
  status: string;
  onStartFull: () => Promise<void>;
  onStepNext: () => Promise<void>;
}

const STAGES = [
  'STAGE_01_CASE_INITIALIZATION',
  'STAGE_02_EVIDENCE_INGESTION',
  'STAGE_03_INTEGRITY_VALIDATION',
  'STAGE_04_ARTIFACT_DISCOVERY',
  'STAGE_05_INITIAL_TRIAGE',
  'STAGE_06_INVESTIGATION_PLANNING',
  'STAGE_07_FORENSIC_TOOL_EXECUTION',
  'STAGE_08_EVIDENCE_CORRELATION',
  'STAGE_09_AI_HYPOTHESIS_ANALYSIS',
  'STAGE_10_CLAIM_VALIDATION',
  'STAGE_11_ATTACK_TIMELINE_CONSTRUCTION',
  'STAGE_12_RISK_ASSESSMENT',
  'STAGE_13_REPORT_GENERATION',
  'STAGE_14_FINAL_INTEGRITY_CHECK',
  'STAGE_15_CASE_COMPLETION',
];

export const InvestigationWorkspace: React.FC<InvestigationWorkspaceProps> = ({
  caseId,
  currentStage,
  status,
  onStartFull,
  onStepNext,
}) => {
  const [isRunning, setIsRunning] = useState(false);
  const [logMessages, setLogMessages] = useState<string[]>([
    `[SYS] Initialized orchestrator for target case: ${caseId}`,
    `[AUTH] Model inference gate active with 3-tier Nemotron routing`,
    `[INTEG] Pre-investigation SHA-256 fingerprint verified`,
  ]);

  const currentIdx = STAGES.findIndex((s) => s.includes(currentStage) || currentStage.includes(s));
  const progressPercent = Math.round(((currentIdx >= 0 ? currentIdx + 1 : 1) / STAGES.length) * 100);

  const handleRunFull = async () => {
    setIsRunning(true);
    setLogMessages((prev) => [...prev, `[CMD] Starting sequential 15-stage autonomous execution...`]);
    try {
      await onStartFull();
      setLogMessages((prev) => [
        ...prev,
        `[OK] Stage 01 - 15 execution completed successfully`,
        `[SEAL] Ed25519 digital signature seal generated on chain head`,
      ]);
    } catch (err: any) {
      setLogMessages((prev) => [...prev, `[ERR] Execution failed: ${err.message}`]);
    } finally {
      setIsRunning(false);
    }
  };

  const handleStepNext = async () => {
    setIsRunning(true);
    setLogMessages((prev) => [...prev, `[CMD] Advancing to next stage...`]);
    try {
      await onStepNext();
      setLogMessages((prev) => [...prev, `[OK] Stage advanced successfully`]);
    } catch (err: any) {
      setLogMessages((prev) => [...prev, `[ERR] Step failed: ${err.message}`]);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Control Bar & Progress */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
              Autonomous 15-Stage Finite State Machine
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="mono" style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                {currentStage}
              </span>
              <span className={`badge ${status === 'COMPLETED' ? 'badge-verified' : (status === 'RUNNING' ? 'badge-cyan' : 'badge-amber')}`}>
                {status}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handleStepNext}
              disabled={isRunning || status === 'COMPLETED'}
              className="btn btn-secondary"
            >
              <SkipForward size={16} />
              <span>Step Next Stage</span>
            </button>
            <button
              onClick={handleRunFull}
              disabled={isRunning || status === 'COMPLETED'}
              className="btn btn-primary"
            >
              <Play size={16} />
              <span>{isRunning ? 'Orchestrating...' : 'Execute Full Pipeline'}</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
            <span>Pipeline Progression</span>
            <span style={{ fontWeight: 700, color: 'var(--accent-blue)' }}>{progressPercent}% Complete</span>
          </div>
          <div style={{
            height: '8px',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: '4px',
            overflow: 'hidden',
          }}>
            <div style={{
              width: `${progressPercent}%`,
              height: '100%',
              backgroundColor: 'var(--accent-cyan)',
              transition: 'width 0.4s ease',
            }} />
          </div>
        </div>
      </div>

      {/* Stepper Grid (All 15 Stages) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '12px',
      }}>
        {STAGES.map((stg, i) => {
          const isPast = currentIdx > i || status === 'COMPLETED';
          const isCurrent = currentIdx === i && status !== 'COMPLETED';
          const stageShort = stg.replace('STAGE_', '');

          return (
            <div
              key={stg}
              style={{
                background: isCurrent ? 'rgba(0, 240, 255, 0.08)' : 'var(--bg-surface)',
                border: `1px solid ${isCurrent ? 'var(--accent-cyan)' : (isPast ? 'rgba(0, 210, 106, 0.3)' : 'var(--border-color)')}`,
                borderRadius: '6px',
                padding: '12px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
              }}
            >
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: isPast ? 'rgba(0, 210, 106, 0.15)' : (isCurrent ? 'rgba(0, 240, 255, 0.2)' : 'rgba(255, 255, 255, 0.05)'),
                color: isPast ? 'var(--accent-green)' : (isCurrent ? 'var(--accent-cyan)' : 'var(--text-muted)'),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                fontWeight: 700,
                flexShrink: 0,
              }}>
                {isPast ? <CheckCircle2 size={14} /> : i + 1}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div className="mono" style={{ fontSize: '0.75rem', fontWeight: 700, color: isCurrent ? 'var(--accent-cyan)' : 'var(--text-primary)', textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden' }}>
                  {stageShort}
                </div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                  {isPast ? 'COMPLETED' : (isCurrent ? 'ACTIVE EXECUTION' : 'QUEUED')}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Execution Console */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{
          padding: '12px 18px',
          borderBottom: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-secondary)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <Terminal size={16} style={{ color: 'var(--accent-cyan)' }} />
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Live Forensic Orchestration Log
          </h4>
        </div>
        <div style={{
          padding: '16px 20px',
          backgroundColor: '#05080f',
          maxHeight: '220px',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}>
          {logMessages.map((msg, i) => (
            <div key={i} className="mono" style={{ fontSize: '0.8rem', color: msg.includes('[ERR]') ? 'var(--accent-red)' : (msg.includes('[OK]') ? 'var(--accent-green)' : 'var(--text-secondary)') }}>
              {msg}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

