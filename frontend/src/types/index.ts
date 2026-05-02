/* ===== Port ===== */
export type PortDirection = 'input' | 'output' | 'inout';

export interface PortData {
  id?: string;
  name: string;
  direction: PortDirection;
  width: number;
  signed?: boolean;
}

/* ===== Module ===== */
export type ModuleType = 'base' | 'wrapped' | 'board_ip';

export interface ModuleData {
  id: string;
  name: string;
  instance_name?: string;
  type: ModuleType;
  ports: PortData[];
  position?: [number, number];
  config: Record<string, unknown>;
  [key: string]: unknown;
}

/* ===== Connection ===== */
export interface ConnectionData {
  id: string;
  src_module: string;
  src_port: string;
  dst_module: string;
  dst_port: string;
  wire_name?: string;
}

/* ===== Wrapped Module ===== */
export interface WrappedModuleData {
  name: string;
  internal_modules: ModuleData[];
  internal_connections: ConnectionData[];
  exposed_ports: string[];
}

/* ===== IR ===== */
export interface IR {
  version: string;
  modules: ModuleData[];
  connections: ConnectionData[];
  wrapped_modules: WrappedModuleData[];
  top_module_name: string;
}

/* ===== Project ===== */
export interface ProjectFile {
  version: string;
  name: string;
  ir: IR;
  board?: BoardConfig;
  simulation?: SimulationConfig;
  canvas_state: {
    viewport: { x: number; y: number; zoom: number };
  };
}

/* ===== Board ===== */
export interface BoardConfig {
  board_name: string;
  fpga_part: string;
  clock_pins: Record<string, string>;
  gpio_map: Record<string, string>;
  constraints: string;
}

/* ===== Simulation ===== */
export interface SimulationConfig {
  simulator: string;
  clock_period_ns: number;
  reset_cycles: number;
  sim_time_us: number;
  monitored_signals: string[];
}

export interface SimulationResult {
  success: boolean;
  stdout: string;
  stderr: string;
  errors: string[];
  warnings: string[];
  vcd_path?: string;
}

/* ===== Module Library ===== */
export interface ModuleTemplate {
  name: string;
  type: ModuleType;
  category: string;
  ports: PortData[];
  defaultConfig: Record<string, unknown>;
}

/* ===== Waveform ===== */
export interface SignalChange {
  time_ns: number;
  value: string;
}

export interface WaveformSignal {
  name: string;
  width: number;
  changes: SignalChange[];
}

export interface WaveformData {
  total_time_ns: number;
  timescale: string;
  signals: WaveformSignal[];
}

/* ===== UI ===== */
export type Theme = 'light' | 'dark';
export type LeftPanelTab = 'library' | 'signals' | 'files';
export type BottomPanelTab = 'code' | 'log' | 'waveform';
