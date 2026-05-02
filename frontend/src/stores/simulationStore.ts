import { create } from 'zustand';
import type { SimulationConfig, SimulationResult, WaveformData } from '@/types';
import { api } from '@/services/api';

interface SimulationState {
  config: SimulationConfig;
  isRunning: boolean;
  result: SimulationResult | null;
  waveform: WaveformData | null;

  setConfig: (config: Partial<SimulationConfig>) => void;
  compile: (sources: string[], workDir: string) => Promise<void>;
  run: (topModule: string, workDir: string, sources: string[]) => Promise<void>;
  loadWaveform: (vcdPath: string) => Promise<void>;
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  config: {
    simulator: 'modelsim',
    clock_period_ns: 10,
    reset_cycles: 5,
    sim_time_us: 100,
    monitored_signals: [],
  },
  isRunning: false,
  result: null,
  waveform: null,

  setConfig: (partial) => set((s) => ({ config: { ...s.config, ...partial } })),

  compile: async (sources, workDir) => {
    set({ isRunning: true, result: null });
    try {
      const r = await api.compile(sources, workDir);
      set({ result: { success: r.success, stdout: r.stdout || '', stderr: r.stderr || '', errors: r.errors || [], warnings: r.warnings || [], vcd_path: r.vcd_path }, isRunning: false });
    } catch (e) {
      set({ isRunning: false, result: { success: false, stdout: '', stderr: String(e), errors: [String(e)], warnings: [] } });
    }
  },

  run: async (topModule, workDir, sources) => {
    set({ isRunning: true, result: null });
    try {
      const simTime = `${get().config.sim_time_us}us`;
      const r = await api.runSimulation(topModule, simTime, workDir, sources);
      set({ result: { success: r.success, stdout: r.stdout || '', stderr: r.stderr || '', errors: r.errors || [], warnings: r.warnings || [], vcd_path: r.vcd_path }, isRunning: false });
    } catch (e) {
      set({ isRunning: false, result: { success: false, stdout: '', stderr: String(e), errors: [String(e)], warnings: [] } });
    }
  },

  loadWaveform: async (vcdPath) => {
    try {
      const r = await api.parseVCD(vcdPath);
      if (r.success) {
        set({ waveform: r.waveform });
      }
    } catch {
      // ignore
    }
  },
}));
