import { Settings2, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUIStore } from '@/stores/uiStore';
import type { PortData } from '@/types';

export function PropertiesPanel() {
  const rightPanelOpen = useUIStore((s) => s.rightPanelOpen);
  const toggleRightPanel = useUIStore((s) => s.toggleRightPanel);

  return (
    <>
      <AnimatePresence>
        {rightPanelOpen && (
          <motion.aside
            initial={{ width: 0 }}
            animate={{ width: 280 }}
            exit={{ width: 0 }}
            className="flex-shrink-0 flex flex-col z-40 overflow-hidden"
            style={{ background: 'var(--panel-bg)', borderLeft: '1px solid var(--panel-border)' }}
          >
            <div
              className="h-10 flex items-center justify-between px-3 border-b"
              style={{ background: 'var(--canvas-bg)', borderColor: 'var(--panel-border)' }}
            >
              <div className="flex items-center gap-2 text-xs font-bold" style={{ color: 'var(--text-primary)' }}>
                <Settings2 size={14} />
                <span>PROPERTIES</span>
              </div>
              <button onClick={toggleRightPanel} className="text-gray-400 hover:text-gray-800">
                <ChevronRight size={16} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              <PropertiesContent />
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
      {!rightPanelOpen && (
        <button
          onClick={toggleRightPanel}
          className="absolute right-0 top-1/2 -translate-y-1/2 bg-white border border-r-0 border-gray-200 rounded-l-lg p-2 flex flex-col items-center gap-1 text-[10px] font-bold text-gray-500 shadow-lg hover:text-primary transition-all z-40"
          style={{ background: 'var(--panel-bg)', borderColor: 'var(--panel-border)' }}
        >
          <Settings2 size={16} />
          <div className="[writing-mode:vertical-lr]">PROPS</div>
        </button>
      )}
    </>
  );
}

function PropertiesContent() {
  const nodes = useCanvasStore((s) => s.nodes);
  const edges = useCanvasStore((s) => s.edges);
  const selectedNodeId = useCanvasStore((s) => s.selectedNodeId);
  const selectedEdgeId = useCanvasStore((s) => s.selectedEdgeId);
  const removeNode = useCanvasStore((s) => s.removeNode);

  if (selectedEdgeId) {
    const edge = edges.find((e) => e.id === selectedEdgeId);
    if (!edge) return <EmptyState />;
    return (
      <div className="p-4 space-y-3 text-xs">
        <h3 className="font-bold text-sm">Connection</h3>
        <Field label="Wire" value={(edge.data as Record<string, unknown> | undefined)?.wire_name as string || edge.id} />
        <Field label="Source" value={`${edge.source} / ${edge.sourceHandle}`} />
        <Field label="Target" value={`${edge.target} / ${edge.targetHandle}`} />
        <button
          className="w-full py-1.5 text-red-500 border border-red-300 rounded hover:bg-red-50 text-xs font-medium"
          onClick={() => {
            useCanvasStore.setState({
              edges: edges.filter((e) => e.id !== selectedEdgeId),
              selectedEdgeId: null,
            });
          }}
        >
          Delete Connection
        </button>
      </div>
    );
  }

  if (selectedNodeId) {
    const node = nodes.find((n) => n.id === selectedNodeId);
    if (!node) return <EmptyState />;
    const mod = node.data.module;
    const ports = (mod.ports || []) as PortData[];
    return (
      <div className="p-4 space-y-3 text-xs">
        <h3 className="font-bold text-sm break-all">{mod.instance_name || mod.name}</h3>
        <Field label="Module" value={mod.name} />
        <Field label="Type" value={mod.type} />
        <Field label="Position" value={`${Math.round(node.position.x)}, ${Math.round(node.position.y)}`} />

        <div>
          <h4 className="text-[10px] font-bold text-gray-400 uppercase mb-1">Ports ({ports.length})</h4>
          <div className="space-y-1">
            {ports.map((port) => (
              <div key={port.id || port.name} className="flex items-center gap-2 py-0.5">
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    port.direction === 'input' ? 'bg-green-500' :
                    port.direction === 'output' ? 'bg-red-500' : 'bg-yellow-500'
                  }`}
                />
                <span className="flex-1 font-medium">{port.name}</span>
                <span className="text-gray-400">{port.direction}</span>
                <span className="text-gray-400 font-mono">[{port.width - 1}:0]</span>
              </div>
            ))}
          </div>
        </div>

        {Object.keys(mod.config || {}).length > 0 && (
          <div>
            <h4 className="text-[10px] font-bold text-gray-400 uppercase mb-1">Config</h4>
            {Object.entries(mod.config).map(([k, v]) => (
              <Field key={k} label={k} value={String(v)} />
            ))}
          </div>
        )}

        <button
          className="w-full py-1.5 text-red-500 border border-red-300 rounded hover:bg-red-50 text-xs font-medium"
          onClick={() => removeNode(selectedNodeId)}
        >
          Delete Module
        </button>
      </div>
    );
  }

  return <EmptyState />;
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10px] text-gray-400 uppercase font-medium">{label}</div>
      <div className="text-xs break-all mt-0.5" style={{ color: 'var(--text-primary)' }}>{value}</div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-20 px-4">
      <Settings2 className="mx-auto text-gray-200 mb-2" size={40} />
      <p className="text-xs text-gray-400">Select a module or connection to edit properties</p>
    </div>
  );
}
