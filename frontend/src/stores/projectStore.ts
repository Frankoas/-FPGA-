import { create } from 'zustand';
import type { ProjectFile, IR, BoardConfig, SimulationConfig } from '@/types';
import { api } from '@/services/api';

interface ProjectState {
  name: string;
  path: string;
  ir: IR | null;
  board: BoardConfig | null;
  simulation: SimulationConfig | null;
  isDirty: boolean;

  setName: (name: string) => void;
  setIR: (ir: IR) => void;
  setDirty: (dirty: boolean) => void;

  saveProject: () => Promise<void>;
  loadProject: (path: string) => Promise<void>;
  newProject: () => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  name: 'untitled_design',
  path: '',
  ir: null,
  board: null,
  simulation: null,
  isDirty: false,

  setName: (name) => set({ name }),
  setIR: (ir) => set({ ir, isDirty: true }),
  setDirty: (dirty) => set({ isDirty: dirty }),

  saveProject: async () => {
    const { name, ir, board, simulation, path } = get();
    if (!ir) return;
    const project: ProjectFile = {
      version: '1.0',
      name,
      ir,
      board: board || undefined,
      simulation: simulation || undefined,
      canvas_state: { viewport: { x: 0, y: 0, zoom: 1 } },
    };
    const result = await api.saveProject(project, path || `${name}.fpga.json`);
    if (result.success) {
      set({ isDirty: false, path: result.path || path });
    }
  },

  loadProject: async (filePath) => {
    const result = await api.loadProject(filePath);
    if (result.success && result.project) {
      const p = result.project;
      set({
        name: p.name,
        path: filePath,
        ir: p.ir,
        board: p.board || null,
        simulation: p.simulation || null,
        isDirty: false,
      });
    }
  },

  newProject: () => {
    set({
      name: 'untitled_design',
      path: '',
      ir: null,
      board: null,
      simulation: null,
      isDirty: false,
    });
  },
}));
