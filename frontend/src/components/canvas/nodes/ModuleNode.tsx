import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import type { ModuleNodeData, Port as PortDef } from '@/types';

const TYPE_STYLES: Record<string, { accent: string; bg: string; text: string; badge: string }> = {
  base: {
    accent: 'var(--node-base)',
    bg: 'var(--node-base-bg)',
    text: 'var(--node-base-text)',
    badge: 'var(--node-base-badge)',
  },
  wrapped: {
    accent: 'var(--node-wrapped)',
    bg: 'var(--node-wrapped-bg)',
    text: 'var(--node-wrapped-text)',
    badge: 'var(--node-wrapped-badge)',
  },
  board_ip: {
    accent: 'var(--node-board)',
    bg: 'var(--node-board-bg)',
    text: 'var(--node-board-text)',
    badge: 'var(--node-board-badge)',
  },
};

const PORT_DIR_STYLE: Record<string, { color: string }> = {
  input: { color: 'var(--port-input)' },
  output: { color: 'var(--port-output)' },
  inout: { color: 'var(--port-inout)' },
};

const HEADER_H = 32;
const PORT_ROW_H = 24;
const FOOTER_H = 20;
const BODY_PAD_Y = 10;

function ModuleNode({ data, selected }: NodeProps) {
  const mod = (data as ModuleNodeData).module;
  const style = TYPE_STYLES[mod.type] || TYPE_STYLES.base;
  const inputs = mod.ports.filter((p: PortDef) => p.direction === 'input');
  const outputs = mod.ports.filter((p: PortDef) => p.direction === 'output' || p.direction === 'inout');
  const maxPorts = Math.max(inputs.length, outputs.length, 1);
  const bodyH = maxPorts * PORT_ROW_H + BODY_PAD_Y * 2;
  const nodeW = Math.max(160, mod.instance_name.length * 10 + 60);

  const handleTop = (idx: number) => HEADER_H + BODY_PAD_Y + idx * PORT_ROW_H + PORT_ROW_H / 2;

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{
        width: nodeW,
        background: 'var(--panel-bg)',
        border: `2px solid ${selected ? 'var(--accent)' : style.accent}`,
        boxShadow: selected
          ? '0 0 0 3px var(--accent-bg), 0 8px 24px rgba(0,0,0,0.18)'
          : '0 4px 12px rgba(0,0,0,0.10)',
        transition: 'box-shadow 0.2s, border-color 0.2s',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center gap-2 px-3"
        style={{
          height: HEADER_H,
          background: `linear-gradient(135deg, ${style.bg}, ${style.accent}22)`,
          borderBottom: `1px solid ${style.accent}33`,
        }}
      >
        <div className="flex items-center gap-1.5">
          <span
            className="w-2.5 h-2.5 rounded-md flex-shrink-0"
            style={{ background: style.accent }}
          />
          <span
            className="text-[13px] font-bold truncate select-none"
            style={{ color: style.text }}
          >
            {mod.instance_name || mod.name}
          </span>
        </div>
        <span
          className="ml-auto text-[9px] px-1.5 py-0.5 rounded-full font-medium select-none"
          style={{ background: style.badge, color: style.text }}
        >
          {mod.type === 'board_ip' ? 'IP' : mod.type}
        </span>
      </div>

      {/* Body - ports */}
      <div
        className="relative flex justify-between"
        style={{ minHeight: bodyH, padding: `${BODY_PAD_Y}px 0` }}
      >
        {/* Left handles (inputs) */}
        <div className="flex flex-col">
          {inputs.map((port: PortDef, i: number) => (
            <div
              key={port.id}
              className="flex items-center"
              style={{ height: PORT_ROW_H, position: 'relative' }}
            >
              <Handle
                type="target"
                position={Position.Left}
                id={port.id}
                style={{
                  position: 'absolute',
                  top: handleTop(i),
                  left: 0,
                  transform: 'translate(-50%, -50%)',
                  background: PORT_DIR_STYLE.input.color,
                  width: 10,
                  height: 10,
                  border: '2.5px solid var(--panel-bg)',
                  borderRadius: '50%',
                  zIndex: 10,
                }}
              />
              <span
                className="text-[11px] ml-3 text-[var(--text-secondary)] max-w-[70px] truncate select-none font-medium"
                title={`${port.name} [${port.width - 1}:0]`}
              >
                {port.name}
              </span>
            </div>
          ))}
        </div>

        {/* Right handles (outputs/inout) */}
        <div className="flex flex-col items-end">
          {outputs.map((port: PortDef, i: number) => (
            <div
              key={port.id}
              className="flex items-center justify-end"
              style={{ height: PORT_ROW_H, position: 'relative' }}
            >
              <span
                className="text-[11px] mr-3 text-[var(--text-secondary)] max-w-[70px] truncate select-none font-medium text-right"
                title={`${port.name} [${port.width - 1}:0]`}
              >
                {port.name}
              </span>
              <Handle
                type="source"
                position={Position.Right}
                id={port.id}
                style={{
                  position: 'absolute',
                  top: handleTop(i),
                  right: 0,
                  transform: 'translate(50%, -50%)',
                  background: PORT_DIR_STYLE[port.direction]?.color || 'var(--port-output)',
                  width: 10,
                  height: 10,
                  border: '2.5px solid var(--panel-bg)',
                  borderRadius: '50%',
                  zIndex: 10,
                }}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div
        className="flex items-center justify-center px-2"
        style={{
          height: FOOTER_H,
          background: `${style.accent}0D`,
          borderTop: `1px solid ${style.accent}1A`,
        }}
      >
        <span className="text-[9px] text-[var(--text-muted)] uppercase tracking-widest font-semibold select-none">
          {mod.name}
        </span>
      </div>
    </div>
  );
}

export default memo(ModuleNode);
