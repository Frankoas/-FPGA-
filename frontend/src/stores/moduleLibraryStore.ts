import { create } from 'zustand';
import type { ModuleTemplate } from '@/types';

const DEFAULT_TEMPLATES: ModuleTemplate[] = [
  // === 基础门电路 ===
  {
    name: 'and_gate',
    type: 'base',
    category: 'gate',
    ports: [
      { name: 'a', direction: 'input', width: 1, signed: false },
      { name: 'b', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'or_gate',
    type: 'base',
    category: 'gate',
    ports: [
      { name: 'a', direction: 'input', width: 1, signed: false },
      { name: 'b', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'not_gate',
    type: 'base',
    category: 'gate',
    ports: [
      { name: 'a', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'xor_gate',
    type: 'base',
    category: 'gate',
    ports: [
      { name: 'a', direction: 'input', width: 1, signed: false },
      { name: 'b', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'nand_gate',
    type: 'base',
    category: 'gate',
    ports: [
      { name: 'a', direction: 'input', width: 1, signed: false },
      { name: 'b', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'nor_gate',
    type: 'base',
    category: 'gate',
    ports: [
      { name: 'a', direction: 'input', width: 1, signed: false },
      { name: 'b', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },

  // === 组合逻辑 ===
  {
    name: 'mux_2to1',
    type: 'base',
    category: 'combinational',
    ports: [
      { name: 'a', direction: 'input', width: 8, signed: false },
      { name: 'b', direction: 'input', width: 8, signed: false },
      { name: 'sel', direction: 'input', width: 1, signed: false },
      { name: 'y', direction: 'output', width: 8, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'decoder_2to4',
    type: 'base',
    category: 'combinational',
    ports: [
      { name: 'in', direction: 'input', width: 2, signed: false },
      { name: 'en', direction: 'input', width: 1, signed: false },
      { name: 'out', direction: 'output', width: 4, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'encoder_4to2',
    type: 'base',
    category: 'combinational',
    ports: [
      { name: 'in', direction: 'input', width: 4, signed: false },
      { name: 'out', direction: 'output', width: 2, signed: false },
      { name: 'valid', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'adder_n',
    type: 'base',
    category: 'combinational',
    ports: [
      { name: 'a', direction: 'input', width: 8, signed: false },
      { name: 'b', direction: 'input', width: 8, signed: false },
      { name: 'cin', direction: 'input', width: 1, signed: false },
      { name: 'sum', direction: 'output', width: 8, signed: false },
      { name: 'cout', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },

  // === 时序逻辑 ===
  {
    name: 'd_flipflop',
    type: 'base',
    category: 'sequential',
    ports: [
      { name: 'clk', direction: 'input', width: 1, signed: false },
      { name: 'rst_n', direction: 'input', width: 1, signed: false },
      { name: 'd', direction: 'input', width: 1, signed: false },
      { name: 'q', direction: 'output', width: 1, signed: false },
      { name: 'q_n', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'register_n',
    type: 'base',
    category: 'sequential',
    ports: [
      { name: 'clk', direction: 'input', width: 1, signed: false },
      { name: 'rst_n', direction: 'input', width: 1, signed: false },
      { name: 'en', direction: 'input', width: 1, signed: false },
      { name: 'd', direction: 'input', width: 8, signed: false },
      { name: 'q', direction: 'output', width: 8, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'counter_n',
    type: 'base',
    category: 'sequential',
    ports: [
      { name: 'clk', direction: 'input', width: 1, signed: false },
      { name: 'rst_n', direction: 'input', width: 1, signed: false },
      { name: 'en', direction: 'input', width: 1, signed: false },
      { name: 'count', direction: 'output', width: 8, signed: false },
      { name: 'overflow', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'shift_reg',
    type: 'base',
    category: 'sequential',
    ports: [
      { name: 'clk', direction: 'input', width: 1, signed: false },
      { name: 'rst_n', direction: 'input', width: 1, signed: false },
      { name: 'si', direction: 'input', width: 1, signed: false },
      { name: 'dir', direction: 'input', width: 1, signed: false },
      { name: 'q', direction: 'output', width: 8, signed: false },
    ],
    defaultConfig: {},
  },

  // === IO 接口 ===
  {
    name: 'gpio_input',
    type: 'board_ip',
    category: 'io',
    ports: [
      { name: 'pin', direction: 'inout', width: 1, signed: false },
      { name: 'data_in', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'gpio_output',
    type: 'board_ip',
    category: 'io',
    ports: [
      { name: 'data_out', direction: 'input', width: 1, signed: false },
      { name: 'pin', direction: 'inout', width: 1, signed: false },
    ],
    defaultConfig: {},
  },
  {
    name: 'uart_tx',
    type: 'board_ip',
    category: 'io',
    ports: [
      { name: 'clk', direction: 'input', width: 1, signed: false },
      { name: 'rst_n', direction: 'input', width: 1, signed: false },
      { name: 'data', direction: 'input', width: 8, signed: false },
      { name: 'send', direction: 'input', width: 1, signed: false },
      { name: 'tx', direction: 'output', width: 1, signed: false },
      { name: 'busy', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: { baud_rate: 115200 },
  },
  {
    name: 'uart_rx',
    type: 'board_ip',
    category: 'io',
    ports: [
      { name: 'clk', direction: 'input', width: 1, signed: false },
      { name: 'rst_n', direction: 'input', width: 1, signed: false },
      { name: 'rx', direction: 'input', width: 1, signed: false },
      { name: 'data', direction: 'output', width: 8, signed: false },
      { name: 'valid', direction: 'output', width: 1, signed: false },
    ],
    defaultConfig: { baud_rate: 115200 },
  },
];

const CATEGORY_LABELS: Record<string, string> = {
  gate: '基本门电路',
  combinational: '组合逻辑',
  sequential: '时序逻辑',
  io: 'IO 接口',
};

interface ModuleLibraryState {
  templates: ModuleTemplate[];
  categories: Record<string, string>;
  searchQuery: string;
  activeCategory: string | null;

  setSearch: (q: string) => void;
  setCategory: (cat: string | null) => void;

  getFiltered: () => ModuleTemplate[];
  getTemplate: (name: string) => ModuleTemplate | undefined;
}

export const useModuleLibraryStore = create<ModuleLibraryState>((set, get) => ({
  templates: DEFAULT_TEMPLATES,
  categories: CATEGORY_LABELS,
  searchQuery: '',
  activeCategory: null,

  setSearch: (q) => set({ searchQuery: q }),
  setCategory: (cat) => set({ activeCategory: cat }),

  getFiltered: () => {
    const { templates, searchQuery, activeCategory } = get();
    let result = templates;
    if (activeCategory) {
      result = result.filter((t) => t.category === activeCategory);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      result = result.filter((t) => t.name.toLowerCase().includes(q));
    }
    return result;
  },

  getTemplate: (name) => get().templates.find((t) => t.name === name),
}));
