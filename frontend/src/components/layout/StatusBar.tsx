import { useUIStore } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';
import { useProjectStore } from '@/stores/projectStore';

export function StatusBar() {
  const statusMessage = useUIStore((s) => s.statusMessage);
  const theme = useUIStore((s) => s.theme);
  const toggleTheme = useUIStore((s) => s.toggleTheme);
  const gridSnap = useUIStore((s) => s.gridSnap);
  const toggleGridSnap = useUIStore((s) => s.toggleGridSnap);
  const nodeCount = useCanvasStore((s) => s.nodes.length);
  const edgeCount = useCanvasStore((s) => s.edges.length);
  const projectName = useProjectStore((s) => s.name);
  const isDirty = useProjectStore((s) => s.isDirty);

  return (
    <footer
      className="h-6 flex items-center justify-between px-3 text-[10px] z-50 flex-shrink-0"
      style={{ background: 'var(--canvas-bg)', borderTop: '1px solid var(--panel-border)', color: 'var(--text-secondary)' }}
    >
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 text-green-600">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
          <span>{statusMessage}</span>
        </div>
        <span>IR v1.0</span>
      </div>
      <div className="flex items-center gap-4">
        <span>Nodes: {nodeCount} | Edges: {edgeCount}</span>
        {isDirty && <span className="text-amber-500">● Modified</span>}
        <span>Project: {projectName}</span>
        <button
          className={`px-1.5 rounded text-[9px] font-medium transition-colors ${
            gridSnap ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={toggleGridSnap}
          title="Toggle grid snap"
        >
          SNAP
        </button>
        <button
          className="px-1.5 rounded text-[9px] font-medium transition-colors hover:text-primary"
          onClick={toggleTheme}
          title="Toggle theme"
        >
          {theme === 'dark' ? 'LIGHT' : 'DARK'}
        </button>
      </div>
    </footer>
  );
}
