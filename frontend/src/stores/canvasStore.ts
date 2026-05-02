import { create } from 'zustand';
import {
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect,
  type Connection as RFConnection,
} from '@xyflow/react';
import type { Module, Connection, IR, ModuleNodeData, ConnectionEdgeData, Port } from '@/types';

interface CanvasState {
  nodes: Array<{ id: string; type: string; position: { x: number; y: number }; data: ModuleNodeData }>;
  edges: Array<{ id: string; source: string; target: string; sourceHandle: string; targetHandle: string; data: ConnectionEdgeData }>;
  selectedNodeId: string | null;
  selectedEdgeId: string | null;

  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;

  addModule: (module: Module, position?: { x: number; y: number }) => void;
  removeModule: (id: string) => void;
  updateModulePosition: (id: string, position: { x: number; y: number }) => void;
  updateModuleConfig: (id: string, config: Record<string, unknown>) => void;

  removeConnection: (id: string) => void;

  selectNode: (id: string | null) => void;
  selectEdge: (id: string | null) => void;

  buildIR: (topModuleName: string) => IR;

  loadCanvas: (ir: IR) => void;
  clearCanvas: () => void;
}

let nodeCounter = 0;
function genNodeId(): string {
  nodeCounter += 1;
  return `node_${nodeCounter}`;
}

let edgeCounter = 0;
function genEdgeId(): string {
  edgeCounter += 1;
  return `edge_${edgeCounter}`;
}

const NODE_TYPE_LAYOUT: Record<string, string> = {
  base: 'moduleNode',
  wrapped: 'moduleNode',
  board_ip: 'moduleNode',
};

export const useCanvasStore = create<CanvasState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,

  onNodesChange: (changes) => set({ nodes: applyNodeChanges(changes, get().nodes) }),
  onEdgesChange: (changes) => set({ edges: applyEdgeChanges(changes, get().edges) }),

  onConnect: (connection: RFConnection) => {
    const { nodes, edges } = get();
    const srcNode = nodes.find((n) => n.id === connection.source);
    const dstNode = nodes.find((n) => n.id === connection.target);
    if (!srcNode || !dstNode) return;

    const srcModule = srcNode.data.module;
    const dstModule = dstNode.data.module;
    const srcPort = srcModule.ports.find((p) => p.id === connection.sourceHandle);
    const dstPort = dstModule.ports.find((p) => p.id === connection.targetHandle);
    if (!srcPort || !dstPort) return;

    // Allow output→input or inout↔inout only
    if (srcPort.direction === 'input' && dstPort.direction !== 'output' && dstPort.direction !== 'inout') return;
    if (srcPort.direction === 'output' && dstPort.direction !== 'input' && dstPort.direction !== 'inout') return;

    // Prevent multi-drive on input ports
    const alreadyDriven = edges.some(
      (e) => e.target === connection.target && e.targetHandle === connection.targetHandle
    );
    if (alreadyDriven && dstPort.direction === 'input') return;

    // Prevent self-connection
    if (connection.source === connection.target) return;

    // Prevent duplicate connections
    const exists = edges.some(
      (e) =>
        e.source === connection.source &&
        e.target === connection.target &&
        e.sourceHandle === connection.sourceHandle &&
        e.targetHandle === connection.targetHandle
    );
    if (exists) return;

    const wireName = `${srcModule.instance_name || srcModule.name}_${srcPort.name}`;
    const connId = genEdgeId();
    const newEdge = {
      id: connId,
      source: connection.source,
      target: connection.target,
      sourceHandle: connection.sourceHandle!,
      targetHandle: connection.targetHandle!,
      type: 'smoothstep',
      animated: false,
      data: {
        connection: {
          id: connId,
          src_module: srcModule.id,
          src_port: srcPort.name,
          dst_module: dstModule.id,
          dst_port: dstPort.name,
          wire_name: wireName,
        },
        wireName,
      },
    };
    set({ edges: addEdge(newEdge, get().edges) });
  },

  addModule: (module, position) => {
    const node = {
      id: module.id,
      type: NODE_TYPE_LAYOUT[module.type] || 'moduleNode',
      position: position || module.position || { x: 0, y: 0 },
      data: { module },
    };
    set({ nodes: [...get().nodes, node] });
  },

  removeModule: (id) => {
    set({
      nodes: get().nodes.filter((n) => n.id !== id),
      edges: get().edges.filter((e) => e.source !== id && e.target !== id),
      selectedNodeId: get().selectedNodeId === id ? null : get().selectedNodeId,
    });
  },

  updateModulePosition: (id, position) => {
    set({
      nodes: get().nodes.map((n) =>
        n.id === id ? { ...n, position } : n
      ),
    });
  },

  updateModuleConfig: (id, config) => {
    set({
      nodes: get().nodes.map((n) =>
        n.id === id
          ? { ...n, data: { ...n.data, module: { ...n.data.module, config } } }
          : n
      ),
    });
  },

  removeConnection: (id) => {
    set({ edges: get().edges.filter((e) => e.id !== id) });
  },

  selectNode: (id) => set({ selectedNodeId: id, selectedEdgeId: null }),
  selectEdge: (id) => set({ selectedEdgeId: id, selectedNodeId: null }),

  buildIR: (topModuleName): IR => {
    const { nodes, edges } = get();
    const modules: Module[] = nodes.map((n) => n.data.module);
    const connections: Connection[] = edges.map((e) => e.data.connection);
    return {
      version: '1.0',
      top_module_name: topModuleName,
      modules,
      connections,
      wrapped_modules: [],
    };
  },

  loadCanvas: (ir) => {
    nodeCounter = 0;
    edgeCounter = 0;
    const nodes = ir.modules.map((m) => ({
      id: m.id,
      type: NODE_TYPE_LAYOUT[m.type] || 'moduleNode',
      position: { x: m.position[0], y: m.position[1] },
      data: { module: m },
    }));
    const edges = ir.connections.map((c) => ({
      id: c.id,
      source: c.src_module,
      target: c.dst_module,
      sourceHandle: c.src_port,
      targetHandle: c.dst_port,
      type: 'smoothstep',
      data: {
        connection: c,
        wireName: c.wire_name || `${c.src_module}_${c.src_port}`,
      },
    }));
    set({ nodes, edges, selectedNodeId: null, selectedEdgeId: null });
  },

  clearCanvas: () => set({ nodes: [], edges: [], selectedNodeId: null, selectedEdgeId: null }),
}));
