import { useUIStore } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';
import { useProjectStore } from '@/stores/projectStore';

export default function StatusBar() {
  const statusMessage = useUIStore((s) => s.statusMessage);
  const theme = useUIStore((s) => s.theme);
  const toggleTheme = useUIStore((s) => s.toggleTheme);
  const gridSnap = useUIStore((s) => s.gridSnap);
  const toggleGridSnap = useUIStore((s) => s.toggleGridSnap);
  const nodeCount = useCanvasStore((s) => s.nodes.length);
  const edgeCount = useCanvasStore((s) => s.edges.length);
  const isDirty = useProjectStore((s) => s.isDirty);

  return (
    <div className="flex items-center h-7 px-3 bg-[var(--statusbar-bg)] border-t border-[var(--border-primary)] text-[11px] text-[var(--text-secondary)] select-none gap-4">
      {/* Left: status */}
      <span className="flex-1 truncate flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full" style={{
          background: statusMessage.includes('失败') ? 'var(--error)' :
            statusMessage.includes('成功') || statusMessage.includes('✓') ? 'var(--success)' :
            'var(--text-muted)'
        }} />
        {statusMessage}
      </span>

      {/* Center: stats */}
      <div className="flex items-center gap-3 text-[var(--text-muted)]">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded" style={{ background: 'var(--node-base)' }} />
          模块 <strong className="text-[var(--text-secondary)]">{nodeCount}</strong>
        </span>
        <span className="flex items-center gap-1">
          <span className="text-[var(--text-muted)]">↔</span>
          连线 <strong className="text-[var(--text-secondary)]">{edgeCount}</strong>
        </span>
        {isDirty && (
          <span className="text-[var(--warning)] flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--warning)]" />
            已修改
          </span>
        )}
      </div>

      {/* Right: toggles */}
      <div className="flex items-center gap-1.5">
        <button
          className={`px-2 py-0.5 rounded-md text-[10px] font-medium transition-all duration-150 ${
            gridSnap
              ? 'bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--accent)]/30'
              : 'border border-[var(--border-primary)] text-[var(--text-muted)] hover:bg-[var(--bg-hover)]'
          }`}
          onClick={toggleGridSnap}
          title="切换网格吸附"
        >
          ⊞ 吸附{gridSnap ? ' ON' : ' OFF'}
        </button>

        <button
          className="px-2 py-0.5 rounded-md text-[10px] font-medium border border-[var(--border-primary)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] transition-all duration-150"
          onClick={toggleTheme}
          title="切换主题"
        >
          {theme === 'dark' ? '☀ 亮色' : '🌙 暗色'}
        </button>
      </div>
    </div>
  );
}
