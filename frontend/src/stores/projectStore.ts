import { create } from 'zustand';
import type { ProjectFile, IR, BoardConfig, SimulationConfig } from '@/types';
import { api } from '@/services/api';

interface ProjectState {
  name: string;
  filePath: string | null;
  ir: IR | null;
  board: BoardConfig | null;
  simulation: SimulationConfig | null;
  canvasState: Record<string, unknown>;
  isDirty: boolean;
  lastSaved: string | null;

  setProjectName: (name: string) => void;
  setIR: (ir: IR) => void;
  setBoard: (board: BoardConfig) => void;
  setSimulation: (config: SimulationConfig) => void;
  setCanvasState: (state: Record<string, unknown>) => void;
  markDirty: () => void;

  newProject: () => void;
  saveProject: () => Promise<void>;
  loadProject: (filePath: string) => Promise<void>;

  getProjectFile: () => ProjectFile;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  name: '未命名项目',
  filePath: null,
  ir: null,
  board: null,
  simulation: {
    simulator: 'iverilog',
    clock_period_ns: 10,
    reset_cycles: 5,
    sim_time_us: 100,
    monitored_signals: [],
  },
  canvasState: {},
  isDirty: false,
  lastSaved: null,

  setProjectName: (name) => set({ name, isDirty: true }),
  setIR: (ir) => set({ ir, isDirty: true }),
  setBoard: (board) => set({ board, isDirty: true }),
  setSimulation: (config) => set({ simulation: config, isDirty: true }),
  setCanvasState: (state) => set({ canvasState: state, isDirty: true }),
  markDirty: () => set({ isDirty: true }),

  newProject: () => set({
    name: '未命名项目',
    filePath: null,
    ir: null,
    board: null,
    simulation: {
      simulator: 'iverilog',
      clock_period_ns: 10,
      reset_cycles: 5,
      sim_time_us: 100,
      monitored_signals: [],
    },
    canvasState: {},
    isDirty: false,
    lastSaved: null,
  }),

  saveProject: async () => {
    const { filePath, getProjectFile } = get();
    const project = getProjectFile();
    const result = await api.saveProject(project, filePath || 'untitled.fpga.json');
    if (result.success) {
      set({ filePath: result.path, isDirty: false, lastSaved: new Date().toISOString() });
    }
  },

  loadProject: async (filePath: string) => {
    const result = await api.loadProject(filePath);
    if (result.success) {
      const p = result.project;
      set({
        name: p.name,
        filePath,
        ir: p.ir,
        board: p.board || null,
        simulation: p.simulation || null,
        canvasState: p.canvas_state,
        isDirty: false,
        lastSaved: new Date().toISOString(),
      });
    }
  },

  getProjectFile: (): ProjectFile => {
    const { name, ir, board, simulation, canvasState } = get();
    return {
      version: '1.0',
      name,
      ir: ir!,
      board,
      simulation,
      canvas_state: canvasState,
    };
  },
}));
