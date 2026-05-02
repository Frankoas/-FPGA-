import { Search, Folder, Box } from 'lucide-react';
import { motion } from 'motion/react';
import { useModuleLibraryStore } from '@/stores/moduleLibraryStore';
import { useCanvasStore, type ModuleNodeData } from '@/stores/canvasStore';
import { useUIStore } from '@/stores/uiStore';
import type { ModuleTemplate, ModuleData } from '@/types';
import type { Node } from '@xyflow/react';

const CAT_ICONS: Record<string, string> = {
  gate: '⊿',
  combinational: '∑',
  sequential: '⏳',
  io: '⚡',
};

const TYPE_DOT: Record<string, string> = {
  base: 'bg-primary',
  wrapped: 'bg-purple-500',
  board_ip: 'bg-orange-500',
};

export function ModuleLibrary() {
  const { categories, searchQuery, setSearch, activeCategory, setCategory, getFiltered } = useModuleLibraryStore();
  const addNode = useCanvasStore((s) => s.addNode);
  const setStatus = useUIStore((s) => s.setStatus);

  const onDragStart = (event: React.DragEvent, tmpl: ModuleTemplate) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify(tmpl));
    event.dataTransfer.effectAllowed = 'move';
  };

  const onClickAdd = (tmpl: ModuleTemplate) => {
    const id = `mod_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
    const newNode: Node<ModuleNodeData> = {
      id,
      type: tmpl.type,
      position: { x: 100 + Math.random() * 400, y: 100 + Math.random() * 300 },
      data: {
        module: {
          id,
          name: tmpl.name,
          instance_name: `${tmpl.name}_inst`,
          type: tmpl.type,
          ports: tmpl.ports.map((p, i) => ({ ...p, id: `${tmpl.name}_p${i}` })),
          config: { ...tmpl.defaultConfig },
        } as ModuleData,
      },
    };
    addNode(newNode);
    setStatus(`Added: ${tmpl.name}`);
  };

  const filtered = getFiltered();
  const grouped: Record<string, ModuleTemplate[]> = {};
  for (const t of filtered) {
    if (!grouped[t.category]) grouped[t.category] = [];
    grouped[t.category].push(t);
  }

  return (
    <div className="flex flex-col h-full" style={{ background: 'var(--panel-bg)', borderRight: '1px solid var(--panel-border)' }}>
      <div className="p-4 border-b" style={{ borderColor: 'var(--panel-border)' }}>
        <h2 className="text-sm font-bold text-gray-800 mb-3 uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
          Module Library
        </h2>
        <div className="relative">
          <Search className="absolute left-2 top-2.5 text-gray-400" size={14} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search modules..."
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-primary"
            style={{ color: 'var(--text-primary)', background: 'var(--canvas-bg)', borderColor: 'var(--panel-border)' }}
          />
        </div>
        {/* Category filter chips */}
        <div className="flex flex-wrap gap-1 mt-2">
          <button
            className={`px-2 py-0.5 text-[10px] rounded-full font-medium transition-colors ${
              !activeCategory ? 'bg-primary text-white' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
            onClick={() => setCategory(null)}
          >
            All
          </button>
          {Object.entries(categories).map(([key, label]) => (
            <button
              key={key}
              className={`px-2 py-0.5 text-[10px] rounded-full font-medium transition-colors ${
                activeCategory === key ? 'bg-primary text-white' : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
              onClick={() => setCategory(activeCategory === key ? null : key)}
            >
              {CAT_ICONS[key] || ''} {label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {Object.entries(categories).map(([catKey, catLabel]) => {
          const items = grouped[catKey];
          if (!items || items.length === 0) return null;
          return (
            <div key={catKey}>
              <div className="flex items-center gap-1.5 text-[10px] font-bold text-gray-400 uppercase mb-2">
                <Folder size={10} />
                <span>{catLabel}</span>
              </div>
              <div className="space-y-2">
                {items.map((tmpl) => (
                  <motion.div
                    key={tmpl.name}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="p-2 border border-blue-50 bg-blue-50/30 rounded-md hover:border-primary-light transition-colors group"
                  >
                    <div
                      draggable
                      onDragStart={(e) => onDragStart(e, tmpl)}
                      onClick={() => onClickAdd(tmpl)}
                      className="flex items-center gap-2 cursor-grab active:cursor-grabbing"
                    >
                      <div className={`w-2 h-2 rounded-full ${TYPE_DOT[tmpl.type] || 'bg-primary'}`} />
                      <Box size={14} className="text-primary-light" />
                      <span className="text-xs font-medium text-gray-700 group-hover:text-primary">{tmpl.name}</span>
                      <span className="ml-auto text-[9px] text-gray-400">{tmpl.ports.length}p</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          );
        })}
        {Object.keys(grouped).length === 0 && (
          <div className="text-center text-xs text-gray-400 py-8">No modules found</div>
        )}
      </div>
    </div>
  );
}
