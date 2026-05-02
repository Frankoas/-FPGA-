import { useState, useRef } from 'react';
import { useUIStore } from '@/stores/uiStore';
import { useModuleLibraryStore } from '@/stores/moduleLibraryStore';
import { useCanvasStore } from '@/stores/canvasStore';
import type { Module, ModuleTemplate, LeftPanelTab } from '@/types';

function generateId(): string {
  return `mod_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

// Track position for staggered placement
let placeX = 200;
let placeY = 150;
const PLACE_STEP = 80;

function createModuleFromTemplate(tmpl: ModuleTemplate): Module {
  const pos = { x: placeX, y: placeY };
  placeY += PLACE_STEP;
  if (placeY > 600) { placeY = 150; placeX += 250; }
  if (placeX > 1200) { placeX = 200; }

  return {
    id: generateId(),
    name: tmpl.name,
    instance_name: `${tmpl.name}_inst`,
    type: tmpl.type,
    ports: tmpl.ports.map((p, i) => ({ ...p, id: `${tmpl.name}_port_${i}` })),
    position: [pos.x, pos.y],
    config: { ...tmpl.defaultConfig },
  };
}

const CATEGORY_ICONS: Record<string, string> = {
  gate: '⊿',
  combinational: '∑',
  sequential: '⏳',
  io: '⚡',
};

const TYPE_DOT: Record<string, string> = {
  base: 'var(--node-base)',
  wrapped: 'var(--node-wrapped)',
  board_ip: 'var(--node-board)',
};

export default function LeftPanel() {
  const leftPanelTab = useUIStore((s) => s.leftPanelTab);
  const setLeftPanelTab = useUIStore((s) => s.setLeftPanelTab);
  const leftPanelOpen = useUIStore((s) => s.leftPanelOpen);
  const toggleLeftPanel = useUIStore((s) => s.toggleLeftPanel);

  if (!leftPanelOpen) return null;

  return (
    <div className="w-60 min-w-[200px] border-r border-[var(--border-primary)] bg-[var(--panel-bg)] flex flex-col animate-slide-in">
      <PanelTabs active={leftPanelTab} onChange={setLeftPanelTab} onClose={toggleLeftPanel} />
      <div className="flex-1 overflow-hidden">
        {leftPanelTab === 'library' && <LibraryTab />}
        {leftPanelTab === 'signals' && <SignalsTab />}
        {leftPanelTab === 'files' && <FilesTab />}
      </div>
    </div>
  );
}

function PanelTabs({ active, onChange, onClose }: {
  active: LeftPanelTab;
  onChange: (t: LeftPanelTab) => void;
  onClose: () => void;
}) {
  const tabs: { id: LeftPanelTab; label: string; icon: string }[] = [
    { id: 'library', label: '模块库', icon: '📦' },
    { id: 'signals', label: '信号', icon: '📡' },
    { id: 'files', label: '文件', icon: '📁' },
  ];

  return (
    <div className="flex items-center bg-[var(--panel-header)] border-b border-[var(--border-primary)] px-1">
      {tabs.map((t) => (
        <button
          key={t.id}
          className={`flex-1 flex items-center justify-center gap-1 py-2 text-[11px] font-medium transition-all duration-150 ${
            active === t.id
              ? 'text-[var(--accent)] border-b-[2.5px] border-[var(--accent)] bg-[var(--accent-subtle)]'
              : 'text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] border-b-[2.5px] border-transparent'
          }`}
          onClick={() => onChange(t.id)}
        >
          <span className="text-xs">{t.icon}</span>
          {t.label}
        </button>
      ))}
      <button
        className="px-2 py-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded text-xs transition-colors ml-1"
        onClick={onClose}
        title="关闭面板"
      >
        ✕
      </button>
    </div>
  );
}

function LibraryTab() {
  const { templates, categories, searchQuery, setSearch, activeCategory, setCategory, getFiltered } = useModuleLibraryStore();
  const addModule = useCanvasStore((s) => s.addModule);
  const setStatus = useUIStore((s) => s.setStatus);
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  const toggleCollapse = (cat: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat); else next.add(cat);
      return next;
    });
  };

  const handleAddModule = (tmpl: ModuleTemplate) => {
    const mod = createModuleFromTemplate(tmpl);
    addModule(mod);
    setStatus(`已添加模块: ${mod.instance_name}`);
  };

  const filtered = getFiltered();

  // Group by category
  const grouped: Record<string, ModuleTemplate[]> = {};
  for (const t of filtered) {
    if (!grouped[t.category]) grouped[t.category] = [];
    grouped[t.category].push(t);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search */}
      <div className="p-2 pb-1">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索模块..."
            className="w-full pl-7 pr-2 py-1.5 text-[12px] rounded-lg border border-[var(--border-primary)] bg-[var(--bg-primary)] text-[var(--text-primary)] outline-none focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent-ring)] transition-all placeholder:text-[var(--text-muted)]"
          />
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-[var(--text-muted)] text-xs">🔍</span>
        </div>
      </div>

      {/* Category filter chips */}
      <div className="px-2 pb-2 flex flex-wrap gap-1">
        <button
          className={`px-2 py-0.5 text-[10px] rounded-full font-medium transition-all ${
            !activeCategory
              ? 'bg-[var(--accent)] text-white'
              : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
          }`}
          onClick={() => setCategory(null)}
        >
          全部
        </button>
        {Object.entries(categories).map(([key, label]) => (
          <button
            key={key}
            className={`px-2 py-0.5 text-[10px] rounded-full font-medium transition-all ${
              activeCategory === key
                ? 'bg-[var(--accent)] text-white'
                : 'bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
            }`}
            onClick={() => setCategory(activeCategory === key ? null : key)}
          >
            {CATEGORY_ICONS[key] || ''} {label}
          </button>
        ))}
      </div>

      {/* Module list */}
      <div className="flex-1 overflow-y-auto px-1.5 pb-2">
        {Object.entries(categories).map(([key, label]) => {
          const items = grouped[key];
          if (!items || items.length === 0) return null;
          const isCollapsed = collapsed.has(key);
          return (
            <div key={key} className="mb-1">
              <button
                className="w-full text-left px-2 py-1.5 text-[11px] font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] rounded-md uppercase flex items-center gap-1.5 transition-colors"
                onClick={() => toggleCollapse(key)}
              >
                <span className="text-[9px] transition-transform" style={{ transform: isCollapsed ? 'rotate(-90deg)' : 'rotate(0)' }}>
                  ▼
                </span>
                <span className="text-xs">{CATEGORY_ICONS[key] || '•'}</span>
                {label}
                <span className="text-[10px] text-[var(--text-muted)] ml-auto bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded-full">
                  {items.length}
                </span>
              </button>
              {!isCollapsed && (
                <div className="space-y-0.5 ml-2">
                  {items.map((tmpl) => (
                    <div
                      key={tmpl.name}
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData('application/module-template', JSON.stringify(tmpl));
                        e.dataTransfer.effectAllowed = 'copy';
                      }}
                      onClick={() => handleAddModule(tmpl)}
                      className="group w-full text-left px-2.5 py-2 text-[12px] rounded-lg border border-transparent hover:border-[var(--border-primary)] hover:bg-[var(--bg-hover)] active:bg-[var(--bg-active)] transition-all cursor-grab active:cursor-grabbing flex items-center gap-2.5"
                    >
                      <span
                        className="w-2.5 h-2.5 rounded-md flex-shrink-0 ring-1 ring-offset-1 ring-offset-[var(--panel-bg)]"
                        style={{
                          background: TYPE_DOT[tmpl.type] || 'var(--node-base)',
                          boxShadow: `0 0 6px ${TYPE_DOT[tmpl.type]}66`,
                        }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="text-[12px] font-medium truncate">{tmpl.name}</div>
                        <div className="text-[10px] text-[var(--text-muted)]">{tmpl.ports.length} 端口</div>
                      </div>
                      <span className="text-[var(--text-muted)] text-[10px] opacity-0 group-hover:opacity-100 transition-opacity">
                        ＋
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
        {Object.keys(grouped).length === 0 && (
          <div className="p-3 text-center text-[var(--text-muted)] text-[12px]">
            <p>未找到匹配的模块</p>
          </div>
        )}
      </div>
    </div>
  );
}

function SignalsTab() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <span className="text-3xl mb-3 opacity-40">📡</span>
      <p className="text-[var(--text-muted)] text-[12px] font-medium">暂无监测信号</p>
      <p className="text-[var(--text-muted)] text-[11px] mt-1">运行仿真后可在此查看信号列表</p>
    </div>
  );
}

function FilesTab() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-4">
      <span className="text-3xl mb-3 opacity-40">📁</span>
      <p className="text-[var(--text-muted)] text-[12px] font-medium">项目文件列表</p>
      <p className="text-[var(--text-muted)] text-[11px] mt-1">打开项目后可在此浏览文件</p>
    </div>
  );
}
