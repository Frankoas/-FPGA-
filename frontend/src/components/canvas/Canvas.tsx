import { useCallback } from 'react';
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  useReactFlow,
  ReactFlowProvider,
  type Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCanvasStore, type ModuleNodeData } from '@/stores/canvasStore';
import { useUIStore } from '@/stores/uiStore';
import { BaseModuleNode } from './nodes/BaseModuleNode';
import type { ModuleData } from '@/types';

const nodeTypes = {
  base: BaseModuleNode,
  wrapped: BaseModuleNode,
  board_ip: BaseModuleNode,
};

const defaultEdgeOptions = {
  type: 'smoothstep' as const,
  animated: true,
  style: { stroke: '#1a56db', strokeWidth: 2 },
};

function CanvasInner() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
  } = useCanvasStore();
  const { screenToFlowPosition } = useReactFlow();
  const gridSnap = useUIStore((s) => s.gridSnap);
  const setStatus = useUIStore((s) => s.setStatus);

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const moduleDataStr = event.dataTransfer.getData('application/reactflow');
      if (!moduleDataStr) return;

      try {
        const template = JSON.parse(moduleDataStr);
        const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });

        const id = `mod_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
        const newNode: Node<ModuleNodeData> = {
          id,
          type: template.type,
          position: { x: Math.round(position.x), y: Math.round(position.y) },
          data: {
            module: {
              id,
              name: template.name,
              instance_name: `${template.name}_inst`,
              type: template.type,
              ports: template.ports.map((p: Record<string, unknown>, idx: number) => ({
                ...p,
                id: `${template.name}_p${idx}`,
              })),
              config: { ...(template.defaultConfig || {}) },
            } as ModuleData,
          },
        };
        addNode(newNode);
        setStatus(`Placed: ${template.name}`);
      } catch (err) {
        console.error('Drop failed:', err);
        setStatus('Drop failed — check console');
      }
    },
    [screenToFlowPosition, addNode, setStatus]
  );

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDragOver={onDragOver}
        onDrop={onDrop}
        nodeTypes={nodeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        snapToGrid={gridSnap}
        snapGrid={[20, 20]}
        fitView
        deleteKeyCode={['Delete', 'Backspace']}
        multiSelectionKeyCode="Shift"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="var(--canvas-dot)" />
        <Controls />
        <MiniMap
          zoomable
          pannable
          position="bottom-right"
          nodeColor={(n) => {
            const d = n.data as ModuleNodeData | undefined;
            const type = d?.module?.type;
            if (type === 'wrapped') return '#7c3aed';
            if (type === 'board_ip') return '#ea580c';
            return '#1a56db';
          }}
          maskColor="rgba(0,0,0,0.4)"
        />
      </ReactFlow>
    </div>
  );
}

export function Canvas() {
  return (
    <ReactFlowProvider>
      <CanvasInner />
    </ReactFlowProvider>
  );
}
