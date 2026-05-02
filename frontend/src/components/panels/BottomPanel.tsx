import Editor from '@monaco-editor/react';
import { useUIStore } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';
import { useSimulationStore } from '@/stores/simulationStore';
import type { BottomPanelTab } from '@/types';

export default function BottomPanel() {
  const bottomPanelOpen = useUIStore((s) => s.bottomPanelOpen);
  const bottomPanelTab = useUIStore((s) => s.bottomPanelTab);
  const setBottomPanelTab = useUIStore((s) => s.setBottomPanelTab);
  const toggleBottomPanel = useUIStore((s) => s.toggleBottomPanel);

  if (!bottomPanelOpen) return null;

  return (
    <div className="h-56 min-h-[100px] border-t border-[var(--border-primary)] bg-[var(--panel-bg)] flex flex-col">
      <div className="flex items-center bg-[var(--panel-header)] border-b border-[var(--border-primary)] px-1">
        <TabBtn active={bottomPanelTab === 'code'} icon="📝" label="代码" onClick={() => setBottomPanelTab('code')} />
        <TabBtn active={bottomPanelTab === 'log'} icon="📜" label="日志" onClick={() => setBottomPanelTab('log')} />
        <TabBtn active={bottomPanelTab === 'waveform'} icon="〰" label="波形" onClick={() => setBottomPanelTab('waveform')} />
        <div className="flex-1" />
        <span className="text-[10px] text-[var(--text-muted)] mr-1">{bottomPanelTab === 'code' ? 'Verilog' : ''}</span>
        <button
          className="px-2 py-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded-md text-xs transition-colors"
          onClick={toggleBottomPanel}
        >
          ✕
        </button>
      </div>
      <div className="flex-1 overflow-hidden">
        {bottomPanelTab === 'code' && <CodeTab />}
        {bottomPanelTab === 'log' && <LogTab />}
        {bottomPanelTab === 'waveform' && <WaveformTab />}
      </div>
    </div>
  );
}

function TabBtn({ active, icon, label, onClick }: { active: boolean; icon: string; label: string; onClick: () => void }) {
  return (
    <button
      className={`flex items-center gap-1 px-3 py-2 text-[11.5px] font-medium transition-all duration-150 border-b-[2.5px] ${
        active
          ? 'text-[var(--accent)] border-[var(--accent)] bg-[var(--accent-subtle)]'
          : 'text-[var(--text-muted)] border-transparent hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
      }`}
      onClick={onClick}
    >
      <span className="text-xs">{icon}</span>
      {label}
    </button>
  );
}

function CodeTab() {
  const code = useUIStore((s) => s.generatedCode);
  const setGeneratedCode = useUIStore((s) => s.setGeneratedCode);
  const theme = useUIStore((s) => s.theme);
  const nodeCount = useCanvasStore((s) => s.nodes.length);

  const displayCode = code || `// Verilog 代码将在此显示
// 当前画布有 ${nodeCount} 个模块
// 点击工具栏的 "Top" 或 "TB" 按钮生成代码
`;

  return (
    <Editor
      height="100%"
      defaultLanguage="verilog"
      language="verilog"
      theme={theme === 'dark' ? 'vs-dark' : 'vs'}
      value={displayCode}
      onChange={(v) => setGeneratedCode(v || '')}
      options={{
        fontSize: 13,
        fontFamily: "'Cascadia Code', 'Fira Code', 'JetBrains Mono', Consolas, monospace",
        minimap: { enabled: false },
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        tabSize: 2,
        renderWhitespace: 'selection',
        bracketPairColorization: { enabled: true },
        automaticLayout: true,
        padding: { top: 12 },
        glyphMargin: false,
        folding: true,
        lineDecorationsWidth: 8,
        lineNumbersMinChars: 4,
      }}
    />
  );
}

function LogTab() {
  const result = useSimulationStore((s) => s.result);
  const isRunning = useSimulationStore((s) => s.isRunning);

  return (
    <div className="h-full p-3 font-mono text-[12px] overflow-y-auto bg-[var(--bg-primary)]">
      {isRunning && (
        <div className="flex items-center gap-2 text-[var(--accent)] mb-2">
          <span className="inline-block w-3 h-3 rounded-full border-2 border-[var(--accent)] border-t-transparent animate-spin" />
          仿真运行中...
        </div>
      )}
      {!result && !isRunning && (
        <div className="flex flex-col items-center justify-center h-full text-[var(--text-muted)]">
          <span className="text-2xl mb-2 opacity-40">📜</span>
          <p className="font-medium">日志输出区域</p>
          <p className="text-[11px] mt-1">运行编译或仿真后在此查看输出</p>
        </div>
      )}
      {result?.errors && result.errors.length > 0 && (
        <div className="space-y-1 mb-2">
          <div className="font-semibold text-[var(--error)] flex items-center gap-1">
            <span>✕</span> 错误:
          </div>
          {result.errors.map((e, i) => (
            <pre key={i} className="whitespace-pre-wrap text-[var(--error)]/90 bg-[var(--error-bg)] p-2 rounded-md text-[11px]">{e}</pre>
          ))}
        </div>
      )}
      {result?.warnings && result.warnings.length > 0 && (
        <div className="space-y-1 mb-2">
          <div className="font-semibold text-[var(--warning)] flex items-center gap-1">
            <span>⚠</span> 警告:
          </div>
          {result.warnings.map((w, i) => (
            <pre key={i} className="whitespace-pre-wrap text-[var(--warning)]/90 bg-[var(--warning-bg)] p-2 rounded-md text-[11px]">{w}</pre>
          ))}
        </div>
      )}
      {result?.stdout && (
        <pre className="whitespace-pre-wrap text-[var(--text-primary)] mt-2 p-2 bg-[var(--bg-secondary)] rounded-md text-[11px]">{result.stdout}</pre>
      )}
      {result?.stderr && (
        <pre className="whitespace-pre-wrap text-[var(--error)]/90 mt-2">{result.stderr}</pre>
      )}
    </div>
  );
}

function WaveformTab() {
  const waveform = useSimulationStore((s) => s.waveform);

  if (!waveform) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-[var(--text-muted)]">
        <span className="text-2xl mb-2 opacity-40">〰</span>
        <p className="font-medium">波形查看器</p>
        <p className="text-[11px] mt-1">运行仿真并加载 VCD 文件后可在此查看波形</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-3 text-[12px]">
      <div className="flex items-center gap-3 text-[var(--text-muted)] mb-3 text-[11px]">
        <span className="flex items-center gap-1">
          <span className="font-semibold">总时间:</span> {waveform.total_time_ns} ns
        </span>
        <span className="flex items-center gap-1">
          <span className="font-semibold">时标:</span> {waveform.timescale}
        </span>
        <span className="flex items-center gap-1">
          <span className="font-semibold">信号数:</span> {waveform.signals.length}
        </span>
      </div>
      <table className="w-full border-collapse">
        <thead>
          <tr className="text-left text-[var(--text-muted)] text-[10px] uppercase tracking-wide">
            <th className="p-2 border-b border-[var(--border-primary)] font-semibold">信号名</th>
            <th className="p-2 border-b border-[var(--border-primary)] font-semibold">宽度</th>
            <th className="p-2 border-b border-[var(--border-primary)] font-semibold text-right">变化数</th>
          </tr>
        </thead>
        <tbody>
          {waveform.signals.map((sig) => (
            <tr key={sig.name} className="hover:bg-[var(--bg-hover)] transition-colors">
              <td className="p-2 font-mono font-medium">{sig.name}</td>
              <td className="p-2 text-[var(--text-secondary)]">{sig.width}</td>
              <td className="p-2 text-[var(--text-secondary)] text-right">{sig.changes.length}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
