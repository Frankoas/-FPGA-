// === IR Data Types (aligned with backend Pydantic models) ===

export type PortDirection = 'input' | 'output' | 'inout';

export interface Port {
  id: string;
  name: string;
  direction: PortDirection;
  width: number;
  signed: boolean;
  array_size?: number | null;
  description?: string;
}

export type ModuleType = 'base' | 'wrapped' | 'board_ip';

export interface Module {
  id: string;
  name: string;
  instance_name?: string | null;
  type: ModuleType;
  ports: Port[];
  position: [number, number];
  config: Record<string, unknown>;
}

export interface Connection {
  id: string;
  src_module: string;
  src_port: string;
  dst_module: string;
  dst_port: string;
  wire_name?: string | null;
}

export interface WrappedModule {
  name: string;
  exposed_ports: Port[];
  internal_modules: Module[];
  internal_connections: Connection[];
  internal_wrapped: WrappedModule[];
}

export interface IR {
  version: string;
  modules: Module[];
  connections: Connection[];
  wrapped_modules: WrappedModule[];
  top_module_name: string;
}

export interface BoardConfig {
  board_name: string;
  fpga_part?: string;
  clock_pins: Record<string, string>;
  gpio_map: Record<string, string>;
  constraints?: string;
}

export interface SimulationConfig {
  simulator: string;
  clock_period_ns: number;
  reset_cycles: number;
  sim_time_us: number;
  monitored_signals: string[];
}

export interface ProjectFile {
  version: string;
  name: string;
  ir: IR;
  board?: BoardConfig | null;
  simulation?: SimulationConfig | null;
  canvas_state: Record<string, unknown>;
}

// === ReactFlow Node/Edge Data ===

export interface ModuleNodeData {
  module: Module;
}

export interface ConnectionEdgeData {
  connection: Connection;
  wireName: string;
}

// === Module Template (for library) ===

export interface ModuleTemplate {
  name: string;
  type: ModuleType;
  category: string;
  ports: Omit<Port, 'id'>[];
  defaultConfig: Record<string, unknown>;
}

// === Simulation ===

export interface ProbedSignal {
  moduleId: string;
  moduleName: string;
  portName: string;
  width: number;
}

export interface SignalChange {
  time_ns: number;
  value: string;
}

export interface SignalTrace {
  name: string;
  width: number;
  signed: boolean;
  changes: SignalChange[];
}

export interface WaveformData {
  signals: SignalTrace[];
  total_time_ns: number;
  timescale: string;
}

// === UI ===

export type Theme = 'light' | 'dark';
export type LeftPanelTab = 'library' | 'signals' | 'files';
export type BottomPanelTab = 'code' | 'log' | 'waveform';
