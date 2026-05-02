import { useEffect } from 'react';
import { useUIStore } from '@/stores/uiStore';
import { Header } from '@/components/layout/Header';
import { StatusBar } from '@/components/layout/StatusBar';
import { ModuleLibrary } from '@/components/panels/ModuleLibrary';
import { PropertiesPanel } from '@/components/panels/PropertiesPanel';
import { BottomPanel } from '@/components/panels/BottomPanel';
import { Canvas } from '@/components/canvas/Canvas';

export default function App() {
  const theme = useUIStore((s) => s.theme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <div className="flex flex-col h-screen" style={{ background: 'var(--canvas-bg)', color: 'var(--text-primary)' }}>
      <Header />

      <main className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar */}
        <aside className="w-64 flex-shrink-0 z-40">
          <ModuleLibrary />
        </aside>

        {/* Center Area */}
        <div className="flex-1 flex flex-col relative overflow-hidden">
          <div className="flex-1">
            <Canvas />
          </div>
          <BottomPanel />
        </div>

        {/* Right Sidebar */}
        <PropertiesPanel />
      </main>

      <StatusBar />
    </div>
  );
}
