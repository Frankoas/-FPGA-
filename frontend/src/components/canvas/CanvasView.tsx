import { useCallback, useRef } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUIStore } from '@/stores/uiStore';
import ModuleNode from './nodes/ModuleNode';

const nodeTypes = { moduleNode: ModuleNode };

export default function CanvasView() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, selectNode, selectEdge, addModule } = useCanvasStore();
  const { screenToFlowPosition } = useReactFlow();
  const setStatus = useUIStore((s) => s.setStatus);
  const gridSnap = useUIStore((s) => s.gridSnap);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const onNodeClick = useCallback((_e: React.MouseEvent, node: Node) => {
    selectNode(node.id);
  }, [selectNode]);

  const onEdgeClick = useCallback((_e: React.MouseEvent, edge: Edge) => {
    selectEdge(edge.id);
  }, [selectEdge]);

  const onPaneClick = useCallback(() => {
    selectNode(null);
    selectEdge(null);
  }, [selectNode, selectEdge]);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const data = e.dataTransfer.getData('application/module-template');
    if (!data) return;

    try {
      const tmpl = JSON.parse(data);
      const id = `mod_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      const flowPos = screenToFlowPosition({ x: e.clientX, y: e.clientY });
      const module = {
        id,
        name: tmpl.name,
        instance_name: `${tmpl.name}_inst`,
        type: tmpl.type,
        ports: tmpl.ports.map((p: { name: string; direction: string; width: number; signed: boolean }, i: number) => ({
          ...p,
          id: `${tmpl.name}_port_${i}`,
        })),
        position: [Math.round(flowPos.x), Math.round(flowPos.y)],
        config: { ...tmpl.defaultConfig },
      };
      addModule(module);
      setStatus(`已放置模块: ${module.instance_name}`);
    } catch {
      // ignore invalid drop data
    }
  }, [addModule, setStatus, screenToFlowPosition]);

  return (
    <div ref={reactFlowWrapper} className="flex-1 h-full" onDragOver={onDragOver} onDrop={onDrop}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        nodesDraggable={true}
        nodesConnectable={true}
        elementsSelectable={true}
        snapToGrid={gridSnap}
        snapGrid={[20, 20]}
        fitView
        deleteKeyCode={['Delete', 'Backspace']}
        multiSelectionKeyCode="Shift"
        selectionKeyCode="Shift"
        panOnDrag={[1]}
        connectionLineStyle={{ stroke: 'var(--edge-default)', strokeWidth: 2 }}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
          style: { stroke: 'var(--edge-default)', strokeWidth: 2 },
        }}
      >
        <Background color="var(--border-primary)" gap={20} size={1} />
        <Controls />
        <MiniMap
          nodeColor={(n) => {
            const type = (n.data as { module?: { type: string } })?.module?.type;
            if (type === 'wrapped') return 'var(--node-wrapped)';
            if (type === 'board_ip') return 'var(--node-board)';
            return 'var(--node-base)';
          }}
          maskColor="rgba(0,0,0,0.4)"
        />
      </ReactFlow>
    </div>
  );
}
