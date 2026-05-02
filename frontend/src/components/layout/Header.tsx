import {
  Cpu, Save, Play, Code, Wand2,
} from 'lucide-react';
import { useCanvasStore } from '@/stores/canvasStore';
import { useUIStore } from '@/stores/uiStore';
import { useProjectStore } from '@/stores/projectStore';
import { useSimulationStore } from '@/stores/simulationStore';
import { api } from '@/services/api';
import { getLayoutedElements } from '@/utils/layout';

export function Header() {
  const { nodes, edges, setNodes, buildIR, clearCanvas } = useCanvasStore();
  const { setStatus, setGeneratedCode, setBottomPanelTab } = useUIStore();
  const { name: projectName, setIR, saveProject, newProject } = useProjectStore();

  const handleLayout = () => {
    const { nodes: layoutedNodes } = getLayoutedElements(nodes, edges);
    setNodes(layoutedNodes);
    setStatus('Auto layout applied');
  };

  const handleGenerate = async () => {
    const ir = buildIR(projectName);
    setIR(ir);
    setStatus('Generating Top module...');
    try {
      const result = await api.generateTop(ir);
      if (result.success) {
        setGeneratedCode(result.verilog);
        setBottomPanelTab('code');
        setStatus('Top module generated');
      }
    } catch (e) {
      setStatus(`Generate failed: ${(e as Error).message}`);
    }
  };

  const handleGenerateTB = async () => {
    const ir = buildIR(`${projectName}_tb`);
    setIR(ir);
    const sim = useSimulationStore.getState().config;
    setStatus('Generating Testbench...');
    try {
      const result = await api.generateTestbench(ir, sim);
      if (result.success) {
        setGeneratedCode(result.verilog);
        setBottomPanelTab('code');
        setStatus('Testbench generated');
      }
    } catch (e) {
      setStatus(`TB generate failed: ${(e as Error).message}`);
    }
  };

  const handleSave = async () => {
    const ir = buildIR(projectName);
    setIR(ir);
    setStatus('Saving project...');
    try {
      await saveProject();
      setStatus('Project saved');
    } catch (e) {
      setStatus(`Save failed: ${(e as Error).message}`);
    }
  };

  const handleNew = () => {
    clearCanvas();
    newProject();
    setStatus('New project');
  };

  const handleSimulate = async () => {
    setStatus('Simulation — configure sources first');
    setBottomPanelTab('log');
  };

  return (
    <header className="h-12 bg-primary text-white flex items-center justify-between px-4 shadow-md z-50 flex-shrink-0">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Cpu className="text-blue-300" size={24} />
          <h1 className="font-bold text-sm tracking-tight hidden sm:block">FPGA Visual Builder</h1>
        </div>
        <nav className="flex items-center gap-1 text-xs">
          <button className="px-3 py-1 hover:bg-white/10 rounded" onClick={handleNew}>File</button>
          <button className="px-3 py-1 hover:bg-white/10 rounded">Edit</button>
          <button className="px-3 py-1 hover:bg-white/10 rounded" onClick={handleGenerateTB}>Testbench</button>
        </nav>
      </div>

      <div className="flex items-center gap-2">
        <div className="flex bg-white/10 rounded-md p-0.5">
          <button className="p-1.5 hover:bg-white/15 rounded flex items-center gap-1.5" title="Save" onClick={handleSave}>
            <Save size={16} />
            <span className="text-[10px] hidden lg:block">SAVE</span>
          </button>
          <div className="w-px bg-white/20 mx-0.5" />
          <button className="p-1.5 hover:bg-white/15 rounded flex items-center gap-1.5 text-amber-300" title="Auto Layout" onClick={handleLayout}>
            <Wand2 size={16} />
            <span className="text-[10px] hidden lg:block">LAYOUT</span>
          </button>
          <div className="w-px bg-white/20 mx-0.5" />
          <button className="p-1.5 hover:bg-white/15 rounded flex items-center gap-1.5 text-blue-300" title="Generate Top" onClick={handleGenerate}>
            <Code size={16} />
            <span className="text-[10px] hidden lg:block">GENERATE</span>
          </button>
          <div className="w-px bg-white/20 mx-0.5" />
          <button className="p-1.5 hover:bg-white/15 rounded flex items-center gap-1.5 text-green-400" title="Simulate" onClick={handleSimulate}>
            <Play size={16} />
            <span className="text-[10px] hidden lg:block">SIMULATE</span>
          </button>
        </div>
      </div>
    </header>
  );
}
