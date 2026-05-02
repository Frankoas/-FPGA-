import { create } from 'zustand';
import type { SimulationConfig, WaveformData, ProbedSignal } from '@/types';
import { api } from '@/services/api';

interface SimulationState {
  config: SimulationConfig;
  isRunning: boolean;
  result: { stdout?: string; stderr?: string; errors?: string[]; warnings?: string[] } | null;
  waveform: WaveformData | null;
  probedSignals: ProbedSignal[];
  expandedSignals: Set<string>;

  setConfig: (c: Partial<SimulationConfig>) => void;
  setProbedSignals: (signals: ProbedSignal[]) => void;
  toggleExpandedSignal: (name: string) => void;

  runCompile: (sources: string[], workDir: string) => Promise<void>;
  runSimulation: (topModule: string, workDir: string) => Promise<void>;
  loadWaveform: (vcdPath: string) => Promise<void>;

  clearResult: () => void;
}

export const useSimulationStore = create<SimulationState>((set, get) => ({
  config: {
    simulator: 'iverilog',
    clock_period_ns: 10,
    reset_cycles: 5,
    sim_time_us: 100,
    monitored_signals: [],
  },
  isRunning: false,
  result: null,
  waveform: null,
  probedSignals: [],
  expandedSignals: new Set(),

  setConfig: (c) => set((s) => ({ config: { ...s.config, ...c } })),
  setProbedSignals: (signals) => set({ probedSignals: signals }),
  toggleExpandedSignal: (name) => set((s) => {
    const next = new Set(s.expandedSignals);
    if (next.has(name)) next.delete(name);
    else next.add(name);
    return { expandedSignals: next };
  }),

  runCompile: async (sources, workDir) => {
    set({ isRunning: true, result: null });
    try {
      const r = await api.compile(sources, workDir);
      set({ result: r, isRunning: false });
    } catch (e) {
      set({ result: { errors: [(e as Error).message] }, isRunning: false });
    }
  },

  runSimulation: async (topModule, workDir) => {
    set({ isRunning: true, result: null });
    try {
      const { config } = get();
      const simTime = `${config.sim_time_us}us`;
      const r = await api.runSimulation(topModule, simTime, workDir);
      set({ result: r, isRunning: false });
    } catch (e) {
      set({ result: { errors: [(e as Error).message] }, isRunning: false });
    }
  },

  loadWaveform: async (vcdPath) => {
    try {
      const r = await api.parseVCD(vcdPath);
      if (r.success) {
        set({ waveform: r.waveform });
      }
    } catch (e) {
      set({ result: { errors: [(e as Error).message] } });
    }
  },

  clearResult: () => set({ result: null }),
}));
