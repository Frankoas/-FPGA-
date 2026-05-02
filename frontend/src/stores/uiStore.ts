import { create } from 'zustand';
import type { Theme, LeftPanelTab, BottomPanelTab } from '@/types';

interface UIState {
  // theme
  theme: Theme;
  setTheme: (t: Theme) => void;
  toggleTheme: () => void;

  // panels
  leftPanelOpen: boolean;
  rightPanelOpen: boolean;
  bottomPanelOpen: boolean;
  leftPanelTab: LeftPanelTab;
  bottomPanelTab: BottomPanelTab;

  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;
  toggleBottomPanel: () => void;
  setLeftPanelTab: (tab: LeftPanelTab) => void;
  setBottomPanelTab: (tab: BottomPanelTab) => void;

  // grid
  gridSnap: boolean;
  toggleGridSnap: () => void;

  // status
  statusMessage: string;
  setStatus: (msg: string) => void;

  // dialog
  activeDialog: string | null;
  showDialog: (name: string) => void;
  hideDialog: () => void;

  // generated code
  generatedCode: string;
  setGeneratedCode: (code: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  theme: (localStorage.getItem('fpga-theme') as Theme) || 'dark',
  setTheme: (t) => {
    localStorage.setItem('fpga-theme', t);
    document.documentElement.setAttribute('data-theme', t);
    set({ theme: t });
  },
  toggleTheme: () => {
    set((s) => {
      const next = s.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('fpga-theme', next);
      document.documentElement.setAttribute('data-theme', next);
      return { theme: next };
    });
  },

  leftPanelOpen: true,
  rightPanelOpen: false,
  bottomPanelOpen: true,
  leftPanelTab: 'library',
  bottomPanelTab: 'code',

  toggleLeftPanel: () => set((s) => ({ leftPanelOpen: !s.leftPanelOpen })),
  toggleRightPanel: () => set((s) => ({ rightPanelOpen: !s.rightPanelOpen })),
  toggleBottomPanel: () => set((s) => ({ bottomPanelOpen: !s.bottomPanelOpen })),
  setLeftPanelTab: (tab) => set({ leftPanelTab: tab, leftPanelOpen: true }),
  setBottomPanelTab: (tab) => set({ bottomPanelTab: tab, bottomPanelOpen: true }),

  gridSnap: true,
  toggleGridSnap: () => set((s) => ({ gridSnap: !s.gridSnap })),

  statusMessage: '就绪',
  setStatus: (msg) => set({ statusMessage: msg }),

  activeDialog: null,
  showDialog: (name) => set({ activeDialog: name }),
  hideDialog: () => set({ activeDialog: null }),

  generatedCode: '',
  setGeneratedCode: (code) => set({ generatedCode: code }),
}));
