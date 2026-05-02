import { useEffect } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { useUIStore } from '@/stores/uiStore';
import MenuBar from '@/components/layout/MenuBar';
import Toolbar from '@/components/layout/Toolbar';
import StatusBar from '@/components/layout/StatusBar';
import LeftPanel from '@/components/panels/LeftPanel';
import RightPanel from '@/components/panels/RightPanel';
import BottomPanel from '@/components/panels/BottomPanel';
import CanvasView from '@/components/canvas/CanvasView';

export default function App() {
  const theme = useUIStore((s) => s.theme);

  // Apply theme on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Keyboard shortcuts
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      const ctrl = e.ctrlKey || e.metaKey;

      // Ctrl+B: toggle left panel
      if (ctrl && e.key === 'b') {
        e.preventDefault();
        useUIStore.getState().toggleLeftPanel();
      }
      // Ctrl+J: toggle bottom panel
      if (ctrl && e.key === 'j') {
        e.preventDefault();
        useUIStore.getState().toggleBottomPanel();
      }
      // Ctrl+Shift+P: toggle right panel
      if (ctrl && e.shiftKey && e.key === 'P') {
        e.preventDefault();
        useUIStore.getState().toggleRightPanel();
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <MenuBar />
      <Toolbar />

      {/* Main area: LeftPanel + Canvas + RightPanel */}
      <div className="flex flex-1 overflow-hidden">
        <LeftPanel />
        <ReactFlowProvider>
          <CanvasView />
        </ReactFlowProvider>
        <RightPanel />
      </div>

      <BottomPanel />
      <StatusBar />
    </div>
  );
}
