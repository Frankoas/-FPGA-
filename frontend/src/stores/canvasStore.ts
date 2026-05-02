import { create } from 'zustand';
import { applyNodeChanges, applyEdgeChanges, addEdge } from '@xyflow/react';
import type { Node, Edge, OnNodesChange, OnEdgesChange, OnConnect, Connection } from '@xyflow/react';
import type { ModuleData, ConnectionData, IR, PortData } from '@/types';

export interface ModuleNodeData extends Record<string, unknown> {
  module: ModuleData;
}

interface CanvasState {
  nodes: Node<ModuleNodeData>[];
  edges: Edge[];
  selectedNodeId: string | null;
  selectedEdgeId: string | null;

  setNodes: (nodes: Node<ModuleNodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;

  onNodesChange: OnNodesChange<Node<ModuleNodeData>>;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;

  addNode: (node: Node<ModuleNodeData>) => void;
  removeNode: (id: string) => void;
  updateNodeData: (id: string, data: Partial<ModuleData>) => void;

  selectNode: (id: string | null) => void;
  selectEdge: (id: string | null) => void;

  buildIR: (topModuleName: string) => IR;
  loadCanvas: (ir: IR) => void;
  clearCanvas: () => void;
}

export const useCanvasStore = create<CanvasState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: ((changes: Parameters<OnNodesChange>[0]) => {
    set({ nodes: applyNodeChanges(changes, get().nodes) as Node<ModuleNodeData>[] });
  }) as OnNodesChange<Node<ModuleNodeData>>,

  onEdgesChange: ((changes: Parameters<OnEdgesChange>[0]) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
  }) as OnEdgesChange,

  onConnect: (connection: Connection) => {
    const { nodes, edges } = get();
    const srcNode = nodes.find((n) => n.id === connection.source);
    const dstNode = nodes.find((n) => n.id === connection.target);
    if (!srcNode || !dstNode) return;

    const srcPorts = srcNode.data.module.ports as PortData[];
    const dstPorts = dstNode.data.module.ports as PortData[];
    const srcPort = srcPorts.find((p) => (p.id || p.name) === connection.sourceHandle);
    const dstPort = dstPorts.find((p) => (p.id || p.name) === connection.targetHandle);
    if (!srcPort || !dstPort) return;

    // Direction validation
    if (srcPort.direction === 'input' && dstPort.direction !== 'output' && dstPort.direction !== 'inout') return;
    if (srcPort.direction === 'output' && dstPort.direction !== 'input' && dstPort.direction !== 'inout') return;

    // Prevent multi-drive
    if (dstPort.direction === 'input') {
      const alreadyDriven = edges.some(
        (e) => e.target === connection.target && e.targetHandle === connection.targetHandle
      );
      if (alreadyDriven) return;
    }

    // Prevent self-connection
    if (connection.source === connection.target) return;

    // Prevent duplicate
    const exists = edges.some(
      (e) =>
        e.source === connection.source &&
        e.target === connection.target &&
        e.sourceHandle === connection.sourceHandle &&
        e.targetHandle === connection.targetHandle
    );
    if (exists) return;

    const wire_name = `${srcNode.data.module.instance_name || srcNode.data.module.name}_${srcPort.name}`;
    set({
      edges: addEdge(
        {
          ...connection,
          id: `edge_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
          type: 'smoothstep',
          animated: true,
          style: { stroke: '#1a56db', strokeWidth: 2 },
          data: {
            wire_name,
            connection: {
              id: `edge_${Date.now()}`,
              src_module: srcNode.data.module.id,
              src_port: srcPort.name,
              dst_module: dstNode.data.module.id,
              dst_port: dstPort.name,
              wire_name,
            } satisfies ConnectionData,
          },
        },
        get().edges
      ),
    });
  },

  addNode: (node) => set({ nodes: [...get().nodes, node] }),

  removeNode: (id) => {
    set({
      nodes: get().nodes.filter((n) => n.id !== id),
      edges: get().edges.filter((e) => e.source !== id && e.target !== id),
      selectedNodeId: get().selectedNodeId === id ? null : get().selectedNodeId,
    });
  },

  updateNodeData: (id, data) => {
    set({
      nodes: get().nodes.map((n) => {
        if (n.id === id) {
          return { ...n, data: { ...n.data, module: { ...n.data.module, ...data } } };
        }
        return n;
      }),
    });
  },

  selectNode: (id) => set({ selectedNodeId: id, selectedEdgeId: null }),
  selectEdge: (id) => set({ selectedEdgeId: id, selectedNodeId: null }),

  buildIR: (topModuleName): IR => {
    const { nodes, edges } = get();
    return {
      version: '1.0',
      top_module_name: topModuleName,
      modules: nodes.map((n) => n.data.module),
      connections: edges.map((e) => {
        const ed = (e.data || {}) as Record<string, unknown>;
        return (ed.connection as ConnectionData) || {
          id: e.id,
          src_module: e.source,
          src_port: e.sourceHandle || '',
          dst_module: e.target,
          dst_port: e.targetHandle || '',
          wire_name: ed.wire_name as string | undefined,
        };
      }),
      wrapped_modules: [],
    };
  },

  loadCanvas: (ir) => {
    const nodes: Node<ModuleNodeData>[] = ir.modules.map((m) => ({
      id: m.id,
      type: m.type,
      position: m.position ? { x: m.position[0], y: m.position[1] } : { x: 0, y: 0 },
      data: { module: m },
    }));
    const edges: Edge[] = ir.connections.map((c, i) => ({
      id: c.id || `edge_${i}`,
      source: c.src_module,
      target: c.dst_module,
      sourceHandle: c.src_port,
      targetHandle: c.dst_port,
      type: 'smoothstep',
      animated: true,
      style: { stroke: '#1a56db', strokeWidth: 2 },
      data: { wire_name: c.wire_name, connection: c },
    }));
    set({ nodes, edges, selectedNodeId: null, selectedEdgeId: null });
  },

  clearCanvas: () => set({ nodes: [], edges: [], selectedNodeId: null, selectedEdgeId: null }),
}));
