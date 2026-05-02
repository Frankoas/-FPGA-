import { create } from 'zustand';
import type { Theme, BottomPanelTab } from '@/types';

interface UIState {
  theme: Theme;
  setTheme: (t: Theme) => void;
  toggleTheme: () => void;

  bottomPanelOpen: boolean;
  rightPanelOpen: boolean;
  bottomPanelTab: BottomPanelTab;

  toggleBottomPanel: () => void;
  toggleRightPanel: () => void;
  setBottomPanelTab: (tab: BottomPanelTab) => void;

  gridSnap: boolean;
  toggleGridSnap: () => void;

  statusMessage: string;
  setStatus: (msg: string) => void;

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

  bottomPanelOpen: true,
  rightPanelOpen: true,
  bottomPanelTab: 'code',

  toggleBottomPanel: () => set((s) => ({ bottomPanelOpen: !s.bottomPanelOpen })),
  toggleRightPanel: () => set((s) => ({ rightPanelOpen: !s.rightPanelOpen })),
  setBottomPanelTab: (tab) => set({ bottomPanelTab: tab, bottomPanelOpen: true }),

  gridSnap: true,
  toggleGridSnap: () => set((s) => ({ gridSnap: !s.gridSnap })),

  statusMessage: 'Ready',
  setStatus: (msg) => set({ statusMessage: msg }),

  generatedCode: '',
  setGeneratedCode: (code) => set({ generatedCode: code }),
}));
