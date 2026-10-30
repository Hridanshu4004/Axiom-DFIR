import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { FindingDrillDownModal } from './components/FindingDrillDownModal';

// Views
import { OverviewDashboard } from './views/OverviewDashboard';
import { CaseManagement } from './views/CaseManagement';
import { EvidenceExplorer } from './views/EvidenceExplorer';
import { InvestigationWorkspace } from './views/InvestigationWorkspace';
import { HypothesisLedger } from './views/HypothesisLedger';
import { FindingVerification } from './views/FindingVerification';
import { AttackGraph } from './views/AttackGraph';
import { InvestigationTimeline } from './views/InvestigationTimeline';
import { ModelObservatory } from './views/ModelObservatory';
import { InvestigationReports } from './views/InvestigationReports';

// Types & API
import {
  CaseSummary,
  EvidenceItem,
  Hypothesis,
  Finding,
  AtomicClaim,
  GraphData,
  TimelineEvent,
  ChainOfCustody,
  ModelObservatory as ModelObservatoryType,
  ConfigResponse,
} from './types';
import { api } from './api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [activeCaseId, setActiveCaseId] = useState<string>('CASE-DEMO-2026');
  const [activeCase, setActiveCase] = useState<CaseSummary | null>(null);

  // Forensic Subsystem Data
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([]);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [atomicClaims, setAtomicClaims] = useState<AtomicClaim[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [custody, setCustody] = useState<ChainOfCustody | null>(null);
  const [observatory, setObservatory] = useState<ModelObservatoryType | null>(null);
  const [config, setConfig] = useState<ConfigResponse | null>(null);

  // Modal & Loading States
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch initial config & cases
  const loadGlobalData = useCallback(async () => {
    try {
      const cfg = await api.getConfig();
      setConfig(cfg);
    } catch {
      setConfig({
        environment: 'demo',
        demo_mode: true,
        nebius_configured: false,
        nebius_endpoint: 'https://api.tokenfactory.nebius.com/v1/',
        fast_model: 'meta-llama/Meta-Llama-3.1-8B-Instruct',
        balanced_model: 'nvidia/nemotron-mini-4b-instruct',
        deep_model: 'nvidia/nemotron-4-340b-instruct',
      });
    }

    try {
      const obs = await api.getModelObservatory();
      setObservatory(obs);
    } catch {
      // Model observatory handles fallback defaults internally
    }

    try {
      const caseList = await api.getCases();
      if (caseList && caseList.length > 0) {
        setCases(caseList);
        if (!activeCaseId || !caseList.some((c) => c.case_id === activeCaseId)) {
          setActiveCaseId(caseList[0].case_id);
          setActiveCase(caseList[0]);
        } else {
          const found = caseList.find((c) => c.case_id === activeCaseId);
          if (found) setActiveCase(found);
        }
      } else {
        const defaultCase: CaseSummary = {
          case_id: 'CASE-DEMO-2026',
          status: 'IN_PROGRESS',
          current_stage: 'STAGE_08_CLAIM_VALIDATION',
          integrity_status: 'MATCH',
          evidence_items_count: 5,
          verified_findings_count: 8,
          total_findings_count: 10,
          updated_at: new Date().toISOString(),
        };
        setCases([defaultCase]);
        setActiveCase(defaultCase);
      }
    } catch {
      const defaultCase: CaseSummary = {
        case_id: 'CASE-DEMO-2026',
        status: 'IN_PROGRESS',
        current_stage: 'STAGE_08_CLAIM_VALIDATION',
        integrity_status: 'MATCH',
        evidence_items_count: 5,
        verified_findings_count: 8,
        total_findings_count: 10,
        updated_at: new Date().toISOString(),
      };
      setCases([defaultCase]);
      setActiveCase(defaultCase);
    }
  }, [activeCaseId]);

  // Fetch case-specific data
  const loadCaseData = useCallback(async (cId: string) => {
    if (!cId) return;
    setIsRefreshing(true);
    try {
      // Run queries concurrently
      const [evRes, hypRes, finRes, claimsRes, grpRes, timeRes, custRes] = await Promise.allSettled([
        api.getEvidence(cId),
        api.getHypotheses(cId),
        api.getFindings(cId),
        api.getAtomicClaims(cId),
        api.getGraph(cId),
        api.getTimeline(cId),
        api.getCustody(cId),
      ]);

      if (evRes.status === 'fulfilled' && evRes.value?.items) {
        setEvidenceItems(evRes.value.items);
      }
      if (hypRes.status === 'fulfilled' && Array.isArray(hypRes.value)) {
        setHypotheses(hypRes.value);
      }
      if (finRes.status === 'fulfilled' && Array.isArray(finRes.value)) {
        setFindings(finRes.value);
      }
      if (claimsRes.status === 'fulfilled' && Array.isArray(claimsRes.value)) {
        setAtomicClaims(claimsRes.value);
      }
      if (grpRes.status === 'fulfilled' && grpRes.value) {
        setGraphData(grpRes.value);
      }
      if (timeRes.status === 'fulfilled' && Array.isArray(timeRes.value)) {
        setTimeline(timeRes.value);
      }
      if (custRes.status === 'fulfilled' && custRes.value) {
        setCustody(custRes.value);
      }
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadGlobalData();
  }, [loadGlobalData]);

  useEffect(() => {
    if (activeCaseId) {
      loadCaseData(activeCaseId);
    }
  }, [activeCaseId, loadCaseData]);

  // Handle case creation
  const handleCreateCase = async (newId: string, evidencePath: string, desc: string) => {
    try {
      const created = await api.createCase({
        case_id: newId,
        evidence_path: evidencePath,
        description: desc,
      });
      setCases((prev) => [created, ...prev]);
      setActiveCaseId(created.case_id);
      setActiveCase(created);
    } catch {
      // Client-side fallback
      const fallback: CaseSummary = {
        case_id: newId,
        status: 'INITIALIZED',
        current_stage: 'STAGE_01_CASE_INITIALIZATION',
        integrity_status: 'BASELINED',
        evidence_items_count: 1,
        verified_findings_count: 0,
        total_findings_count: 0,
        updated_at: new Date().toISOString(),
      };
      setCases((prev) => [fallback, ...prev]);
      setActiveCaseId(fallback.case_id);
      setActiveCase(fallback);
    }
  };

  // Pipeline Execution Actions
  const handleStartFull = async () => {
    try {
      await api.startInvestigation(activeCaseId);
      await loadCaseData(activeCaseId);
      await loadGlobalData();
    } catch {
      // Advance stage optimistically in demo mode
      if (activeCase) {
        const updated = { ...activeCase, current_stage: 'STAGE_15_CASE_COMPLETION', status: 'COMPLETED' };
        setActiveCase(updated);
        setCases((prev) => prev.map((c) => (c.case_id === activeCaseId ? updated : c)));
      }
    }
  };

  const handleStepNext = async () => {
    try {
      await api.stepInvestigation(activeCaseId);
      await loadCaseData(activeCaseId);
      await loadGlobalData();
    } catch {
      // Step advancement
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', backgroundColor: 'var(--bg-primary)' }}>
      {/* 10-Tab Navigation Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        caseId={activeCaseId}
      />

      {/* Main Investigation Panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {/* Top Context Header */}
        <Header
          caseId={activeCaseId}
          stage={activeCase?.current_stage || 'STAGE_01_CASE_INITIALIZATION'}
          integrityStatus={activeCase?.integrity_status || 'MATCH'}
          nebiusConfigured={config?.nebius_configured ?? false}
          onRefresh={() => {
            loadGlobalData();
            loadCaseData(activeCaseId);
          }}
          isRefreshing={isRefreshing}
        />

        {/* View Viewport */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
          {currentTab === 'overview' && (
            <OverviewDashboard
              cases={cases}
              activeCase={activeCase}
              findings={findings}
              onSelectTab={setCurrentTab}
              nebiusConfigured={config?.nebius_configured ?? false}
            />
          )}

          {currentTab === 'cases' && (
            <CaseManagement
              cases={cases}
              activeCaseId={activeCaseId}
              onSelectCase={(id) => {
                setActiveCaseId(id);
                const found = cases.find((c) => c.case_id === id);
                if (found) setActiveCase(found);
              }}
              onCreateCase={handleCreateCase}
            />
          )}

          {currentTab === 'evidence' && (
            <EvidenceExplorer
              evidenceItems={evidenceItems}
              caseId={activeCaseId}
            />
          )}

          {currentTab === 'workspace' && (
            <InvestigationWorkspace
              caseId={activeCaseId}
              currentStage={activeCase?.current_stage || 'STAGE_01_CASE_INITIALIZATION'}
              status={activeCase?.status || 'INITIALIZED'}
              onStartFull={handleStartFull}
              onStepNext={handleStepNext}
            />
          )}

          {currentTab === 'hypotheses' && (
            <HypothesisLedger
              hypotheses={hypotheses}
            />
          )}

          {currentTab === 'findings' && (
            <FindingVerification
              findings={findings}
              atomicClaims={atomicClaims}
              onOpenFindingModal={(f) => setSelectedFinding(f)}
            />
          )}

          {currentTab === 'graph' && (
            <AttackGraph
              graphData={graphData}
              caseId={activeCaseId}
            />
          )}

          {currentTab === 'timeline' && (
            <InvestigationTimeline
              timeline={timeline}
              caseId={activeCaseId}
            />
          )}

          {currentTab === 'models' && (
            <ModelObservatory
              observatory={observatory}
              onRefresh={() => {
                api.getModelObservatory().then(setObservatory).catch(() => {});
              }}
            />
          )}

          {currentTab === 'reports' && (
            <InvestigationReports
              caseId={activeCaseId}
              custody={custody}
            />
          )}
        </main>
      </div>

      {/* Drill-down Modal for Evidence Verification */}
      <FindingDrillDownModal
        finding={selectedFinding}
        onClose={() => setSelectedFinding(null)}
      />
    </div>
  );
};

export default App;
