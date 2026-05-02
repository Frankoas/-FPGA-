declare module 'dagre' {
  namespace dagre {
    class Graph {
      constructor();
      setGraph(opts: Record<string, unknown>): Graph;
      setDefaultEdgeLabel(cb: () => void): Graph;
      setNode(id: string, opts: Record<string, unknown>): Graph;
      setEdge(src: string, dst: string, opts?: Record<string, unknown>): Graph;
      node(id: string): { x: number; y: number; [key: string]: unknown };
    }
    namespace graphlib {
      export { Graph };
    }
    function layout(graph: Graph): void;
  }
  export = dagre;
}
