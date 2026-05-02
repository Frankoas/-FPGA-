import { useState, useRef, useEffect } from 'react';
import { useUIStore } from '@/stores/uiStore';
import { useProjectStore } from '@/stores/projectStore';
import { useCanvasStore } from '@/stores/canvasStore';

interface MenuItem {
  label: string;
  shortcut?: string;
  action?: () => void;
  divider?: boolean;
}

export default function MenuBar() {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const setStatus = useUIStore((s) => s.setStatus);
  const projectName = useProjectStore((s) => s.name);
  const clearCanvas = useCanvasStore((s) => s.clearCanvas);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpenMenu(null);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const menus: Record<string, MenuItem[]> = {
    '文件': [
      { label: '新建项目', shortcut: 'Ctrl+N', action: () => { useProjectStore.getState().newProject(); clearCanvas(); setStatus('新建项目'); } },
      { label: '打开项目', shortcut: 'Ctrl+O', action: () => setStatus('打开项目 - 功能开发中') },
      { label: '保存', shortcut: 'Ctrl+S', action: () => setStatus('保存 - 功能开发中') },
      { label: '另存为...', shortcut: 'Ctrl+Shift+S', action: () => setStatus('另存为 - 功能开发中') },
      { label: '', divider: true },
      { label: '导出 Verilog', shortcut: 'Ctrl+E', action: () => setStatus('导出 Verilog - 功能开发中') },
      { label: '', divider: true },
      { label: '退出', action: () => setStatus('退出') },
    ],
    '编辑': [
      { label: '撤销', shortcut: 'Ctrl+Z', action: () => setStatus('撤销') },
      { label: '重做', shortcut: 'Ctrl+Y', action: () => setStatus('重做') },
      { label: '', divider: true },
      { label: '删除选中', shortcut: 'Delete', action: () => setStatus('删除') },
      { label: '全选', shortcut: 'Ctrl+A', action: () => setStatus('全选') },
    ],
    '视图': [
      { label: '切换模块库', shortcut: 'Ctrl+B', action: () => useUIStore.getState().toggleLeftPanel() },
      { label: '切换属性面板', shortcut: 'Ctrl+Shift+P', action: () => useUIStore.getState().toggleRightPanel() },
      { label: '切换代码面板', shortcut: 'Ctrl+J', action: () => useUIStore.getState().toggleBottomPanel() },
      { label: '', divider: true },
      { label: '放大', shortcut: 'Ctrl+=', action: () => setStatus('放大') },
      { label: '缩小', shortcut: 'Ctrl+-', action: () => setStatus('缩小') },
      { label: '适应画布', shortcut: 'Ctrl+0', action: () => setStatus('适应画布') },
    ],
    '生成': [
      { label: '生成 Top 模块', shortcut: 'F5', action: () => setStatus('生成 Top 模块') },
      { label: '生成 Testbench', shortcut: 'F6', action: () => setStatus('生成 Testbench') },
      { label: '', divider: true },
      { label: '编译', shortcut: 'F7', action: () => setStatus('编译') },
      { label: '仿真', shortcut: 'F8', action: () => setStatus('仿真') },
    ],
    '帮助': [
      { label: '使用手册', action: () => setStatus('使用手册') },
      { label: '关于 FPGA 可视化编程工具', action: () => setStatus('关于 FPGA 可视化编程工具 v1.0') },
    ],
  };

  return (
    <div ref={menuRef} className="flex items-center h-8 bg-[var(--bg-secondary)] border-b border-[var(--border-primary)] select-none px-2 gap-0.5">
      {/* App icon */}
      <span className="text-sm mr-2">⚡</span>

      {Object.entries(menus).map(([name, items]) => (
        <div key={name} className="relative">
          <button
            className={`px-2.5 h-7 text-[12.5px] font-medium rounded-md transition-colors ${
              openMenu === name
                ? 'bg-[var(--bg-active)] text-[var(--text-primary)]'
                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
            }`}
            onMouseDown={() => setOpenMenu(openMenu === name ? null : name)}
            onMouseEnter={() => openMenu && setOpenMenu(name)}
          >
            {name}
          </button>
          {openMenu === name && (
            <div className="absolute top-full left-0 mt-1 min-w-[220px] bg-[var(--panel-bg)] border border-[var(--border-primary)] rounded-lg shadow-[var(--shadow-md)] z-50 py-1 animate-fade-in overflow-hidden">
              {items.map((item, i) =>
                item.divider ? (
                  <div key={i} className="h-px bg-[var(--border-primary)] my-1 mx-2" />
                ) : (
                  <button
                    key={i}
                    className="w-full text-left px-3 py-1.5 text-[12.5px] text-[var(--text-primary)] hover:bg-[var(--bg-hover)] flex justify-between items-center gap-6 transition-colors"
                    onClick={() => { item.action?.(); setOpenMenu(null); }}
                  >
                    <span>{item.label}</span>
                    {item.shortcut && (
                      <span className="text-[var(--text-muted)] text-[11px] font-mono">{item.shortcut}</span>
                    )}
                  </button>
                )
              )}
            </div>
          )}
        </div>
      ))}

      {/* Title bar */}
      <div className="flex-1 text-center text-[12px] text-[var(--text-muted)] font-medium">
        {projectName} — FPGA 可视化编程工具
      </div>

      {/* Window controls */}
      <div className="flex items-center gap-1">
        <span className="w-3 h-3 rounded-full bg-[var(--warning)]/60" />
        <span className="w-3 h-3 rounded-full bg-[var(--success)]/60" />
        <span className="w-3 h-3 rounded-full bg-[var(--error)]/60" />
      </div>
    </div>
  );
}
