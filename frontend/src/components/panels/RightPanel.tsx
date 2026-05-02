import { useUIStore } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';
import type { PortDirection } from '@/types';

const DIR_LABELS: Record<PortDirection, string> = {
  input: '输入',
  output: '输出',
  inout: '双向',
};

const TYPE_LABELS: Record<string, string> = {
  base: '基础模块',
  wrapped: '封装模块',
  board_ip: '板载IP',
};

const DIR_COLOR: Record<string, string> = {
  input: 'var(--port-input)',
  output: 'var(--port-output)',
  inout: 'var(--port-inout)',
};

export default function RightPanel() {
  const rightPanelOpen = useUIStore((s) => s.rightPanelOpen);
  const toggleRightPanel = useUIStore((s) => s.toggleRightPanel);

  if (!rightPanelOpen) return null;

  return (
    <div className="w-64 min-w-[220px] border-l border-[var(--border-primary)] bg-[var(--panel-bg)] flex flex-col animate-slide-in">
      <div className="flex items-center justify-between bg-[var(--panel-header)] border-b border-[var(--border-primary)] px-3 py-2">
        <span className="text-[12px] font-semibold text-[var(--text-primary)] flex items-center gap-1.5">
          <span className="text-xs">📋</span>
          属性
        </span>
        <button
          className="text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded-md px-1.5 py-0.5 text-xs transition-colors"
          onClick={toggleRightPanel}
        >
          ✕
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        <PropertyContent />
      </div>
    </div>
  );
}

function PropertyContent() {
  const nodes = useCanvasStore((s) => s.nodes);
  const edges = useCanvasStore((s) => s.edges);
  const selectedNodeId = useCanvasStore((s) => s.selectedNodeId);
  const selectedEdgeId = useCanvasStore((s) => s.selectedEdgeId);
  const removeModule = useCanvasStore((s) => s.removeModule);
  const removeConnection = useCanvasStore((s) => s.removeConnection);

  if (selectedEdgeId) {
    const edge = edges.find((e) => e.id === selectedEdgeId);
    if (!edge) return <EmptyState />;
    return (
      <div className="p-3 space-y-3 animate-fade-in">
        <div className="flex items-center gap-2">
          <span className="text-lg">🔗</span>
          <h3 className="text-[13px] font-bold">连线属性</h3>
        </div>
        <Field label="信号名" value={edge.data.wireName} />
        <Field label="源模块" value={edge.source} mono />
        <Field label="目标模块" value={edge.target} mono />
        <Field label="源端口" value={edge.sourceHandle} />
        <Field label="目标端口" value={edge.targetHandle} />
        <button
          className="w-full mt-3 py-1.5 text-[12px] font-medium text-[var(--error)] border border-[var(--error)]/40 rounded-lg hover:bg-[var(--error-bg)] transition-colors"
          onClick={() => { removeConnection(selectedEdgeId); }}
        >
          删除连线
        </button>
      </div>
    );
  }

  if (selectedNodeId) {
    const node = nodes.find((n) => n.id === selectedNodeId);
    if (!node) return <EmptyState />;
    const mod = node.data.module;
    const typeLabel = TYPE_LABELS[mod.type] || mod.type;
    return (
      <div className="p-3 space-y-3 animate-fade-in">
        <div>
          <h3 className="text-[14px] font-bold break-all text-[var(--text-primary)]">{mod.instance_name || mod.name}</h3>
          <span className="text-[11px] text-[var(--text-muted)]">{typeLabel}</span>
        </div>

        <div className="bg-[var(--bg-secondary)] rounded-lg p-2.5 space-y-1.5">
          <Field label="模块名" value={mod.name} />
          <Field label="坐标" value={`${Math.round(node.position.x)}, ${Math.round(node.position.y)}`} />
          <Field label="ID" value={mod.id} mono />
        </div>

        <div>
          <h4 className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-1.5">
            端口 ({mod.ports.length})
          </h4>
          <div className="space-y-0.5">
            {mod.ports.map((port) => (
              <div key={port.id} className="flex items-center gap-2 text-[11px] py-1 px-2 rounded-md hover:bg-[var(--bg-hover)] transition-colors">
                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{
                  background: DIR_COLOR[port.direction],
                  boxShadow: `0 0 4px ${DIR_COLOR[port.direction]}80`
                }} />
                <span className="flex-1 font-medium">{port.name}</span>
                <span className="text-[var(--text-muted)] text-[10px]">{DIR_LABELS[port.direction]}</span>
                <span className="text-[var(--text-muted)] font-mono text-[10px]">[{port.width - 1}:0]</span>
              </div>
            ))}
          </div>
        </div>

        {Object.keys(mod.config).length > 0 && (
          <div>
            <h4 className="text-[11px] font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-1.5">配置</h4>
            <div className="bg-[var(--bg-secondary)] rounded-lg p-2.5 space-y-1.5">
              {Object.entries(mod.config).map(([k, v]) => (
                <Field key={k} label={k} value={String(v)} />
              ))}
            </div>
          </div>
        )}

        <button
          className="w-full mt-2 py-1.5 text-[12px] font-medium text-[var(--error)] border border-[var(--error)]/40 rounded-lg hover:bg-[var(--error-bg)] transition-colors"
          onClick={() => removeModule(selectedNodeId)}
        >
          删除模块
        </button>
      </div>
    );
  }

  return <EmptyState />;
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <label className="text-[10px] text-[var(--text-muted)] block font-medium uppercase tracking-wide">{label}</label>
      <div className={`text-[12px] text-[var(--text-primary)] break-all mt-0.5 ${mono ? 'font-mono text-[11px]' : ''}`}>
        {value}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <span className="text-3xl mb-3 opacity-40">🎯</span>
      <p className="text-[var(--text-muted)] text-[12px] font-medium">未选中任何对象</p>
      <p className="text-[var(--text-muted)] text-[11px] mt-1">点击画布上的模块或连线查看属性</p>
    </div>
  );
}
