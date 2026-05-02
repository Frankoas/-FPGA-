import Editor from '@monaco-editor/react';
import { Terminal, FileJson, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useUIStore } from '@/stores/uiStore';
import { useSimulationStore } from '@/stores/simulationStore';

export function BottomPanel() {
  const bottomPanelOpen = useUIStore((s) => s.bottomPanelOpen);
  const bottomPanelTab = useUIStore((s) => s.bottomPanelTab);
  const setBottomPanelTab = useUIStore((s) => s.setBottomPanelTab);
  const toggleBottomPanel = useUIStore((s) => s.toggleBottomPanel);

  return (
    <>
      <AnimatePresence>
        {bottomPanelOpen && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 200 }}
            exit={{ height: 0 }}
            className="z-30 overflow-hidden flex flex-col"
            style={{ background: 'var(--panel-bg)', borderTop: '1px solid var(--panel-border)' }}
          >
            <div
              className="flex items-center justify-between px-4 h-8 border-b"
              style={{ background: 'var(--canvas-bg)', borderColor: 'var(--panel-border)' }}
            >
              <div className="flex items-center gap-4">
                <TabBtn
                  active={bottomPanelTab === 'log'}
                  icon={<Terminal size={12} />}
                  label="TERMINAL"
                  onClick={() => setBottomPanelTab('log')}
                />
                <TabBtn
                  active={bottomPanelTab === 'code'}
                  icon={<FileJson size={12} />}
                  label="CODE"
                  onClick={() => setBottomPanelTab('code')}
                />
                <TabBtn
                  active={bottomPanelTab === 'waveform'}
                  icon={<FileJson size={12} />}
                  label="WAVEFORM"
                  onClick={() => setBottomPanelTab('waveform')}
                />
              </div>
              <button onClick={toggleBottomPanel} className="text-gray-400 hover:text-gray-600">
                <ChevronDown size={14} />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              {bottomPanelTab === 'code' && <CodeTab />}
              {bottomPanelTab === 'log' && <LogTab />}
              {bottomPanelTab === 'waveform' && <WaveformTab />}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {!bottomPanelOpen && (
        <button
          onClick={toggleBottomPanel}
          className="absolute bottom-0 left-1/2 -translate-x-1/2 bg-white border border-b-0 border-gray-200 rounded-t-lg px-4 py-1 flex items-center gap-2 text-[10px] font-bold text-gray-500 shadow-lg hover:text-primary transition-all z-40"
          style={{ background: 'var(--panel-bg)', borderColor: 'var(--panel-border)' }}
        >
          <Terminal size={12} />
          CONSOLE
        </button>
      )}
    </>
  );
}

function TabBtn({ active, icon, label, onClick }: { active: boolean; icon: React.ReactNode; label: string; onClick: () => void }) {
  return (
    <button
      className={`text-[10px] font-bold flex items-center gap-1 h-8 px-1 border-b-2 transition-colors ${
        active ? 'text-primary border-primary' : 'text-gray-500 border-transparent hover:text-primary'
      }`}
      onClick={onClick}
    >
      {icon}
      {label}
    </button>
  );
}

function CodeTab() {
  const code = useUIStore((s) => s.generatedCode);
  const setGeneratedCode = useUIStore((s) => s.setGeneratedCode);
  const theme = useUIStore((s) => s.theme);

  return (
    <Editor
      height="100%"
      defaultLanguage="verilog"
      language="verilog"
      theme={theme === 'dark' ? 'vs-dark' : 'vs'}
      value={code || '// Click GENERATE in the toolbar to produce Verilog code'}
      onChange={(v) => setGeneratedCode(v || '')}
      options={{
        fontSize: 12,
        fontFamily: "'Cascadia Code', 'Fira Code', Consolas, monospace",
        minimap: { enabled: false },
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        tabSize: 2,
        automaticLayout: true,
        padding: { top: 8 },
      }}
    />
  );
}

function LogTab() {
  const result = useSimulationStore((s) => s.result);
  const isRunning = useSimulationStore((s) => s.isRunning);

  return (
    <div className="p-3 font-mono text-[11px] text-gray-600 h-[168px] overflow-y-auto" style={{ color: 'var(--text-secondary)', background: 'var(--canvas-bg)' }}>
      {isRunning && (
        <p className="text-blue-500 mb-1">[Simulation] Running...</p>
      )}
      {!result && !isRunning && (
        <>
          <p className="text-blue-500 mb-1">[Build] FPGA Visual Builder workspace ready.</p>
          <p className="text-gray-400 mb-1">-- Ready for generation and simulation --</p>
          <p className="animate-pulse">_</p>
        </>
      )}
      {result?.errors && result.errors.length > 0 && (
        <div className="space-y-1 mb-2">
          <p className="font-bold text-red-500">Errors:</p>
          {result.errors.map((e, i) => <pre key={i} className="text-red-400 whitespace-pre-wrap">{e}</pre>)}
        </div>
      )}
      {result?.warnings && result.warnings.length > 0 && (
        <div className="space-y-1 mb-2">
          <p className="font-bold text-yellow-500">Warnings:</p>
          {result.warnings.map((w, i) => <pre key={i} className="text-yellow-400 whitespace-pre-wrap">{w}</pre>)}
        </div>
      )}
      {result?.stdout && <pre className="whitespace-pre-wrap mt-2" style={{ color: 'var(--text-primary)' }}>{result.stdout}</pre>}
      {result?.stderr && <pre className="whitespace-pre-wrap text-red-400 mt-2">{result.stderr}</pre>}
    </div>
  );
}

function WaveformTab() {
  const waveform = useSimulationStore((s) => s.waveform);
  if (!waveform) {
    return (
      <div className="flex items-center justify-center h-full text-xs text-gray-400">
        Run simulation and load VCD to view waveform
      </div>
    );
  }
  return (
    <div className="h-full overflow-auto p-3 text-xs">
      <div className="text-gray-400 mb-2">
        Time: {waveform.total_time_ns}ns | Scale: {waveform.timescale} | Signals: {waveform.signals.length}
      </div>
      <table className="w-full border-collapse text-[11px]">
        <thead>
          <tr className="text-left text-gray-400">
            <th className="p-1 border-b" style={{ borderColor: 'var(--panel-border)' }}>Signal</th>
            <th className="p-1 border-b" style={{ borderColor: 'var(--panel-border)' }}>Width</th>
            <th className="p-1 border-b text-right" style={{ borderColor: 'var(--panel-border)' }}>Changes</th>
          </tr>
        </thead>
        <tbody>
          {waveform.signals.map((sig) => (
            <tr key={sig.name} className="hover:bg-gray-50">
              <td className="p-1 font-mono font-medium">{sig.name}</td>
              <td className="p-1 text-gray-500">{sig.width}</td>
              <td className="p-1 text-gray-500 text-right">{sig.changes.length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
