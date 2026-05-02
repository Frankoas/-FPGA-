import { useUIStore } from '@/stores/uiStore';
import { useCanvasStore } from '@/stores/canvasStore';
import { useProjectStore } from '@/stores/projectStore';
import { api } from '@/services/api';

function ToolBtn({ icon, label, title, onClick, accent, highlight }: {
  icon: string;
  label: string;
  title: string;
  onClick: () => void;
  accent?: boolean;
  highlight?: boolean;
}) {
  return (
    <button
      title={title}
      onClick={onClick}
      className={`flex items-center gap-1.5 px-2.5 py-1 text-[12px] rounded-md font-medium transition-all duration-150 active:scale-95
        ${highlight
          ? 'bg-[var(--accent)] text-white shadow-[var(--shadow-glow)] hover:bg-[var(--accent-hover)] border border-[var(--accent)]'
          : accent
            ? 'bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--accent)]/30 hover:bg-[var(--accent)]/20'
            : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] border border-transparent hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
        }`}
    >
      <span className="text-sm">{icon}</span>
      <span className="hidden xl:inline">{label}</span>
    </button>
  );
}

function Separator() {
  return <div className="w-px h-5 bg-[var(--border-primary)]" />;
}

export default function Toolbar() {
  const setStatus = useUIStore((s) => s.setStatus);
  const setGeneratedCode = useUIStore((s) => s.setGeneratedCode);
  const setBottomPanelTab = useUIStore((s) => s.setBottomPanelTab);
  const clearCanvas = useCanvasStore((s) => s.clearCanvas);
  const buildIR = useCanvasStore((s) => s.buildIR);
  const setIR = useProjectStore((s) => s.setIR);
  const simulation = useProjectStore((s) => s.simulation);

  const handleNew = () => {
    clearCanvas();
    useProjectStore.getState().newProject();
    setStatus('新建项目');
  };

  const handleGenerateTop = async () => {
    const ir = buildIR('top_module');
    setIR(ir);
    setStatus('正在生成 Top 模块...');
    try {
      const result = await api.generateTop(ir);
      if (result.success) {
        setGeneratedCode(result.verilog);
        setBottomPanelTab('code');
        setStatus('Top 模块生成成功 ✓');
      }
    } catch (e) {
      setStatus(`生成失败: ${(e as Error).message}`);
    }
  };

  const handleGenerateTB = async () => {
    const ir = buildIR('top_module');
    setIR(ir);
    if (!simulation) return;
    setStatus('正在生成 Testbench...');
    try {
      const result = await api.generateTestbench(ir, simulation);
      if (result.success) {
        setGeneratedCode(result.verilog);
        setBottomPanelTab('code');
        setStatus('Testbench 生成成功 ✓');
      }
    } catch (e) {
      setStatus(`生成失败: ${(e as Error).message}`);
    }
  };

  return (
    <div className="flex items-center gap-1 h-9 px-2.5 bg-[var(--bg-secondary)] border-b border-[var(--border-primary)]">
      {/* File ops */}
      <ToolBtn icon="📄" label="新建" title="新建项目 (Ctrl+N)" onClick={handleNew} />
      <ToolBtn icon="📂" label="打开" title="打开项目" onClick={() => setStatus('打开项目 - 功能开发中')} />
      <ToolBtn icon="💾" label="保存" title="保存项目 (Ctrl+S)" onClick={() => setStatus('保存 - 功能开发中')} />

      <Separator />

      {/* Undo/Redo */}
      <ToolBtn icon="↩" label="撤销" title="撤销 (Ctrl+Z)" onClick={() => setStatus('撤销')} />
      <ToolBtn icon="↪" label="重做" title="重做 (Ctrl+Y)" onClick={() => setStatus('重做')} />

      <Separator />

      {/* Generate */}
      <ToolBtn icon="⚙" label="Top" title="生成顶层模块 (F5)" onClick={handleGenerateTop} accent />
      <ToolBtn icon="🧪" label="TB" title="生成 Testbench (F6)" onClick={handleGenerateTB} accent />
      <ToolBtn icon="▶" label="编译" title="编译 (F7)" onClick={() => setStatus('编译 - 功能开发中')} highlight />
      <ToolBtn icon="⚡" label="仿真" title="运行仿真 (F8)" onClick={() => setStatus('仿真 - 功能开发中')} highlight />

      <Separator />

      <ToolBtn icon="📋" label="解析" title="解析 Verilog 文件" onClick={() => setStatus('解析 - 功能开发中')} />

      <div className="flex-1" />
    </div>
  );
}
