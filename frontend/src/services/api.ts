import type { IR, ProjectFile, SimulationConfig } from '@/types';

const BASE = '/api';

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((detail as { detail?: string }).detail || res.statusText);
  }
  return res.json() as T;
}

async function get<T>(url: string): Promise<T> {
  const res = await fetch(`${BASE}${url}`);
  if (!res.ok) throw new Error(res.statusText);
  return res.json() as T;
}

// === API ===

export interface HealthResponse {
  status: string;
  service: string;
}

export interface GenerateResponse {
  success: boolean;
  verilog: string;
}

export interface ParseVerilogResponse {
  success: boolean;
  modules: Array<{
    name: string;
    ports: Array<{ name: string; direction: string; width: number }>;
    instantiations: Array<Record<string, unknown>>;
  }>;
}

export interface ParseVCDResponse {
  success: boolean;
  waveform: {
    signals: Array<{
      name: string;
      width: number;
      signed: boolean;
      changes: Array<{ time_ns: number; value: string }>;
    }>;
    total_time_ns: number;
    timescale: string;
  };
}

export interface SaveProjectResponse {
  success: boolean;
  path: string;
}

export interface LoadProjectResponse {
  success: boolean;
  project: ProjectFile;
}

export interface SimulateResponse {
  success: boolean;
  stdout?: string;
  stderr?: string;
  errors?: string[];
  warnings?: string[];
  vcd_path?: string;
}

export const api = {
  health: () => get<HealthResponse>('/health'),

  generateTop: (ir: IR) =>
    post<GenerateResponse>('/generate/top', { ir }),

  generateTestbench: (ir: IR, simulation: SimulationConfig) =>
    post<GenerateResponse>('/generate/testbench', { ir, simulation }),

  parseVerilog: (filePath: string) =>
    post<ParseVerilogResponse>('/parse/verilog', { file_path: filePath }),

  parseVCD: (filePath: string) =>
    post<ParseVCDResponse>('/parse/vcd', { file_path: filePath }),

  saveProject: (project: ProjectFile, filePath: string) =>
    post<SaveProjectResponse>('/project/save', { project, file_path: filePath }),

  loadProject: (filePath: string) =>
    post<LoadProjectResponse>('/project/load', { file_path: filePath }),

  compile: (sources: string[], workDir: string) =>
    post<SimulateResponse>('/simulate/compile', { sources, work_dir: workDir }),

  runSimulation: (topModule: string, simTime: string, workDir: string, sources?: string[]) =>
    post<SimulateResponse>('/simulate/run', {
      top_module: topModule,
      sim_time: simTime,
      work_dir: workDir,
      sources,
    }),
};
