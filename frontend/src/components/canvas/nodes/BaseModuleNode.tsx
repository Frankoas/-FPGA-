import { memo } from 'react';
import { Handle, Position, type NodeProps, type Node } from '@xyflow/react';
import { Settings, Cpu, ChevronDown } from 'lucide-react';
import type { PortData } from '@/types';
import type { ModuleNodeData } from '@/stores/canvasStore';

const BaseModuleNode = memo(({ data, selected }: NodeProps<Node<ModuleNodeData>>) => {
  const mod = data.module;
  const ports = (mod.ports || []) as PortData[];
  const inputs = ports.filter((p) => p.direction === 'input');
  const outputs = ports.filter((p) => p.direction === 'output' || p.direction === 'inout');

  const headerBg = () => {
    switch (mod.type) {
      case 'wrapped': return 'bg-purple-700';
      case 'board_ip': return 'bg-orange-600';
      default: return 'bg-primary';
    }
  };

  return (
    <div
      className="min-w-[200px] rounded-md overflow-hidden"
      style={{
        background: 'var(--node-bg)',
        border: selected ? '2px solid var(--color-primary)' : '1px solid var(--node-border)',
        boxShadow: selected ? '0 0 0 2px rgba(26,86,219,0.2)' : '0 1px 3px rgba(0,0,0,0.1)',
      }}
    >
      {/* Header */}
      <div className={`${headerBg()} px-3 py-2 text-white flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          {mod.type === 'board_ip' ? <Cpu size={14} /> : <Settings size={14} />}
          <span className="text-xs font-bold leading-none">{mod.name}</span>
        </div>
        <ChevronDown size={12} className="opacity-70" />
      </div>

      {/* Instance Name */}
      <div className="px-3 py-1 border-b" style={{ background: 'var(--canvas-bg)', borderColor: 'var(--panel-border)' }}>
        <span className="text-[10px] font-mono italic" style={{ color: 'var(--text-secondary)' }}>
          u_{mod.instance_name || mod.name}
        </span>
      </div>

      {/* Ports */}
      <div className="px-2 py-2 flex justify-between gap-6">
        {/* Inputs */}
        <div className="flex flex-col gap-2">
          {inputs.map((port) => (
            <div key={port.id || port.name} className="relative flex items-center gap-1 group">
              <Handle
                type="target"
                position={Position.Left}
                id={port.id || port.name}
                className="!bg-gray-400 group-hover:!bg-primary"
              />
              <span className="text-[10px] ml-1" style={{ color: 'var(--text-secondary)' }}>
                {port.name}
              </span>
            </div>
          ))}
        </div>

        {/* Outputs */}
        <div className="flex flex-col gap-2 items-end">
          {outputs.map((port) => (
            <div key={port.id || port.name} className="relative flex items-center gap-1 group">
              <span className="text-[10px] mr-1" style={{ color: 'var(--text-secondary)' }}>
                {port.name}
              </span>
              <Handle
                type="source"
                position={Position.Right}
                id={port.id || port.name}
                className="!bg-primary group-hover:!bg-primary-light"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

BaseModuleNode.displayName = 'BaseModuleNode';
export { BaseModuleNode };
